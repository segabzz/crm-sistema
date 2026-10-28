import os
import time
import math
from typing import Optional
from faster_whisper import WhisperModel
from app.core.config import settings

class STTService:
    _instance: Optional["STTService"] = None
    _model: Optional[WhisperModel] = None

    def __init__(self):
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.device = settings.WHISPER_DEVICE
        self.compute_type = settings.WHISPER_COMPUTE_TYPE

    @classmethod
    def get_instance(cls) -> "STTService":
        if cls._instance is None:
            cls._instance = STTService()
        return cls._instance

    def _load_model(self) -> WhisperModel:
        if self._model is None:
            print(f"[STTService] Cargando modelo faster-whisper '{self.model_size}' en {self.device} ({self.compute_type})...")
            start = time.time()
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            print(f"[STTService] Modelo faster-whisper cargado en {time.time() - start:.2f}s")
        return self._model

    def transcribe(
        self,
        audio_path: str,
        catalogo_platillos: Optional[list[str]] = None,
        initial_prompt: Optional[str] = None
    ) -> dict:
        """
        Transcribe un archivo de audio local usando faster-whisper.
        Permite inyectar initial_prompt o una lista de platillos del catálogo para sesgar el vocabulario.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")

        model = self._load_model()
        start_time = time.time()

        # Construcción dinámica de initial_prompt si se proporciona catálogo
        prompt_final = initial_prompt
        if not prompt_final and catalogo_platillos:
            prompt_final = f"Vocabulario esperado del restaurante y menú: {', '.join(catalogo_platillos)}."

        if prompt_final:
            print(f"[STTService] Usando initial_prompt: '{prompt_final}'")

        try:
            # beam_size=1 y vad_filter=True para máxima velocidad en CPU
            segments, info = model.transcribe(
                audio_path,
                language="es",
                beam_size=1,
                vad_filter=True,
                initial_prompt=prompt_final
            )

            segment_texts = []
            segment_probs = []

            for segment in segments:
                segment_texts.append(segment.text)
                if hasattr(segment, "avg_logprob"):
                    # Convertir logprob a aproximación de probabilidad 0-1 con math.exp
                    prob = float(min(max(math.exp(segment.avg_logprob), 0.0), 1.0))
                    segment_probs.append(prob)

            texto_final = " ".join(segment_texts).strip()
            duracion = float(info.duration) if hasattr(info, "duration") else 0.0
            tiempo_inferencia = time.time() - start_time

            # Detección de audio sin voz inteligible
            if not segment_probs or not texto_final:
                print(f"[STTService] No se detectó contenido de voz en {audio_path} ({tiempo_inferencia:.2f}s)")
                return {
                    "texto_transcrito": "",
                    "duracion_segundos": round(duracion, 2),
                    "idioma_detectado": info.language or "es",
                    "confianza": 0.0,
                    "estado_procesamiento": "FALLIDO",
                    "tiempo_inferencia_segundos": round(tiempo_inferencia, 2),
                    "error": "No se detectó contenido de voz en el archivo de audio."
                }

            confianza_promedio = float(sum(segment_probs) / len(segment_probs))
            print(f"[STTService] Transcripción completada en {tiempo_inferencia:.2f}s: \"{texto_final}\"")

            return {
                "texto_transcrito": texto_final,
                "duracion_segundos": round(duracion, 2),
                "idioma_detectado": info.language or "es",
                "confianza": round(confianza_promedio, 3),
                "estado_procesamiento": "TRANSCRITO",
                "tiempo_inferencia_segundos": round(tiempo_inferencia, 2)
            }

        except Exception as e:
            print(f"[STTService ERROR] Falló la transcripción de {audio_path}: {e}")
            return {
                "texto_transcrito": "",
                "duracion_segundos": 0.0,
                "idioma_detectado": "es",
                "confianza": 0.0,
                "estado_procesamiento": "FALLIDO",
                "error": str(e)
            }

stt_service = STTService.get_instance()
