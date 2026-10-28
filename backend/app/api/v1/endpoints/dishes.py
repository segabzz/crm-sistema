from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.dish import Platillo
from app.schemas.dish import DishResponse

router = APIRouter()

@router.get("", response_model=List[DishResponse], summary="Listar catálogo de platillos")
def list_dishes(
    solo_activos: bool = Query(True, description="Filtrar solo platillos actualmente activos"),
    db: Session = Depends(get_db)
):
    """
    Retorna la lista de platillos registrados en el catálogo oficial del restaurante.
    """
    query = db.query(Platillo)
    if solo_activos:
        query = query.filter(Platillo.activo == True)
    return query.order_by(Platillo.categoria, Platillo.nombre).all()
