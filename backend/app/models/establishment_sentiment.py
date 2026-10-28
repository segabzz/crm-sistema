import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class SentimientoEstablecimiento(Base):
    __tablename__ = "establishment_sentiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resena_id = Column(String(36), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    categoria = Column(String(50), nullable=False)  # 'servicio', 'ambiente', 'limpieza', 'tiempo_espera'
    polaridad = Column(String(20), nullable=False)  # 'positivo', 'neutral', 'negativo'
    score_numerico = Column(Float, nullable=False, default=0.0)  # -1.0, 0.0, 1.0
    fragmento_texto = Column(Text, nullable=True)
    valor_mencionado = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relación
    resena = relationship("Resena", back_populates="sentimientos_establecimiento")
