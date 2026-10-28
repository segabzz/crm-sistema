import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class TranscripcionAudio(Base):
    __tablename__ = "audio_transcriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resena_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), unique=True, nullable=False)
    audio_path = Column(String(255), nullable=False)
    duracion_segundos = Column(Float, nullable=True)
    texto_transcrito = Column(Text, nullable=False)
    confianza = Column(Float, nullable=True)
    idioma_detectado = Column(String(10), default="es", nullable=False)
    estado_procesamiento = Column(String(30), default="TRANSCRITO", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relación
    resena = relationship("Resena", back_populates="transcripcion")
