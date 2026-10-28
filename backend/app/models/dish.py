import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Platillo(Base):
    __tablename__ = "dishes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(150), unique=True, nullable=False, index=True)
    categoria = Column(String(50), nullable=False, default="Plato Fuerte")
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False, default=0.0)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    sentimientos = relationship("SentimientoPlatillo", back_populates="platillo")
