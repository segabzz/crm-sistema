import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Resena(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    canal_origen = Column(String(50), nullable=False, default="FORMULARIO_WEB")
    tipo_input = Column(String(20), nullable=False, default="TEXTO")  # 'TEXTO' o 'AUDIO'
    calificacion_general = Column(Integer, nullable=True)  # 1 a 5 estrellas
    autor_nombre = Column(String(120), nullable=True, default="Anónimo")
    texto_original = Column(Text, nullable=False)
    estado_analisis = Column(String(30), nullable=False, default="COMPLETADO")  # 'COMPLETADO', 'FALLIDO_NLP', 'OMITIDO_AUDIO_FALLIDO'
    fecha_resena = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    pedido = relationship("Pedido", back_populates="resenas")
    transcripcion = relationship("TranscripcionAudio", back_populates="resena", uselist=False, cascade="all, delete-orphan")
    sentimientos = relationship("SentimientoPlatillo", back_populates="resena", cascade="all, delete-orphan")
    sentimientos_establecimiento = relationship("SentimientoEstablecimiento", back_populates="resena", cascade="all, delete-orphan")
