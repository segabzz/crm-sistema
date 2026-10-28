"""
Script de ejecución y validación completa del dataset de prueba (6 reseñas)
y consulta de los endpoints de analíticas:
1. Ingesta 5 reseñas de texto variadas.
2. Ingesta 1 reseña de audio real (audio_3_salmon.wav).
3. Consulta y reporta GET /api/v1/analytics/ranking.
4. Consulta y reporta GET /api/v1/analytics/trends.
"""

import os
import sys
import json
import httpx

BASE_URL = "http://127.0.0.1:8000/api/v1"

REVIEWS_DATA = [
    {
        "tipo": "TEXT",
        "payload": {
            "texto": "los tacos de res braseada estuvieron increíbles y el agua de horchata artesanal muy fresca",
            "canal_origen": "GOOGLE_MAPS",
            "calificacion_general": 5,
            "autor_nombre": "Alejandro Peña"
        }
    },
    {
        "tipo": "TEXT",
        "payload": {
            "texto": "el ribeye a la parrilla estaba duro y frío, una decepción total",
            "canal_origen": "TRIPADVISOR",
            "calificacion_general": 2,
            "autor_nombre": "Lucía Morales"
        }
    },
    {
        "tipo": "TEXT",
        "payload": {
            "texto": "pedimos ribeye a la parrilla y la carne estaba muy grasosa, no lo recomiendo",
            "canal_origen": "FORMULARIO_WEB",
            "calificacion_general": 2,
            "autor_nombre": "Javier R."
        }
    },
    {
        "tipo": "TEXT",
        "payload": {
            "texto": "el salmón al ajillo delicioso y el pastel tres leches es una maravilla de porción grande",
            "canal_origen": "WHATSAPP",
            "calificacion_general": 5,
            "autor_nombre": "Sofía Castro"
        }
    },
    {
        "tipo": "TEXT",
        "payload": {
            "texto": "la sopa azteca estaba fría y excesivamente salada, pero el guacamole rústico sí nos gustó",
            "canal_origen": "GOOGLE_MAPS",
            "calificacion_general": 3,
            "autor_nombre": "Martín Vega"
        }
    },
    {
        "tipo": "AUDIO",
        "audio_file": "backend/storage/audios/audio_3_salmon.wav",
        "form_data": {
            "canal_origen": "AUDIO_IN_SITU",
            "calificacion_general": "5",
            "autor_nombre": "Audio Mesa 7 (Salmón y Pastel)"
        }
    }
]

def run_suite():
    print("=" * 85)
    print("INICIANDO INGESTA REAL DE 6 RESEÑAS VARIADAS (TEXTO Y AUDIO)")
    print("=" * 85)

    client = httpx.Client(timeout=45.0)

    for idx, rev in enumerate(REVIEWS_DATA, 1):
        print(f"\n" + "-" * 75)
        print(f">>> ENVIANDO RESEÑA {idx}/6 ({rev['tipo']})")
        print("-" * 75)

        if rev["tipo"] == "TEXT":
            res = client.post(f"{BASE_URL}/reviews/text", json=rev["payload"])
        else:
            audio_path = os.path.abspath(rev["audio_file"])
            with open(audio_path, "rb") as f:
                res = client.post(
                    f"{BASE_URL}/reviews/upload-audio",
                    data=rev["form_data"],
                    files={"file": ("audio_3_salmon.wav", f, "audio/wav")}
                )

        print(f"HTTP Status: {res.status_code}")
        body = res.json()
        print("JSON Devuelto por el Servidor:")
        print(json.dumps(body, indent=2, ensure_ascii=False))

    # Consulta de Ranking
    print("\n" + "=" * 85)
    print("CONSULTA REAL: GET /api/v1/analytics/ranking")
    print("=" * 85)
    res_ranking = client.get(f"{BASE_URL}/analytics/ranking")
    print(f"HTTP Status: {res_ranking.status_code}")
    ranking_json = res_ranking.json()
    print(json.dumps(ranking_json, indent=2, ensure_ascii=False))

    # Consulta de Tendencias
    print("\n" + "=" * 85)
    print("CONSULTA REAL: GET /api/v1/analytics/trends?dias=7")
    print("=" * 85)
    res_trends = client.get(f"{BASE_URL}/analytics/trends?dias=7")
    print(f"HTTP Status: {res_trends.status_code}")
    trends_json = res_trends.json()
    print(json.dumps(trends_json, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_suite()
