"""
Script completo de reset limpio y ejecución del dataset de 6 reseñas:
1. Resetea la base de datos vía POST /api/v1/admin/reset-database.
2. Inserta las 6 reseñas del dataset de prueba (5 texto + 1 audio).
3. Consulta GET /api/v1/analytics/ranking (con Wilson Score puro).
4. Consulta GET /api/v1/analytics/trends.
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

def main():
    client = httpx.Client(timeout=45.0)

    print("=" * 85)
    print("PASO 1: RESETEO TOTAL Y LIMPIEZA DE LA BASE DE DATOS")
    print("=" * 85)
    res_reset = client.post(f"{BASE_URL}/admin/reset-database")
    print(f"Status Reset: {res_reset.status_code}")
    print("Respuesta Reset:", res_reset.json())

    print("\n" + "=" * 85)
    print("PASO 2: INGESTA DE LAS 6 RESEÑAS EN BASE LIMPIA")
    print("=" * 85)

    for idx, rev in enumerate(REVIEWS_DATA, 1):
        print(f"\n--- Ingestando Reseña {idx}/6 ({rev['tipo']}) ---")
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

        print(f"Status: {res.status_code}")
        body = res.json()
        print(f"Reseña ID: {body['id']} | Canal: {body['canal_origen']} | Tipo: {body['tipo_input']}")
        print(f"Texto: \"{body['texto_original']}\"")
        for s in body["sentimientos"]:
            print(f"  -> Platillo: '{s['platillo_nombre_referenciado']}' ({s['platillo_id']}) | Polaridad: {s['polaridad']} | Atributos: {[a['valor_mencionado'] for a in s['atributos']]}")

    print("\n" + "=" * 85)
    print("PASO 3: CONSULTA GET /api/v1/analytics/ranking (WILSON SCORE INTERVAL PURO)")
    print("=" * 85)
    res_rank = client.get(f"{BASE_URL}/analytics/ranking")
    print(f"Status: {res_rank.status_code}")
    ranking_data = res_rank.json()
    print(json.dumps(ranking_data, indent=2, ensure_ascii=False))

    print("\n" + "=" * 85)
    print("PASO 4: CONSULTA GET /api/v1/analytics/trends?dias=7")
    print("=" * 85)
    res_trends = client.get(f"{BASE_URL}/analytics/trends?dias=7")
    print(f"Status: {res_trends.status_code}")
    trends_data = res_trends.json()
    print(json.dumps(trends_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
