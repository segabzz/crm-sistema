import os
import wave
from fastapi.testclient import TestClient
from app.main import app

def test_silence_audio():
    client = TestClient(app)
    
    # 1. Crear audio de silencio de 1 segundo si no existe
    silence_path = "backend/test_silence.wav"
    with wave.open(silence_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00" * 32000)

    # 2. Enviar audio al endpoint
    with open(silence_path, "rb") as f:
        response = client.post(
            "/api/v1/reviews/upload-audio",
            files={"file": ("silencio.wav", f, "audio/wav")},
            data={
                "canal_origen": "AUDIO_IN_SITU",
                "autor_nombre": "Comensal Silencio",
                "calificacion_general": 2
            }
        )

    print(f"Status Code: {response.status_code}")
    data = response.json()
    import pprint
    print("\nRespuesta JSON completa persistida:")
    pprint.pprint(data)
    
    # Verificaciones de aserción
    assert response.status_code == 201, f"Esperado 201, obtenido {response.status_code}"
    assert data["transcripcion"]["estado_procesamiento"] == "FALLIDO", "El estado debe ser FALLIDO"
    assert data["transcripcion"]["confianza"] == 0.0, "La confianza debe ser 0.0"
    assert len(data["sentimientos"]) == 0, "No debe tener sentimientos asociados"
    print("\n[OK] Todas las aserciones de negocio pasaron exitosamente.")

if __name__ == "__main__":
    test_silence_audio()
