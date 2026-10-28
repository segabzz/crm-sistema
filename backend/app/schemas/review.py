from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.audio_transcription import AudioTranscriptionResponse
from app.schemas.sentiment import SentimentResponse
from app.schemas.establishment_sentiment import EstablishmentSentimentResponse

class ReviewCreateText(BaseModel):
    texto: str = Field(..., min_length=3, description="Texto de la reseña")
    canal_origen: Optional[str] = Field(default="FORMULARIO_WEB", description="Canal: FORMULARIO_WEB, GOOGLE_MAPS, WHATSAPP, MANUAL, QR_MESA, etc.")
    calificacion_general: Optional[int] = Field(default=None, ge=1, le=5, description="Calificación de 1 a 5 estrellas si se conoce")
    autor_nombre: Optional[str] = Field(default="Anónimo", description="Nombre del comensal o autor")
    qr_token: Optional[str] = Field(default=None, description="Token del pedido QR si proviene de una mesa")

class ReviewDetailResponse(BaseModel):
    id: str
    canal_origen: str
    tipo_input: str
    calificacion_general: Optional[int] = None
    autor_nombre: Optional[str] = None
    texto_original: str
    estado_analisis: str = "COMPLETADO"
    pedido_id: Optional[str] = None
    fecha_resena: datetime
    created_at: datetime
    transcripcion: Optional[AudioTranscriptionResponse] = None
    sentimientos: List[SentimentResponse] = []
    sentimientos_establecimiento: List[EstablishmentSentimentResponse] = []

    model_config = ConfigDict(from_attributes=True)
