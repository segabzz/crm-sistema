import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class AtributoMencionado(Base):
    __tablename__ = "mentioned_attributes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sentimiento_platillo_id = Column(String(36), ForeignKey("dish_sentiments.id", ondelete="CASCADE"), nullable=False)
    categoria_atributo = Column(String(50), nullable=False, default="general")  # 'sabor', 'temperatura', 'porcion', etc.
    valor_mencionado = Column(String(100), nullable=False)
    polaridad = Column(String(20), nullable=False, default="neutral")  # 'positivo', 'neutral', 'negativo'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relación
    sentimiento = relationship("SentimientoPlatillo", back_populates="atributos")
