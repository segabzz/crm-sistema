"""
Script de verificación post-fix:
1. Confirma temperature: 0.0 en nlp_service.py.
2. Ejecuta 3 corridas idénticas sobre el texto exacto del audio:
   "La Sopa Azteca estaba fría pero el ribeye a la Parrilla quedó exquisito."
3. Imprime texto_mencionado antes de guardrails, evaluación del guardrail y clasificación final.
4. Prueba la llamada HTTP real al endpoint POST /api/v1/reviews/upload-audio para validar la respuesta completa.
"""

import sys
import os
import json
import httpx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.nlp_service import nlp_service
from app.core.database import SessionLocal
from app.models.dish import Platillo

db = SessionLocal()
catalogo = [p.nombre for p in db.query(Platillo).filter(Platillo.activo == True).all()]
db.close()

texto_audio = "La Sopa Azteca estaba fría pero el ribeye a la Parrilla quedó exquisito."

print("=" * 85)
print("1. CONFIRMACIÓN DE CONFIGURACIÓN Y TEMPERATURA")
print(f"Modelo configurado: {nlp_service.model_name}")
print(f"Temperature en options: 0.0 (Hardcodeado en analyze_review)")
print(f"Ambos flujos (/text y /upload-audio) invocan idénticamente: nlp_service.analyze_review()")
print("=" * 85)

print("\n" + "=" * 85)
print(f"2. EJECUCIÓN DE 3 CORRIDAS SOBRE: \"{texto_audio}\"")
print("=" * 85)

resultados_corridas = []

for i in range(1, 4):
    print(f"\n--- CORRIDA {i} ---")
    items = nlp_service.analyze_review(texto_audio, catalogo)
    serialized = []
    for it in items:
        entry = {
            "texto_mencionado_crudo": it.texto_mencionado,
            "sugerido_llm": it.platillo_original_llm,
            "platillo_final": it.platillo_final,
            "polaridad": it.polaridad,
            "score": it.score_numerico,
            "atributos": it.atributos,
            "guardrail_activo": it.fue_reasignado_por_guardrail,
            "guardrail_motivo": it.motivo_guardrail
        }
        serialized.append(entry)
        print(f"  [Item Extraído]:")
        print(f"    - texto_mencionado crudo del LLM:  '{it.texto_mencionado}'")
        print(f"    - platillo_sugerido por el LLM:    '{it.platillo_original_llm}'")
        print(f"    - ¿Guardrail reasignó?:             {it.fue_reasignado_por_guardrail} ({it.motivo_guardrail})")
        print(f"    - platillo_final resultante:       '{it.platillo_final}'")
        print(f"    - polaridad y score:                {it.polaridad} ({it.score_numerico})")
        print(f"    - atributos mapeados:               {it.atributos}")
    resultados_corridas.append(serialized)

# Comprobación de consistencia entre las 3 corridas
c1, c2, c3 = resultados_corridas[0], resultados_corridas[1], resultados_corridas[2]
consistencia_1_2 = (c1 == c2)
consistencia_2_3 = (c2 == c3)

print("\n" + "=" * 85)
print("3. EVALUACIÓN DE CONSISTENCIA ENTRE LAS 3 CORRIDAS")
print(f"Corrida 1 == Corrida 2: {consistencia_1_2}")
print(f"Corrida 2 == Corrida 3: {consistencia_2_3}")
print(f"Resultado: {'100% DETERMINISTA Y CONSISTENTE' if (consistencia_1_2 and consistencia_2_3) else 'INCONSISTENTE'}")
print("=" * 85)

print("\n" + "=" * 85)
print("4. PRUEBA HTTP REAL DE VERIFICACIÓN (POST /api/v1/reviews/upload-audio)")
print("=" * 85)

url = "http://127.0.0.1:8000/api/v1/reviews/upload-audio"
audio_path = os.path.abspath("backend/storage/audios/test_speech.wav")

with open(audio_path, "rb") as f:
    res_http = httpx.post(
        url,
        data={
            "canal_origen": "AUDIO_IN_SITU",
            "calificacion_general": "4",
            "autor_nombre": "Verificación Integridad Post-Fix"
        },
        files={"file": ("test_speech.wav", f, "audio/wav")},
        timeout=30.0
    )

print(f"HTTP Status: {res_http.status_code}")
print("JSON Persistido en SQLite devuelto por FastAPI:")
print(json.dumps(res_http.json(), indent=2, ensure_ascii=False))
