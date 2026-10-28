from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AudioTranscriptionResponse(BaseModel):
    id: str
    audio_path: str
    duracion_segundos: Optional[float] = None
    texto_transcrito: str
    confianza: Optional[float] = None
    idioma_detectado: str
    estado_procesamiento: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
