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

# Prompt variante A: Actual
# Prompt variante B: Aclarar que la búsqueda no distingue mayúsculas y dar ejemplos claros
# Prompt variante C: Instrucción explícita de mapeo de nombres exactos

prompts = {
    "A (Actual)": f"""Eres un extractor de reseñas gastronómicas para un restaurante.
Dispones ÚNICAMENTE del siguiente CATÁLOGO OFICIAL DE PLATILLOS:
{chr(10).join([f'- "{p}"' for p in catalogo])}

REGLAS ESTRICTAS DE EXTRACCIÓN:
1. 'platillo_sugerido': Debe ser EXACTAMENTE uno de los nombres del catálogo oficial si hay coincidencia semántica clara.
   - Si se menciona un platillo o comida que NO corresponde claramente a ninguno de la lista, asigna obligatoriamente "Sin Clasificar".
   - NO inventes ningún nombre fuera del catálogo oficial ni de "Sin Clasificar".
   - Si no se menciona comida ni platillos específicos, devuelve la lista vacía [].
2. 'texto_mencionado': La frase o cita textual completa donde el usuario habla del platillo (incluyendo aclaraciones si las hay).
3. 'polaridad': 'positivo', 'neutral' o 'negativo'.
4. 'atributos': Lista de strings con todas las cualidades, temperaturas, porciones o quejas mencionadas (ej: ["fríos"], ["dura", "porción chica"]). Si no hay atributos, devuelve [].

Texto a analizar:
\"{texto}\"""",

    "B (Instrucción simplificada y directa)": f"""Eres un asistente que analiza reseñas de un restaurante.
Identifica los platillos mencionados en el texto y asócialos al CATÁLOGO OFICIAL:
{chr(10).join([f'- "{p}"' for p in catalogo])}

INSTRUCCIONES:
- Para cada platillo mencionado, 'platillo_sugerido' DEBE ser el nombre EXACTO del catálogo que coincida (por ejemplo, 'Sopa Azteca', 'Ribeye a la Parrilla', etc.).
- Si se menciona un platillo o comida que NO existe en el catálogo, usa 'Sin Clasificar'.
- 'texto_mencionado': Fragmento donde se menciona el platillo.
- 'polaridad': 'positivo', 'neutral' o 'negativo'.
- 'atributos': Lista de atributos o quejas (ej: ['fría']).

Texto:
\"{texto}\""""
}

for name, p in prompts.items():
    print(f"\n=================== PROMPT {name} ===================")
    res = ollama.chat(
        model="llama3.2:latest",
        messages=[{"role": "user", "content": p}],
        format=AnalisisResenaLLM.model_json_schema(),
        options={"temperature": 0.0}
    )
    print(res.message.content)
