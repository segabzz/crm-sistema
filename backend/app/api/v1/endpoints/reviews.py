import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.core.config import settings
from app.core.database import get_db
from app.models.dish import Platillo
from app.models.order import Pedido, ItemPedido
from app.models.review import Resena
from app.models.audio_transcription import TranscripcionAudio
from app.models.sentiment import SentimientoPlatillo
from app.models.attribute import AtributoMencionado
from app.models.establishment_sentiment import SentimientoEstablecimiento
from app.schemas.review import ReviewCreateText, ReviewDetailResponse
from app.services.nlp_service import nlp_service, NLPServiceError
from app.services.stt_service import stt_service

router = APIRouter()

def _procesar_y_persistir_resena(
    db: Session,
    texto_resena: str,
    canal_origen: str,
    tipo_input: str,
    calificacion_general: Optional[int],
    autor_nombre: Optional[str],
    datos_transcripcion: Optional[dict] = None,
    qr_token: Optional[str] = None
) -> Resena:
    """Función auxiliar que orquesta NLP, guardrails, cruce con pedido QR y persistencia relacional completa."""
    # 1. Obtener catálogo oficial activo de la base de datos
    platillos_db = db.query(Platillo).filter(Platillo.activo == True).all()
    catalogo_nombres = [p.nombre for p in platillos_db]
    mapa_platillos = {p.nombre: p for p in platillos_db}

    # 1.b Resolver pedido vinculado si se proporcionó qr_token
    # Confirmación de producto: múltiples comensales de la misma mesa pueden escanear el mismo QR.
    # El estado 'EVALUADO' es meramente informativo y NUNCA bloquea una segunda o subsiguiente reseña.
    pedido_vinculado: Optional[Pedido] = None
    platillos_ids_en_pedido: set[str] = set()
    if qr_token:
        pedido_vinculado = db.query(Pedido).options(
            joinedload(Pedido.items)
        ).filter(Pedido.qr_token == qr_token).first()
        if pedido_vinculado:
            platillos_ids_en_pedido = {it.platillo_id for it in pedido_vinculado.items}
            pedido_vinculado.estado = "EVALUADO"

    # 2. Análisis NLP con guardrails (se omite si el procesamiento de audio falló por silencio)
    items_nlp = []
    items_establecimiento = []
    estado_analisis = "COMPLETADO"
    if not (datos_transcripcion and datos_transcripcion.get("estado_procesamiento") == "FALLIDO"):
        try:
            nlp_result = nlp_service.analyze_review(texto_resena, catalogo_nombres)
            items_nlp = getattr(nlp_result, "platillos", nlp_result)
            items_establecimiento = getattr(nlp_result, "establecimiento", [])
        except NLPServiceError as e:
            print(f"[_procesar_y_persistir_resena WARNING] Falló extracción NLP ({e}). Se guardará con estado_analisis='FALLIDO_NLP'")
            estado_analisis = "FALLIDO_NLP"
            items_nlp = []
            items_establecimiento = []
    elif datos_transcripcion and datos_transcripcion.get("estado_procesamiento") == "FALLIDO":
        estado_analisis = "OMITIDO_AUDIO_FALLIDO"

    # 3. Crear entidad Resena
    nueva_resena = Resena(
        canal_origen=canal_origen,
        tipo_input=tipo_input,
        calificacion_general=calificacion_general,
        autor_nombre=autor_nombre or "Anónimo",
        texto_original=texto_resena,
        estado_analisis=estado_analisis,
        pedido_id=pedido_vinculado.id if pedido_vinculado else None
    )
    db.add(nueva_resena)
    db.flush()  # Generar id de reseña

    # 4. Si proviene de audio, persistir transcripción
    if datos_transcripcion:
        transcripcion = TranscripcionAudio(
            resena_id=nueva_resena.id,
            audio_path=datos_transcripcion.get("audio_path", ""),
            duracion_segundos=datos_transcripcion.get("duracion_segundos"),
            texto_transcrito=datos_transcripcion.get("texto_transcrito", ""),
            confianza=datos_transcripcion.get("confianza"),
            idioma_detectado=datos_transcripcion.get("idioma_detectado", "es"),
            estado_procesamiento=datos_transcripcion.get("estado_procesamiento", "TRANSCRITO")
        )
        db.add(transcripcion)

    # 5. Persistir Sentimientos de Platillos y Atributos asociados (+ Soft Verification Badge si hay pedido)
    for item in items_nlp:
        platillo_obj = mapa_platillos.get(item.platillo_final)
        platillo_id = platillo_obj.id if platillo_obj else None

        justificacion = None
        if item.fue_reasignado_por_guardrail:
            justificacion = f"[Guardrail] {item.motivo_guardrail}"

        # Opción B (Soft Verification Badge) + Ajuste 1:
        # Si platillo_final == "Sin Clasificar", NO aplicar ningún badge del pedido.
        if pedido_vinculado and item.platillo_final != "Sin Clasificar":
            if platillo_id and platillo_id in platillos_ids_en_pedido:
                badge = "[Verificado en Pedido]"
            else:
                badge = "[Aviso: No figuraba en el pedido]"
            justificacion = f"{justificacion} | {badge}" if justificacion else badge

        sentimiento = SentimientoPlatillo(
            resena_id=nueva_resena.id,
            platillo_id=platillo_id,
            platillo_nombre_referenciado=item.platillo_final,
            polaridad=item.polaridad,
            score_numerico=item.score_numerico,
            fragmento_texto=item.texto_mencionado,
            justificacion=justificacion
        )
        db.add(sentimiento)
        db.flush()

        for attr in item.atributos:
            atributo_obj = AtributoMencionado(
                sentimiento_platillo_id=sentimiento.id,
                categoria_atributo=attr["categoria"],
                valor_mencionado=attr["valor"],
                polaridad=attr["polaridad"]
            )
            db.add(atributo_obj)

    # 6. Persistir Sentimientos del Establecimiento (servicio, ambiente, limpieza, tiempo_espera)
    for est_item in items_establecimiento:
        sentimiento_est = SentimientoEstablecimiento(
            resena_id=nueva_resena.id,
            categoria=est_item.categoria,
            polaridad=est_item.polaridad,
            score_numerico=est_item.score_numerico,
            fragmento_texto=est_item.texto_mencionado,
            valor_mencionado=est_item.valor_mencionado
        )
        db.add(sentimiento_est)

    db.commit()

    # Recargar con relaciones completas
    resena_completa = db.query(Resena).options(
        joinedload(Resena.transcripcion),
        joinedload(Resena.sentimientos).joinedload(SentimientoPlatillo.atributos),
        joinedload(Resena.sentimientos_establecimiento)
    ).filter(Resena.id == nueva_resena.id).first()

    return resena_completa

@router.post("/text", response_model=ReviewDetailResponse, status_code=status.HTTP_201_CREATED, summary="Ingestar reseña de texto")
def create_text_review(
    payload: ReviewCreateText,
    db: Session = Depends(get_db)
):
    """
    Ingesta una reseña en formato texto, ejecuta el análisis de sentimientos
    de platillos y establecimiento mediante LLM + guardrails, y persiste todo.
    """
    return _procesar_y_persistir_resena(
        db=db,
        texto_resena=payload.texto,
        canal_origen=payload.canal_origen or ("QR_MESA" if payload.qr_token else "FORMULARIO_WEB"),
        tipo_input="TEXTO",
        calificacion_general=payload.calificacion_general,
        autor_nombre=payload.autor_nombre,
        qr_token=payload.qr_token
    )

@router.post("/upload-audio", response_model=ReviewDetailResponse, status_code=status.HTTP_201_CREATED, summary="Ingestar y transcribir audio de reseña")
async def create_audio_review(
    file: UploadFile = File(..., description="Archivo de audio (.wav, .mp3, .m4a, etc.)"),
    canal_origen: str = Form("AUDIO_IN_SITU", description="Canal de origen"),
    calificacion_general: Optional[int] = Form(None, ge=1, le=5, description="Calificación 1-5 estrellas"),
    autor_nombre: Optional[str] = Form("Anónimo", description="Nombre del autor"),
    qr_token: Optional[str] = Form(None, description="Token del pedido QR si proviene de una mesa"),
    db: Session = Depends(get_db)
):
    """
    Recibe un archivo de audio, lo transcribe localmente con faster-whisper,
    ejecuta el pipeline de NLP estructurado sobre el texto obtenido y persiste el resultado.
    """
    # Guardar archivo de audio temporalmente en storage local
    ext = os.path.splitext(file.filename)[1] or ".wav"
    unique_filename = f"{uuid.uuid4()}{ext}"
    audio_full_path = os.path.join(settings.STORAGE_DIR, unique_filename)

    with open(audio_full_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Obtener catálogo activo para inyectar como sesgo de vocabulario (initial_prompt) en faster-whisper
    platillos_db = db.query(Platillo.nombre).filter(Platillo.activo == True).all()
    catalogo_nombres = [p[0] for p in platillos_db]

    # Transcripción STT local con initial_prompt dinámico
    stt_result = stt_service.transcribe(audio_full_path, catalogo_platillos=catalogo_nombres)
    # Si el motor STT no detecta voz (FALLIDO), no lanzamos HTTP 500: persistimos la reseña
    # con estado_procesamiento: 'FALLIDO' para trazabilidad operativa sin asociar platillos.
    es_fallido = stt_result.get("estado_procesamiento") == "FALLIDO"
    texto_transcrito = stt_result.get("texto_transcrito", "").strip()
    if not texto_transcrito:
        texto_transcrito = "(Audio sin contenido de voz inteligible detectado)"

    datos_stt = {
        "audio_path": audio_full_path,
        "duracion_segundos": stt_result.get("duracion_segundos"),
        "texto_transcrito": texto_transcrito,
        "confianza": stt_result.get("confianza", 0.0),
        "idioma_detectado": stt_result.get("idioma_detectado", "es"),
        "estado_procesamiento": "FALLIDO" if es_fallido else stt_result.get("estado_procesamiento", "TRANSCRITO")
    }

    return _procesar_y_persistir_resena(
        db=db,
        texto_resena=texto_transcrito,
        canal_origen=canal_origen,
        tipo_input="AUDIO",
        calificacion_general=calificacion_general,
        autor_nombre=autor_nombre,
        datos_transcripcion=datos_stt,
        qr_token=qr_token
    )

@router.get("/{review_id}", response_model=ReviewDetailResponse, summary="Obtener detalle de una reseña")
def get_review_detail(
    review_id: str,
    db: Session = Depends(get_db)
):
    """
    Retorna la reseña con su análisis completo de sentimientos por platillo,
    sentimientos del establecimiento, atributos mencionados y datos de transcripción.
    """
    resena = db.query(Resena).options(
        joinedload(Resena.transcripcion),
        joinedload(Resena.sentimientos).joinedload(SentimientoPlatillo.atributos),
        joinedload(Resena.sentimientos_establecimiento)
    ).filter(Resena.id == review_id).first()

    if not resena:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reseña con ID '{review_id}' no encontrada."
        )

    return resena
