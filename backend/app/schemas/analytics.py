from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class DishRankingItem(BaseModel):
    platillo_id: str
    nombre: str
    categoria: str
    total_menciones: int
    positivas: int
    negativas: int
    neutrales: int
    score_ponderado: float
    tasa_positiva: float
    tasa_negativa: float

    model_config = ConfigDict(from_attributes=True)

class RankingResponse(BaseModel):
    total_evaluaciones: int
    top_platillos: List[DishRankingItem]
    platillos_en_riesgo: List[DishRankingItem]

class AttributeFrequencyItem(BaseModel):
    categoria_atributo: str
    total_menciones: int
    positivas: int
    negativas: int
    neutrales: int
    ejemplos_valores: List[str]

    model_config = ConfigDict(from_attributes=True)

class DishTrendItem(BaseModel):
    platillo_id: str
    nombre: str
    menciones_periodo_reciente: int
    score_polaridad_reciente: Optional[float] = None
    menciones_periodo_previo: int
    score_polaridad_previo: Optional[float] = None
    cambio_polaridad: Optional[float] = None
    tendencia: str  # "MEJORANDO", "EMPEORANDO", "ESTABLE", "SIN_DATOS_PREVIOS"
    atributos_destacados: List[AttributeFrequencyItem] = []

class UnclassifiedMentionsSummary(BaseModel):
    total_menciones: int
    positivas: int
    negativas: int
    neutrales: int
    atributos_asociados: List[AttributeFrequencyItem] = []

class EstablishmentTrendsSummary(BaseModel):
    total_menciones: int = 0
    positivas: int = 0
    negativas: int = 0
    neutrales: int = 0
    categorias: List[AttributeFrequencyItem] = []

class TrendsResponse(BaseModel):
    periodo_dias: int
    fecha_corte: str
    tendencias_por_platillo: List[DishTrendItem]
    atributos_mas_mencionados_global: List[AttributeFrequencyItem]
    menciones_sin_clasificar: UnclassifiedMentionsSummary
    sentimientos_establecimiento: EstablishmentTrendsSummary = EstablishmentTrendsSummary()
