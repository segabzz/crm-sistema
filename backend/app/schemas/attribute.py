from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AttributeResponse(BaseModel):
    id: str
    categoria_atributo: str
    valor_mencionado: str
    polaridad: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
