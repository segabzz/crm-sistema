from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db.reset_db import clean_and_reset_db

router = APIRouter()

@router.post("/reset-database", status_code=status.HTTP_200_OK, summary="Limpiar base de datos y reiniciar catálogo")
def reset_database_endpoint(db: Session = Depends(get_db)):
    """
    Elimina todas las reseñas, sentimientos, atributos y transcripciones previas.
    Restaura el catálogo de platillos en su estado inicial limpio sin alterar las tablas.
    """
    clean_and_reset_db(db)
    return {
        "status": "success",
        "message": "Base de datos reseteada exitosamente. Catálogo restaurado limpio."
    }
