from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.analytics import RankingResponse, TrendsResponse
from app.services.ranking_service import ranking_service

router = APIRouter()

@router.get("/ranking", response_model=RankingResponse, summary="Ranking de platillos (Top y En Riesgo)")
def get_ranking(db: Session = Depends(get_db)):
    """
    Retorna el ranking ponderado bayesiano de los platillos del menú,
    clasificados en 'Top Platillos' (mayor satisfacción y volumen)
    y 'Platillos en Riesgo' (mayor tasa de quejas negativas recurrentes).
    """
    return ranking_service.calculate_ranking(db)

@router.get("/trends", response_model=TrendsResponse, summary="Tendencias temporales y atributos por platillo")
def get_trends(
    dias: int = Query(7, ge=1, le=90, description="Ventana de días para comparar periodo reciente vs periodo previo"),
    db: Session = Depends(get_db)
):
    """
    Retorna la agregación de atributos más mencionados a lo largo del tiempo,
    el cambio de polaridad de cada platillo (o 'SIN_DATOS_PREVIOS' si no hay histórico),
    y un desglose separado para menciones no clasificadas.
    """
    return ranking_service.calculate_trends(db, dias=dias)
