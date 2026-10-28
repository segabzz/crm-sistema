"""
Script de evaluación experimental sobre el corpus de 50 reseñas etiquetadas.
Calcula métricas de desempeño del pipeline de IA (Llama 3.2 + Guardrails):
- Exactitud de asignación de platillo al catálogo
- Exactitud de polaridad
- Rendimiento por tipología de caso (Negación, Fuera de catálogo, Multiplatillo, etc.)
- Latencia promedio por reseña
"""

import os
import sys
import csv
import json
import time
import httpx

# Asegurar path de importación
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, BACKEND_DIR)

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.dish import Platillo
from app.services.nlp_service import nlp_service, NLPServiceError

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "corpus_resenas.csv")
OUTPUT_REPORT_PATH = os.path.join(os.path.dirname(__file__), "reporte_evaluacion_corpus.json")

def check_ollama_status() -> bool:
    try:
        r = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/version", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False

def evaluar():
    print("=" * 80)
    print("EVALUACIÓN EXPERIMENTAL DEL CORPUS DE RESEÑAS")
    print(f"Modelo configurado: {settings.OLLAMA_MODEL} en {settings.OLLAMA_BASE_URL}")
    print(f"Archivo de corpus: {CORPUS_PATH}")
    print("=" * 80)

    # 1. Verificar estado de Ollama
    is_online = check_ollama_status()
    if not is_online:
        print("\n[AVISO CRÍTICO] El servicio Ollama no está en ejecución en " + settings.OLLAMA_BASE_URL)
        print("Para ejecutar la evaluación completa con inferencia real:")
        print("  1. Inicia Ollama en otra terminal: ollama serve")
        print("  2. Asegúrate de tener el modelo: ollama pull llama3.2:latest")
        print("  3. Vuelve a ejecutar este script: python validation/evaluar_corpus.py\n")
        return

    # 2. Cargar catálogo activo
    db = SessionLocal()
    catalogo = [p.nombre for p in db.query(Platillo).filter(Platillo.activo == True).all()]
    db.close()
    print(f"Catálogo oficial activo ({len(catalogo)} platillos): {catalogo}\n")

    # 3. Leer reseñas del CSV
    with open(CORPUS_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        filas = list(reader)

    print(f"Total de casos de prueba a evaluar: {len(filas)}")
    print("-" * 80)

    resultados = []
    aciertos_platillo = 0
    aciertos_polaridad = 0
    desglose_tipos = {}
    tiempos = []

    for fila in filas:
        cid = fila["id"]
        texto = fila["texto"]
        platillo_esp = fila["platillo_esperado"]
        polaridad_esp = fila["polaridad_esperada"]
        tipo_caso = fila["tipo_caso"]

        if tipo_caso not in desglose_tipos:
            desglose_tipos[tipo_caso] = {"total": 0, "aciertos_platillo": 0, "aciertos_polaridad": 0}
        desglose_tipos[tipo_caso]["total"] += 1

        t0 = time.time()
        try:
            items = nlp_service.analyze_review(texto, catalogo)
            duracion = time.time() - t0
            tiempos.append(duracion)

            # Para evaluación, comparamos contra el platillo primario o primer item devuelto
            if not items:
                platillo_obtenido = "Sin Clasificar"
                polaridad_obtenida = "neutral"
                guardrail_disparado = False
            else:
                platillo_obtenido = items[0].platillo_final
                polaridad_obtenida = items[0].polaridad
                guardrail_disparado = any(it.fue_reasignado_por_guardrail for it in items)

            match_platillo = (platillo_obtenido == platillo_esp)
            match_polaridad = (polaridad_obtenida == polaridad_esp)

            if match_platillo:
                aciertos_platillo += 1
                desglose_tipos[tipo_caso]["aciertos_platillo"] += 1
            if match_polaridad:
                aciertos_polaridad += 1
                desglose_tipos[tipo_caso]["aciertos_polaridad"] += 1

            status_p = "✓" if match_platillo else "✗"
            status_pol = "✓" if match_polaridad else "✗"

            print(f"[{cid:02d}] {tipo_caso:<20} | Platillo: {status_p} ('{platillo_obtenido}') | Pol: {status_pol} ('{polaridad_obtenida}') | {duracion:.2f}s")

            resultados.append({
                "id": cid,
                "texto": texto,
                "tipo_caso": tipo_caso,
                "esperado": {"platillo": platillo_esp, "polaridad": polaridad_esp},
                "obtenido": {"platillo": platillo_obtenido, "polaridad": polaridad_obtenida},
                "match_platillo": match_platillo,
                "match_polaridad": match_polaridad,
                "guardrail_disparado": guardrail_disparado,
                "latencia_segundos": round(duracion, 3)
            })

        except Exception as e:
            print(f"[{cid:02d}] ERROR al procesar '{texto[:30]}...': {e}")

    total = len(filas)
    acc_platillo = round(aciertos_platillo / total * 100, 2) if total > 0 else 0
    acc_polaridad = round(aciertos_polaridad / total * 100, 2) if total > 0 else 0
    tiempo_promedio = round(sum(tiempos) / len(tiempos), 3) if tiempos else 0

    print("=" * 80)
    print("RESUMEN DE MÉTRICAS GLOBALES:")
    print(f" - Casos evaluados: {total}")
    print(f" - Exactitud en Platillo (Catalog Match): {acc_platillo}% ({aciertos_platillo}/{total})")
    print(f" - Exactitud en Polaridad: {acc_polaridad}% ({aciertos_polaridad}/{total})")
    print(f" - Latencia promedio por reseña: {tiempo_promedio} s")
    print("\nDesglose por Tipología:")
    for tipo, d in desglose_tipos.items():
        t_sub = d["total"]
        acc_p_sub = round(d["aciertos_platillo"] / t_sub * 100, 1)
        acc_pol_sub = round(d["aciertos_polaridad"] / t_sub * 100, 1)
        print(f"  • {tipo:<20}: Platillo: {acc_p_sub}% ({d['aciertos_platillo']}/{t_sub}) | Polaridad: {acc_pol_sub}% ({d['aciertos_polaridad']}/{t_sub})")

    reporte = {
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
        "modelo": settings.OLLAMA_MODEL,
        "total_casos": total,
        "exactitud_platillo_porcentaje": acc_platillo,
        "exactitud_polaridad_porcentaje": acc_polaridad,
        "latencia_promedio_segundos": tiempo_promedio,
        "desglose_por_tipo": desglose_tipos,
        "detalle_casos": resultados
    }

    with open(OUTPUT_REPORT_PATH, mode="w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)

    print(f"\nReporte JSON detallado guardado en: {OUTPUT_REPORT_PATH}")
    print("=" * 80)

if __name__ == "__main__":
    evaluar()
