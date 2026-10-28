from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class OrderItemCreate(BaseModel):
    platillo_id: str = Field(..., description="ID del platillo del catálogo")
    cantidad: int = Field(default=1, ge=1, description="Cantidad solicitada (>= 1)")

class OrderCreate(BaseModel):
    mesa: Optional[str] = Field(default="Mesa General", description="Identificador o nombre de la mesa")
    items: List[OrderItemCreate] = Field(..., min_length=1, description="Lista de platillos del pedido")

class OrderItemResponse(BaseModel):
    id: str
    platillo_id: str
    platillo_nombre: str
    platillo_categoria: str
    cantidad: int
    precio_unitario: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: str
    qr_token: str
    mesa: Optional[str] = None
    total: float
    estado: str
    created_at: datetime
    items: List[OrderItemResponse] = []
    total_resenas: int = 0

    model_config = ConfigDict(from_attributes=True)
