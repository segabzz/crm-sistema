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

texto_audio = "La Sopa Azteca estaba fría pero el ribeye a la Parrilla quedó exquisito."

print("=" * 80)
print("DIAGNÓSTICO: 3 LLAMADAS AL LLM CON EL TEXTO EXACTO DEL AUDIO")
print(f"Texto de entrada: \"{texto_audio}\"")
print(f"Catálogo oficial: {catalogo}")
print(f"Temperatura configurada: 0.0")
print("=" * 80)

for i in range(1, 4):
    print(f"\n--- CORRIDA {i} ---")
    catalogo_formateado = "\n".join([f'- "{p}"' for p in catalogo])
    prompt = f"""Eres un extractor de reseñas gastronómicas para un restaurante.
Dispones ÚNICAMENTE del siguiente CATÁLOGO OFICIAL DE PLATILLOS:
{catalogo_formateado}

REGLAS ESTRICTAS DE EXTRACCIÓN:
1. 'platillo_sugerido': Debe ser EXACTAMENTE uno de los nombres del catálogo oficial si hay coincidencia semántica clara.
   - Si se menciona un platillo o comida que NO corresponde claramente a ninguno de la lista, asigna obligatoriamente "Sin Clasificar".
   - NO inventes ningún nombre fuera del catálogo oficial ni de "Sin Clasificar".
   - Si no se menciona comida ni platillos específicos, devuelve la lista vacía [].
2. 'texto_mencionado': La frase o cita textual completa donde el usuario habla del platillo (incluyendo aclaraciones si las hay).
3. 'polaridad': 'positivo', 'neutral' o 'negativo'.
4. 'atributos': Lista de strings con todas las cualidades, temperaturas, porciones o quejas mencionadas (ej: ["fríos"], ["dura", "porción chica"]). Si no hay atributos, devuelve [].

Texto a analizar:
\"{texto_audio}\""""

    res = ollama.chat(
        model=nlp_service.model_name,
        messages=[{"role": "user", "content": prompt}],
        format=AnalisisResenaLLM.model_json_schema(),
        options={"temperature": 0.0}
    )
    raw = res.message.content.strip()
    print("RAW JSON DEVUELTO POR OLLAMA:\n", raw)
    parsed = AnalisisResenaLLM.model_validate_json(raw)
    for p in parsed.platillos:
        plat_final, reasig, motivo = nlp_service._apply_guardrails(p, texto_audio, set(catalogo))
        print(f"  > Platillo sugerido por LLM: '{p.platillo_sugerido}'")
        print(f"  > Texto mencionado:          '{p.texto_mencionado}'")
        print(f"  > Polaridad:                 '{p.polaridad}'")
        print(f"  > Atributos:                 {p.atributos}")
        print(f"  > ¿Guardrail reasignó?:      {reasig}")
        print(f"  > Motivo Guardrail:          {motivo}")
        print(f"  > Platillo FINAL:            '{plat_final}'")
