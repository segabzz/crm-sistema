"""Regression check (no DB writes): does the exclusion guardrail still fire for Example 2?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.services.nlp_service import nlp_service
from app.core.database import SessionLocal
from app.models.dish import Platillo

db = SessionLocal()
catalogo = [p.nombre for p in db.query(Platillo).filter(Platillo.activo == True).all()]
db.close()

texto = "pedí dos tacos que no venían en el menú de especiales y además estaban fríos"
for i in range(1, 3):
    print(f"--- Corrida {i} ---")
    for it in nlp_service.analyze_review(texto, catalogo):
        print(f"  texto_mencionado='{it.texto_mencionado}' | llm='{it.platillo_original_llm}' | final='{it.platillo_final}' | guardrail={it.fue_reasignado_por_guardrail} | motivo={it.motivo_guardrail}")
