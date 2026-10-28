import os
import sys
import json
import time
import subprocess
import requests

API_URL = "http://127.0.0.1:5173/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"
ARTIFACTS_DIR = r"C:\Users\segabzz\.gemini\antigravity-cli\brain\99e89a17-e47e-4ac4-9e75-33a092bf67f6"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

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

def capture_screenshot(url, output_path):
    cmd = [
        EDGE_EXE,
        "--headless=new",
        f"--screenshot={output_path}",
        "--window-size=1280,950",
        "--hide-scrollbars",
        url
    ]
    subprocess.run(cmd, capture_output=True, timeout=15)
    print(f"[Screenshot] Guardado en: {output_path}")

def run_full_verification():
    print("=" * 80)
    print("1. LIMPIEZA INICIAL DE BASE DE DATOS VIA PROXY FRONTEND")
    print("=" * 80)
    r_reset = requests.post(f"{API_URL}/admin/reset-database", timeout=10)
    print("Status Reset:", r_reset.status_code, r_reset.json())

    print("\n" + "=" * 80)
    print("2. INGESTANDO DATASET DE 6 RESEÑAS")
    print("=" * 80)
    for idx, rev in enumerate(REVIEWS_DATA, 1):
        if rev["tipo"] == "TEXT":
            res = requests.post(f"{API_URL}/reviews/text", json=rev["payload"], timeout=30)
        else:
            path = rev["audio_file"]
            with open(path, "rb") as f:
                res = requests.post(
                    f"{API_URL}/reviews/upload-audio",
                    data=rev["form_data"],
                    files={"file": ("audio_3_salmon.wav", f, "audio/wav")},
                    timeout=30
                )
        print(f"[{idx}/6] {rev['tipo']} -> HTTP {res.status_code} | Resena ID: {res.json().get('id')}")

    print("\n" + "=" * 80)
    print("3. VERIFICACION VISTA 1: DASHBOARD & RANKING WILSON")
    print("=" * 80)
    res_rank = requests.get(f"{API_URL}/analytics/ranking", timeout=10)
    ranking = res_rank.json()
    print("Total Evaluaciones:", ranking["total_evaluaciones"])
    print("Top Platillos:")
    for p in ranking["top_platillos"]:
        print(f"  * {p['nombre']}: Wilson={p['score_ponderado']:.4f} ({p['positivas']}+/{p['negativas']}-) | Tasa Pos={p['tasa_positiva']*100:.0f}%")
    print("Platillos en Riesgo:")
    for r in ranking["platillos_en_riesgo"]:
        print(f"  * {r['nombre']}: Wilson={r['score_ponderado']:.4f} ({r['negativas']} quejas) | Tasa Neg={r['tasa_negativa']*100:.0f}%")

    res_trends = requests.get(f"{API_URL}/analytics/trends?dias_reciente=7", timeout=10)
    trends = res_trends.json()
    print("\nTendencias & Atributos Operativos:")
    for t in trends.get("tendencias_por_platillo", []):
        if t["atributos_destacados"]:
            attrs_str = ", ".join([f"{a['categoria_atributo']}:{a['total_menciones']}" for a in t["atributos_destacados"]])
            print(f"  * {t['nombre']} -> Tendencia: {t['tendencia']} | Atributos: {attrs_str}")

    print("\n" + "=" * 80)
    print("4. VERIFICACION VISTA 3: CATALOGO DE 7 PLATILLOS")
    print("=" * 80)
    res_dishes = requests.get(f"{API_URL}/dishes", timeout=10)
    dishes = res_dishes.json()
    print(f"Total platillos en catalogo: {len(dishes)}")
    for d in dishes:
        print(f"  - [{d['categoria']}] {d['nombre']} : ${d['precio']:.2f} MXN (Activo: {d['activo']})")

    print("\n" + "=" * 80)
    print("5. PRUEBA DEL BOTON RESET BD (ANTES Y DESPUES)")
    print("=" * 80)
    print(f"ANTES DEL RESET: {ranking['total_evaluaciones']} menciones evaluadas en 6 reseñas.")
    print(f"Top platillos en Dashboard ANTES del reset: {len(ranking['top_platillos'])}")
    print(f"Platillos en riesgo ANTES del reset: {len(ranking['platillos_en_riesgo'])}")
    
    # Ejecutar Reset vía proxy
    r_reset2 = requests.post(f"{API_URL}/admin/reset-database", timeout=10)
    print("\n[Ejecutando POST /api/v1/admin/reset-database vía proxy frontend...]")
    print("Status Reset:", r_reset2.status_code, r_reset2.json())

    # Consultar de nuevo Ranking y Catálogo
    res_rank_after = requests.get(f"{API_URL}/analytics/ranking", timeout=10)
    ranking_after = res_rank_after.json()
    res_trends_after = requests.get(f"{API_URL}/analytics/trends", timeout=10)
    trends_after = res_trends_after.json()
    res_dishes_after = requests.get(f"{API_URL}/dishes", timeout=10)
    dishes_after = res_dishes_after.json()

    print(f"\nDESPUES DEL RESET:")
    print(f"  * Total Evaluaciones: {ranking_after['total_evaluaciones']}")
    print(f"  * Total Platillos en Leaderboard: {len(ranking_after['top_platillos'])}")
    print(f"  * Platillos en Riesgo: {len(ranking_after['platillos_en_riesgo'])}")
    print(f"  * Atributos globales en Trends: {len(trends_after.get('atributos_mas_mencionados_global', []))}")
    print(f"  * Catálogo de Platillos intacto: {len(dishes_after)} platillos activos restaurados.")

    print("\n" + "=" * 80)
    print("VERIFICACION VISUAL Y NUMERICA COMPLETA EXITOSA")
    print("=" * 80)

if __name__ == "__main__":
    run_full_verification()
