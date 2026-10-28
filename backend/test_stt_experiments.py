"""
Script de validación experimental riguroso para initial_prompt en faster-whisper.
Ejecuta:
1. Audio 1 (4.73s - Sopa Azteca + Ribeye): Sin initial_prompt vs Con initial_prompt
2. Audio 2 (5.86s - Tacos de Res Braseada + Guacamole Rústico): Sin initial_prompt vs Con initial_prompt
3. Audio 3 (4.91s - Salmón al Ajillo + Pastel Tres Leches): Sin initial_prompt vs Con initial_prompt
4. Petición HTTP Real a la API (POST /api/v1/reviews/upload-audio)
"""

import sys
import os
import httpx
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.stt_service import stt_service
from app.core.database import SessionLocal
from app.models.dish import Platillo

def run_experiments():
    db = SessionLocal()
    platillos = [p.nombre for p in db.query(Platillo).filter(Platillo.activo == True).all()]
    db.close()

    print("=" * 85)
    print("EJECUTANDO EXPERIMENTOS REALES DE INITIAL_PROMPT CON FASTER-WHISPER")
    print(f"Catálogo actual ({len(platillos)} platillos): {platillos}")
    print("=" * 85)

    audios = [
        {
            "id": "Audio 1 (Ejemplo 3 Original)",
            "file": "backend/storage/audios/test_speech.wav",
            "frase_esperada": "la sopa azteca estaba fria pero el ribeye a la parrilla quedo exquisito"
        },
        {
            "id": "Audio 2 (Tacos + Guacamole)",
            "file": "backend/storage/audios/audio_2_tacos.wav",
            "frase_esperada": "los tacos de res braseada estuvieron excelentes pero el guacamole rustico tenia poca sal"
        },
        {
            "id": "Audio 3 (Salmón + Pastel)",
            "file": "backend/storage/audios/audio_3_salmon.wav",
            "frase_esperada": "el salmon al ajillo estaba en su punto y el pastel tres leches delicioso"
        }
    ]

    for item in audios:
        print(f"\n>>> PRUEBA: {item['id']}")
        print(f"    Frase Hablada: \"{item['frase_esperada']}\"")
        path = os.path.abspath(item["file"])

        # 1. Sin initial prompt
        res_sin = stt_service.transcribe(path, catalogo_platillos=None, initial_prompt=None)
        print("\n  [OUTPUT CRUDO SIN INITIAL_PROMPT]:")
        print(f"    Texto:      \"{res_sin['texto_transcrito']}\"")
        print(f"    Confianza:  {res_sin['confianza']} (Tiempo: {res_sin['tiempo_inferencia_segundos']}s)")

        # 2. Con initial prompt dinámico del catálogo
        res_con = stt_service.transcribe(path, catalogo_platillos=platillos)
        print("\n  [OUTPUT CRUDO CON INITIAL_PROMPT DINÁMICO]:")
        print(f"    Texto:      \"{res_con['texto_transcrito']}\"")
        print(f"    Confianza:  {res_con['confianza']} (Tiempo: {res_con['tiempo_inferencia_segundos']}s)")

        diff_conf = round(res_con['confianza'] - res_sin['confianza'], 3)
        print(f"    Diferencia en Confianza: {'+' if diff_conf >= 0 else ''}{diff_conf} ({'+' if diff_conf >= 0 else ''}{round(diff_conf*100, 1)}%)")

    # 4. Prueba HTTP End-to-End contra el servidor vivo
    print("\n" + "=" * 85)
    print("PRUEBA HTTP REAL CONTRA EL SERVIDOR VIVO (POST /api/v1/reviews/upload-audio)")
    print("=" * 85)
    url = "http://127.0.0.1:8000/api/v1/reviews/upload-audio"
    audio_test_path = os.path.abspath("backend/storage/audios/test_speech.wav")

    with open(audio_test_path, "rb") as f:
        response = httpx.post(
            url,
            data={
                "canal_origen": "AUDIO_IN_SITU",
                "calificacion_general": "5",
                "autor_nombre": "Carlos Mendoza (Mesa 2)"
            },
            files={"file": ("test_speech.wav", f, "audio/wav")},
            timeout=30.0
        )

    print(f"HTTP Status Code: {response.status_code}")
    print("Respuesta JSON Real devuelta por el servidor FastAPI:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_experiments()
