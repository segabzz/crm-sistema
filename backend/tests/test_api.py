import io
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.nlp_service import (
    NLPResultItem,
    NLPEstablishmentItem,
    NLPAnalysisResult,
    NLPServiceError,
)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_root_endpoint(client):
    """Verifica endpoint de salud raíz."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "CRM" in data["service"]

def test_get_dishes(client):
    """Verifica que el catálogo oficial cargue platillos activos."""
    response = client.get("/api/v1/dishes")
    assert response.status_code == 200
    dishes = response.json()
    assert len(dishes) >= 3
    nombres = [d["nombre"] for d in dishes]
    assert "Sopa Azteca" in nombres
    assert "Ribeye a la Parrilla" in nombres

def test_create_text_review_success(client):
    """Verifica ingesta de texto con NLP exitoso simulado."""
    mock_nlp_result = [
        NLPResultItem(
            texto_mencionado="la sopa azteca",
            platillo_final="Sopa Azteca",
            platillo_original_llm="Sopa Azteca",
            polaridad="positivo",
            score_numerico=1.0,
            atributos=[{"categoria": "temperatura", "valor": "caliente", "polaridad": "positivo"}],
            fue_reasignado_por_guardrail=False
        )
    ]
    with patch("app.api.v1.endpoints.reviews.nlp_service.analyze_review", return_value=mock_nlp_result):
        payload = {
            "texto": "la sopa azteca estaba caliente y rica",
            "canal_origen": "GOOGLE_MAPS",
            "calificacion_general": 5,
            "autor_nombre": "Carlos M."
        }
        response = client.post("/api/v1/reviews/text", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["autor_nombre"] == "Carlos M."
        assert data["estado_analisis"] == "COMPLETADO"
        assert len(data["sentimientos"]) == 1
        assert data["sentimientos"][0]["platillo_nombre_referenciado"] == "Sopa Azteca"
        assert data["sentimientos"][0]["polaridad"] == "positivo"

def test_create_text_review_nlp_failure_handled(client):
    """Verifica resiliencia cuando Ollama/LLM falla: persiste con estado_analisis='FALLIDO_NLP'."""
    with patch("app.api.v1.endpoints.reviews.nlp_service.analyze_review", side_effect=NLPServiceError("Ollama desconectado")):
        payload = {
            "texto": "excelente atención y servicio en mesa",
            "canal_origen": "FORMULARIO_WEB",
            "calificacion_general": 4,
            "autor_nombre": "Invitado"
        }
        response = client.post("/api/v1/reviews/text", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["estado_analisis"] == "FALLIDO_NLP"
        assert len(data["sentimientos"]) == 0

def test_create_text_review_validation_errors(client):
    """Verifica validación de Pydantic ante texto corto o calificación fuera de rango."""
    # Texto muy corto (< 3 chars)
    res1 = client.post("/api/v1/reviews/text", json={"texto": "ok"})
    assert res1.status_code == 422

    # Calificación fuera de rango
    res2 = client.post("/api/v1/reviews/text", json={"texto": "buena comida", "calificacion_general": 6})
    assert res2.status_code == 422

def test_get_review_detail_and_not_found(client):
    """Verifica consulta de reseña por ID y manejo de 404."""
    # 404 para ID inexistente
    res_404 = client.get("/api/v1/reviews/id-que-no-existe-12345")
    assert res_404.status_code == 404

    # Crear una para luego consultar
    with patch("app.api.v1.endpoints.reviews.nlp_service.analyze_review", return_value=[]):
        res_create = client.post("/api/v1/reviews/text", json={"texto": "comentario para test"})
        created_id = res_create.json()["id"]

    res_get = client.get(f"/api/v1/reviews/{created_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == created_id

def test_create_audio_review_silent_failure(client):
    """Verifica que un audio silencioso resulte en FALLIDO y OMITIDO_AUDIO_FALLIDO con 201."""
    mock_stt_result = {
        "texto_transcrito": "",
        "duracion_segundos": 1.0,
        "idioma_detectado": "es",
        "confianza": 0.0,
        "estado_procesamiento": "FALLIDO",
        "error": "No se detectó contenido de voz en el archivo de audio."
    }
    with patch("app.api.v1.endpoints.reviews.stt_service.transcribe", return_value=mock_stt_result):
        fake_audio = io.BytesIO(b"RIFF....WAVEfmt ....data....")
        response = client.post(
            "/api/v1/reviews/upload-audio",
            files={"file": ("silencio.wav", fake_audio, "audio/wav")},
            data={"canal_origen": "AUDIO_IN_SITU", "autor_nombre": "Silencioso"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["tipo_input"] == "AUDIO"
        assert data["transcripcion"]["estado_procesamiento"] == "FALLIDO"
        assert data["estado_analisis"] == "OMITIDO_AUDIO_FALLIDO"
        assert len(data["sentimientos"]) == 0

def test_analytics_ranking_and_trends(client):
    """Verifica endpoints de ranking y tendencias."""
    res_rank = client.get("/api/v1/analytics/ranking")
    assert res_rank.status_code == 200
    rank_data = res_rank.json()
    assert "top_platillos" in rank_data
    assert "platillos_en_riesgo" in rank_data
    assert "total_evaluaciones" in rank_data

    res_trends = client.get("/api/v1/analytics/trends?dias=7")
    assert res_trends.status_code == 200
    trends_data = res_trends.json()
    assert "tendencias_por_platillo" in trends_data
    assert "atributos_mas_mencionados_global" in trends_data
    assert "sentimientos_establecimiento" in trends_data

def test_create_and_get_order_by_qr_token(client):
    """Verifica creación de pedido (Mesero) y consulta por qr_token."""
    dishes = client.get("/api/v1/dishes").json()
    sopa = next(d for d in dishes if d["nombre"] == "Sopa Azteca")
    ribeye = next(d for d in dishes if d["nombre"] == "Ribeye a la Parrilla")

    order_payload = {
        "mesa": "Mesa 4",
        "items": [
            {"platillo_id": sopa["id"], "cantidad": 2},
            {"platillo_id": ribeye["id"], "cantidad": 1}
        ]
    }
    res_order = client.post("/api/v1/orders", json=order_payload)
    assert res_order.status_code == 201
    order_data = res_order.json()
    assert order_data["mesa"] == "Mesa 4"
    assert order_data["qr_token"].startswith("ord-")
    assert order_data["estado"] == "CREADO"
    expected_total = round(2 * sopa["precio"] + 1 * ribeye["precio"], 2)
    assert order_data["total"] == expected_total
    assert len(order_data["items"]) == 2

    # Consulta por qr_token válido
    qr_token = order_data["qr_token"]
    res_by_token = client.get(f"/api/v1/orders/by-token/{qr_token}")
    assert res_by_token.status_code == 200
    assert res_by_token.json()["id"] == order_data["id"]

    # Consulta por qr_token inexistente -> 404
    res_404 = client.get("/api/v1/orders/by-token/ord-inexistente-999")
    assert res_404.status_code == 404

def test_qr_linked_reviews_soft_badge_and_multiple_diners(client):
    """
    Verifica:
    1. Cruce determinista (Soft Verification Badge): [Verificado en Pedido] vs [Aviso: No figuraba en el pedido].
    2. Ajuste 1: Si platillo_final == 'Sin Clasificar', NO se aplica ningún badge del pedido.
    3. Confirmación de producto: Dos comensales escaneando el mismo QR pueden enviar reseñas sin bloqueo.
    """
    dishes = client.get("/api/v1/dishes").json()
    sopa = next(d for d in dishes if d["nombre"] == "Sopa Azteca")

    # Crear pedido únicamente con Sopa Azteca
    res_order = client.post("/api/v1/orders", json={
        "mesa": "Mesa 7",
        "items": [{"platillo_id": sopa["id"], "cantidad": 1}]
    })
    assert res_order.status_code == 201
    order_data = res_order.json()
    qr_token = order_data["qr_token"]

    # Comensal 1 menciona Sopa Azteca (en pedido), Ribeye a la Parrilla (NO en pedido) y un Sin Clasificar
    mock_diner_1 = NLPAnalysisResult(
        platillos=[
            NLPResultItem(
                texto_mencionado="la sopa azteca",
                platillo_final="Sopa Azteca",
                platillo_original_llm="Sopa Azteca",
                polaridad="positivo",
                score_numerico=1.0,
                atributos=[],
                fue_reasignado_por_guardrail=False
            ),
            NLPResultItem(
                texto_mencionado="el ribeye",
                platillo_final="Ribeye a la Parrilla",
                platillo_original_llm="Ribeye a la Parrilla",
                polaridad="positivo",
                score_numerico=1.0,
                atributos=[],
                fue_reasignado_por_guardrail=False
            ),
            NLPResultItem(
                texto_mencionado="la pizza",
                platillo_final="Sin Clasificar",
                platillo_original_llm="Sin Clasificar",
                polaridad="neutral",
                score_numerico=0.0,
                atributos=[],
                fue_reasignado_por_guardrail=False
            )
        ],
        establecimiento=[]
    )

    with patch("app.api.v1.endpoints.reviews.nlp_service.analyze_review", return_value=mock_diner_1):
        res_rev1 = client.post("/api/v1/reviews/text", json={
            "texto": "La sopa azteca muy buena, el ribeye rico y la pizza normal",
            "autor_nombre": "Comensal 1",
            "qr_token": qr_token
        })
        assert res_rev1.status_code == 201
        rev1_data = res_rev1.json()
        assert rev1_data["pedido_id"] == order_data["id"]

        sents = {s["platillo_nombre_referenciado"]: s for s in rev1_data["sentimientos"]}
        assert sents["Sopa Azteca"]["justificacion"] == "[Verificado en Pedido]"
        assert sents["Ribeye a la Parrilla"]["justificacion"] == "[Aviso: No figuraba en el pedido]"
        # Ajuste 1: Sin Clasificar NO lleva ningún badge de pedido
        assert sents["Sin Clasificar"]["justificacion"] is None

    # Comensal 2 escanea el MISMO QR (el pedido ya está en estado EVALUADO) y envía su propia reseña
    mock_diner_2 = NLPAnalysisResult(
        platillos=[
            NLPResultItem(
                texto_mencionado="la sopa azteca",
                platillo_final="Sopa Azteca",
                platillo_original_llm="Sopa Azteca",
                polaridad="positivo",
                score_numerico=1.0,
                atributos=[],
                fue_reasignado_por_guardrail=False
            )
        ],
        establecimiento=[]
    )

    with patch("app.api.v1.endpoints.reviews.nlp_service.analyze_review", return_value=mock_diner_2):
        res_rev2 = client.post("/api/v1/reviews/text", json={
            "texto": "A mí también me encantó la sopa azteca",
            "autor_nombre": "Comensal 2",
            "qr_token": qr_token
        })
        assert res_rev2.status_code == 201
        rev2_data = res_rev2.json()
        assert rev2_data["pedido_id"] == order_data["id"]

    # Verificar que el pedido registra ambas reseñas (total_resenas == 2) y estado == EVALUADO
    res_order_after = client.get(f"/api/v1/orders/by-token/{qr_token}")
    assert res_order_after.status_code == 200
    after_data = res_order_after.json()
    assert after_data["estado"] == "EVALUADO"
    assert after_data["total_resenas"] == 2

def test_establishment_sentiments_and_trends_reporting(client):
    """Verifica persistencia de SentimientoEstablecimiento y reporte separado en /analytics/trends."""
    mock_est_only = NLPAnalysisResult(
        platillos=[],
        establecimiento=[
            NLPEstablishmentItem(
                categoria="servicio",
                texto_mencionado="el servicio fue excelente",
                polaridad="positivo",
                score_numerico=1.0,
                valor_mencionado="servicio excelente"
            ),
            NLPEstablishmentItem(
                categoria="limpieza",
                texto_mencionado="muy limpio el lugar",
                polaridad="positivo",
                score_numerico=1.0,
                valor_mencionado="lugar muy limpio"
            )
        ]
    )
    with patch("app.api.v1.endpoints.reviews.nlp_service.analyze_review", return_value=mock_est_only):
        res = client.post("/api/v1/reviews/text", json={
            "texto": "El servicio fue excelente, muy limpio el lugar",
            "autor_nombre": "Laura G."
        })
        assert res.status_code == 201
        data = res.json()
        assert len(data["sentimientos"]) == 0
        assert len(data["sentimientos_establecimiento"]) == 2
        categorias = {e["categoria"] for e in data["sentimientos_establecimiento"]}
        assert categorias == {"servicio", "limpieza"}

    res_trends = client.get("/api/v1/analytics/trends?dias=7")
    assert res_trends.status_code == 200
    est_trends = res_trends.json()["sentimientos_establecimiento"]
    assert est_trends["total_menciones"] >= 2
    assert est_trends["positivas"] >= 2
    cats_reported = {c["categoria_atributo"] for c in est_trends["categorias"]}
    assert "servicio" in cats_reported
    assert "limpieza" in cats_reported

def test_admin_reset_database(client):
    """Verifica que el reset limpie reseñas y mantenga catálogo intacto."""
    response = client.post("/api/v1/admin/reset-database")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verificar que el catálogo sigue existiendo
    res_dishes = client.get("/api/v1/dishes")
    assert len(res_dishes.json()) >= 7
