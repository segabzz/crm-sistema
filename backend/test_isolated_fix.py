import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.nlp_service import AnalisisResenaLLM
import ollama

catalogo = [
    "Tacos de Res Braseada",
    "Ribeye a la Parrilla",
    "Sopa Azteca",
    "Guacamole Rústico",
    "Salmón al Ajillo",
    "Pastel Tres Leches",
    "Agua de Horchata Artesanal"
]

texto = "La Sopa Azteca estaba fría pero el ribeye a la Parrilla quedó exquisito."
catalogo_str = "\n".join([f'- "{p}"' for p in catalogo])

# Probando el prompt original donde funcionaba:
prompt_original = f"""Eres un extractor de reseñas gastronómicas para un restaurante.
Dispones ÚNICAMENTE del siguiente CATÁLOGO OFICIAL DE PLATILLOS:
{catalogo_str}

REGLAS ESTRICTAS DE EXTRACCIÓN:
1. 'platillo_sugerido': Debe ser EXACTAMENTE uno de los nombres del catálogo oficial si hay coincidencia con el platillo mencionado.
   - Si se menciona un platillo que NO está en la lista oficial, asigna "Sin Clasificar".
   - NO inventes nombres fuera del catálogo oficial.
   - Si no se mencionan platillos específicos, devuelve [].
2. 'texto_mencionado': El nombre o fragmento exacto donde se menciona este platillo (ej: 'la sopa azteca', 'el ribeye a la parrilla'). NO pongas la reseña entera.
3. 'polaridad': 'positivo', 'neutral' o 'negativo'.
4. 'atributos': Lista de cualidades o quejas de este platillo (ej: ['fría']).

Texto a analizar:
\"{texto}\""""

res = ollama.chat(
    model="llama3.2:latest",
    messages=[{"role": "user", "content": prompt_original}],
    format=AnalisisResenaLLM.model_json_schema(),
    options={"temperature": 0.0}
)
print("RESULTADO CON PROMPT CORREGIDO:\n", res.message.content)
