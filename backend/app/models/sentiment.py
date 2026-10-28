import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class SentimientoPlatillo(Base):
    __tablename__ = "dish_sentiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resena_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    platillo_id = Column(String(36), ForeignKey("dishes.id", ondelete="SET NULL"), nullable=True)
    platillo_nombre_referenciado = Column(String(150), nullable=False)
    polaridad = Column(String(20), nullable=False)  # 'positivo', 'neutral', 'negativo'
    score_numerico = Column(Float, nullable=False, default=0.0)  # -1.0 a 1.0
    fragmento_texto = Column(Text, nullable=True)
    justificacion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    resena = relationship("Resena", back_populates="sentimientos")
    platillo = relationship("Platillo", back_populates="sentimientos")
    atributos = relationship("AtributoMencionado", back_populates="sentimiento", cascade="all, delete-orphan")
