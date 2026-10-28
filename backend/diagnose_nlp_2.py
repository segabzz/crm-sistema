import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.nlp_service import nlp_service, AnalisisResenaLLM
from app.core.database import SessionLocal
from app.models.dish import Platillo
import ollama

db = SessionLocal()
catalogo = [p.nombre for p in db.query(Platillo).filter(Platillo.activo == True).all()]
db.close()

print("CATÁLOGO:", catalogo)

texto_min = "la sopa azteca estaba fría pero el ribeye a la parrilla quedó exquisito"
texto_may = "La Sopa Azteca estaba fría pero el ribeye a la Parrilla quedó exquisito."

print("\n--- PRUEBA 1: TEXTO EN MINÚSCULAS ---")
items_min = nlp_service.analyze_review(texto_min, catalogo)
for it in items_min:
    print(f"  texto_mencionado: '{it.texto_mencionado}' | sugerido_llm: '{it.platillo_original_llm}' | final: '{it.platillo_final}' | atributos: {it.atributos} | guardrail: {it.fue_reasignado_por_guardrail} ({it.motivo_guardrail})")

print("\n--- PRUEBA 2: TEXTO CON MAYÚSCULAS DE TRANSCRIPCIÓN ---")
items_may = nlp_service.analyze_review(texto_may, catalogo)
for it in items_may:
    print(f"  texto_mencionado: '{it.texto_mencionado}' | sugerido_llm: '{it.platillo_original_llm}' | final: '{it.platillo_final}' | atributos: {it.atributos} | guardrail: {it.fue_reasignado_por_guardrail} ({it.motivo_guardrail})")
