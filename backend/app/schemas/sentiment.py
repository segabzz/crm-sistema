from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.attribute import AttributeResponse

class SentimentResponse(BaseModel):
    id: str
    platillo_id: Optional[str] = None
    platillo_nombre_referenciado: str
    polaridad: str
    score_numerico: float
    fragmento_texto: Optional[str] = None
    justificacion: Optional[str] = None
    created_at: datetime
    atributos: List[AttributeResponse] = []

    model_config = ConfigDict(from_attributes=True)
