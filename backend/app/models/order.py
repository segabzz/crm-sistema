import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Pedido(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qr_token = Column(String(64), unique=True, nullable=False, index=True, default=lambda: f"ord-{uuid.uuid4().hex[:12]}")
    mesa = Column(String(50), nullable=True, default="Mesa General")
    total = Column(Float, nullable=False, default=0.0)
    # Informativo ('ACTIVO' | 'EVALUADO'): no bloquea que múltiples comensales de la misma mesa envíen su reseña
    estado = Column(String(20), nullable=False, default="ACTIVO")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relaciones
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    resenas = relationship("Resena", back_populates="pedido")


class ItemPedido(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = Column(String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    platillo_id = Column(String(36), ForeignKey("dishes.id", ondelete="RESTRICT"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False, default=0.0)

    # Relaciones
    pedido = relationship("Pedido", back_populates="items")
    platillo = relationship("Platillo")
