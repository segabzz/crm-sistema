from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DishBase(BaseModel):
    nombre: str
    categoria: str = "Plato Fuerte"
    descripcion: Optional[str] = None
    precio: float = 0.0
    activo: bool = True

class DishCreate(DishBase):
    pass

class DishResponse(DishBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
