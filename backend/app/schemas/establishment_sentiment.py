from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class EstablishmentSentimentResponse(BaseModel):
    id: str
    categoria: str
    polaridad: str
    score_numerico: float
    fragmento_texto: Optional[str] = None
    valor_mencionado: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
