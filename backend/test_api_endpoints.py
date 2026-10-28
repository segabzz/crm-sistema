"""
Script de pruebas end-to-end de los endpoints del backend utilizando TestClient.
Ejecuta solicitudes reales sobre:
- GET /api/v1/dishes
- POST /api/v1/reviews/text (Caso 1: Normal)
- POST /api/v1/reviews/text (Caso 2: Guardrail exclusión)
- POST /api/v1/reviews/upload-audio (Audio wav -> STT -> NLP -> SQLite)
- GET /api/v1/reviews/{id}
"""

import sys
import os
import json

# Agregar ruta backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_all():
    print("=" * 80)
    print("INICIANDO PRUEBAS END-TO-END DE ENDPOINTS DEL BACKEND")
    print("=" * 80)

    # 1. Probar GET /api/v1/dishes
    print("\n[TEST 1] GET /api/v1/dishes")
    res_dishes = client.get("/api/v1/dishes")
    print(f"Status Code: {res_dishes.status_code}")
    dishes = res_dishes.json()
    print(f"Platillos en catálogo recuperados: {len(dishes)}")
    for d in dishes:
        print(f" - {d['nombre']} (${d['precio']}) [{d['categoria']}]")
    assert res_dishes.status_code == 200
    assert len(dishes) >= 3

    # 2. Probar POST /api/v1/reviews/text (Caso 1: Contraste de platillos)
    print("\n" + "=" * 80)
    print("[TEST 2] POST /api/v1/reviews/text (Caso Contraste)")
    payload_1 = {
        "texto": "la sopa azteca estaba fría pero el ribeye a la parrilla quedó exquisito",
        "canal_origen": "GOOGLE_MAPS",
        "calificacion_general": 4,
        "autor_nombre": "Mariana Rivas"
    }
    res_text_1 = client.post("/api/v1/reviews/text", json=payload_1)
    print(f"Status Code: {res_text_1.status_code}")
    review_1 = res_text_1.json()
    print("Respuesta JSON:\n", json.dumps(review_1, indent=2, ensure_ascii=False))
    assert res_text_1.status_code == 201
    assert len(review_1["sentimientos"]) >= 2
    id_1 = review_1["id"]

    # 3. Probar POST /api/v1/reviews/text (Caso 2: Activación de Guardrail)
    print("\n" + "=" * 80)
    print("[TEST 3] POST /api/v1/reviews/text (Caso Guardrail Negación/Duda)")
    payload_2 = {
        "texto": "pedí dos tacos que no venían en el menú de especiales y además estaban fríos",
        "canal_origen": "WHATSAPP",
        "calificacion_general": 2,
        "autor_nombre": "Roberto Solís"
    }
    res_text_2 = client.post("/api/v1/reviews/text", json=payload_2)
    print(f"Status Code: {res_text_2.status_code}")
    review_2 = res_text_2.json()
    print("Respuesta JSON:\n", json.dumps(review_2, indent=2, ensure_ascii=False))
    assert res_text_2.status_code == 201
    id_2 = review_2["id"]

    # 4. Probar POST /api/v1/reviews/upload-audio (Audio a transcripción -> NLP -> DB)
    print("\n" + "=" * 80)
    print("[TEST 4] POST /api/v1/reviews/upload-audio (Faster-Whisper STT -> NLP)")
    audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage", "audios", "test_speech.wav")
    assert os.path.exists(audio_path), f"El archivo {audio_path} debe existir."

    with open(audio_path, "rb") as f:
        res_audio = client.post(
            "/api/v1/reviews/upload-audio",
            data={
                "canal_origen": "AUDIO_IN_SITU",
                "calificacion_general": 5,
                "autor_nombre": "Comensal Mesa 4"
            },
            files={"file": ("test_speech.wav", f, "audio/wav")}
        )

    print(f"Status Code: {res_audio.status_code}")
    review_audio = res_audio.json()
    print("Respuesta JSON (Audio):\n", json.dumps(review_audio, indent=2, ensure_ascii=False))
    assert res_audio.status_code == 201
    assert review_audio["transcripcion"] is not None
    assert review_audio["tipo_input"] == "AUDIO"
    id_audio = review_audio["id"]

    # 5. Probar GET /api/v1/reviews/{id}
    print("\n" + "=" * 80)
    print(f"[TEST 5] GET /api/v1/reviews/{id_1} (Consultar detalle persistido)")
    res_get = client.get(f"/api/v1/reviews/{id_1}")
    print(f"Status Code: {res_get.status_code}")
    review_get = res_get.json()
    print("Respuesta GET:\n", json.dumps(review_get, indent=2, ensure_ascii=False))
    assert res_get.status_code == 200
    assert review_get["id"] == id_1

    print("\n" + "=" * 80)
    print("TODAS LAS PRUEBAS DE ENDPOINTS COMPLETADAS EXITOSAMENTE!")
    print("=" * 80)

if __name__ == "__main__":
    test_all()
