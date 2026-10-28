from pydantic_settings import BaseSettings
from typing import List
import os

CRM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_DB_PATH = os.path.join(CRM_ROOT, "crm.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "CRM de Análisis de Reseñas Gastronómicas"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Base de Datos (anclada a la raíz canónica del proyecto CRM)
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    
    # Modelos IA
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"
    WHISPER_MODEL_SIZE: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    
    # Guardrail Keywords de exclusión/duda
    GUARDRAIL_NEGATION_KEYWORDS: List[str] = [
        "no venia", "no venian", "no era", "no eran", "fuera del", "fuera de",
        "otro", "otra", "otros", "otras", "no estaba", "no estaban",
        "diferente", "diferentes", "no pedi", "no pedimos", "en vez de", "en lugar de"
    ]
    
    # Almacenamiento local de archivos
    STORAGE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "audios")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

settings = Settings()

# Asegurar que el directorio de storage exista
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
