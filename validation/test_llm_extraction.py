"""
Script standalone de validación para extracción estructurada con Llama 3.2 (3B) en Ollama local.
Fase 2: Catálogo cerrado, mapeo semántico/sinónimos, atributos como List[str] y prueba de alucinación.
"""

import json
import httpx
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, ValidationError
import ollama

MODEL_NAME = "llama3.2:latest"

# 1. Catálogo oficial cerrado de prueba
CATALOGO_OFICIAL = [
    "Tacos de Res Braseada",
    "Ribeye a la Parrilla",
    "Sopa Azteca"
]
VALORES_PERMITIDOS = set(CATALOGO_OFICIAL + ["Sin Clasificar"])

# 2. Esquema Pydantic actualizado (atributos: List[str])
class PolaridadEnum(str, Enum):
    positivo = "positivo"
    neutral = "neutral"
    negativo = "negativo"

class PlatilloMencionado(BaseModel):
    platillo: str = Field(
        description="Debe ser EXACTAMENTE uno de los nombres del catálogo oficial, o 'Sin Clasificar' si no hay coincidencia clara."
    )
    polaridad: PolaridadEnum = Field(description="Polaridad: positivo, neutral o negativo")
    atributos: List[str] = Field(
        default_factory=list,
        description="Lista de atributos o cualidades mencionadas (ej: ['fríos', 'porción muy chica'], ['dura'])"
    )

class AnalisisResena(BaseModel):
    platillos: List[PlatilloMencionado] = Field(
        default_factory=list,
        description="Lista de platillos identificados mapeados al catálogo oficial."
    )

CASOS_PRUEBA_CATALOGO = [
    "los tacos de barbacoa estaban fríos",
    "la carne estaba dura",
    "pedí dos tacos que no venían en el menú de especiales"
]

def verificar_soporte_schema() -> tuple[bool, str]:
    """Verifica la versión de Ollama y el soporte de JSON Schema."""
    try:
        r = httpx.get("http://localhost:11434/api/version", timeout=3.0)
        version = r.json().get("version", "desconocida")
    except Exception as e:
        version = f"Error al consultar versión: {e}"

    schema = AnalisisResena.model_json_schema()
    try:
        ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "ping"}],
            format=schema,
            options={"temperature": 0}
        )
        return True, version
    except Exception as e:
        return False, f"{version} (Error con schema: {e})"

def ejecutar_extraccion_con_catalogo(texto: str, usar_schema: bool, temperature: float = 0.0) -> dict:
    """Ejecuta la llamada a Ollama enviando el catálogo en el prompt."""
    catalogo_str = "\n".join([f'- "{p}"' for p in CATALOGO_OFICIAL])

    prompt = f"""Eres un extractor de reseñas gastronómicas para un restaurante.
Dispones ÚNICAMENTE del siguiente CATÁLOGO OFICIAL DE PLATILLOS:
{catalogo_str}

REGLAS ESTRICTAS DE EXTRACCIÓN:
1. 'platillo': Debe ser EXACTAMENTE uno de los nombres del catálogo oficial anterior si hay coincidencia semántica o sinónimo evidente.
   - Si se menciona un platillo o comida que NO corresponde claramente a ninguno de la lista, asigna obligatoriamente "Sin Clasificar".
   - NO inventes ningún nombre fuera del catálogo oficial ni de "Sin Clasificar".
   - Si no se menciona comida ni platillos, devuelve la lista vacía [].
2. 'polaridad': 'positivo', 'neutral' o 'negativo'.
3. 'atributos': Lista de strings con todas las cualidades, temperaturas, porciones o quejas mencionadas (ej: ["fríos"], ["dura", "sin sabor"]). Si no hay atributos, devuelve [].

Texto a analizar:
\"{texto}\""""

    schema = AnalisisResena.model_json_schema() if usar_schema else "json"

    res = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        format=schema,
        options={"temperature": temperature}
    )

    raw_content = res.message.content.strip()

    # Validación Pydantic
    try:
        parsed_obj = AnalisisResena.model_validate_json(raw_content)
        es_valido = True
        error_msg = None
        data = parsed_obj.model_dump()
    except ValidationError as ve:
        try:
            data = json.loads(raw_content)
            es_valido = False
            error_msg = f"JSON parseable pero falló validación Pydantic: {ve}"
        except Exception as je:
            data = None
            es_valido = False
            error_msg = f"JSON inválido: {je}"

    # Verificación de respeto al catálogo cerrado
    respeta_catalogo = True
    alucinaciones = []
    if es_valido and data and "platillos" in data:
        for item in data["platillos"]:
            nombre = item.get("platillo")
            if nombre not in VALORES_PERMITIDOS:
                respeta_catalogo = False
                alucinaciones.append(nombre)

    return {
        "raw": raw_content,
        "parsed": data,
        "es_valido": es_valido,
        "respeta_catalogo": respeta_catalogo,
        "alucinaciones": alucinaciones,
        "error": error_msg
    }

def main():
    print("=" * 75)
    print("VALIDACIÓN EXTENDIDA: CATÁLOGO CERRADO Y ATRIBUTOS MÚLTIPLES")
    print("Modelo: llama3.2:latest (3B) en Ollama local")
    print("=" * 75)
    print("Catálogo Oficial de Prueba:")
    for p in CATALOGO_OFICIAL:
        print(f"  • {p}")
    print("  • Valor comodín autorizado: \"Sin Clasificar\"")
    print("=" * 75)

    soporta_schema, version_info = verificar_soporte_schema()
    print(f"Versión de Ollama: {version_info} | Modo: {'JSON Schema estricto' if soporta_schema else 'JSON Fallback'}")
    print("=" * 75)

    resultados_totales = []

    for idx, caso in enumerate(CASOS_PRUEBA_CATALOGO, 1):
        print(f"\n=======================================================================")
        print(f"CASO {idx}: \"{caso}\"")
        print(f"=======================================================================")

        corridas_caso = []
        for rep in range(1, 3):
            print(f"\n--- Repetición {rep} ---")
            res = ejecutar_extraccion_con_catalogo(caso, usar_schema=soporta_schema, temperature=0.0)
            corridas_caso.append(res)

            print(f"[RAW JSON RECIBIDO]:\n{res['raw']}")
            print(f"[PARSED / VÁLIDO]: {'SÍ' if res['es_valido'] else 'NO'}")
            print(f"[RESPETA CATÁLOGO CERRADO]: {'SÍ' if res['respeta_catalogo'] else 'NO - ALUCINÓ: ' + str(res['alucinaciones'])}")
            if res['es_valido']:
                print(f"[DATOS ESTRUCTURADOS]: {res['parsed']}")
            else:
                print(f"[ERROR]: {res['error']}")

        # Comparación de consistencia
        c1, c2 = corridas_caso[0], corridas_caso[1]
        consistente_raw = (c1['raw'] == c2['raw'])
        consistente_datos = (c1['parsed'] == c2['parsed'])

        print(f"\n>>> Evaluación Caso {idx}:")
        if consistente_raw:
            print("  Consistencia: 100% IDÉNTICO entre repeticiones.")
        elif consistente_datos:
            print("  Consistencia: Equivalencia semántica (mismos datos estructurados).")
        else:
            print("  Consistencia: INCONSISTENTE entre corridas.")

        resultados_totales.append({
            "caso_id": idx,
            "texto": caso,
            "corridas": corridas_caso,
            "consistente": consistente_datos
        })

    print("\n" + "=" * 75)
    print("TABLA RESUMEN DE LAS 6 CORRIDAS")
    print("=" * 75)
    for r in resultados_totales:
        c1 = r["corridas"][0]
        platillos_c1 = [p.get("platillo") for p in c1["parsed"]["platillos"]] if c1["parsed"] else []
        atributos_c1 = [p.get("atributos") for p in c1["parsed"]["platillos"]] if c1["parsed"] else []
        print(f"Caso {r['caso_id']}: \"{r['texto']}\"")
        print(f"  -> Platillo(s) mapeado(s): {platillos_c1}")
        print(f"  -> Atributos extraídos: {atributos_c1}")
        print(f"  -> ¿Respetó catálogo?: {'SÍ' if c1['respeta_catalogo'] else 'NO (Alucinó)'}")
        print(f"  -> Consistencia entre repeticiones: {'100%' if r['consistente'] else 'Diferencias'}")
        print("-" * 75)

if __name__ == "__main__":
    main()
