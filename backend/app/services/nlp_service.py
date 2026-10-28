import re
import unicodedata
from enum import Enum
from typing import List, Optional, Tuple, Iterator
from pydantic import BaseModel, Field, ValidationError
import ollama
from app.core.config import settings

def _normalize_text(text: str) -> str:
    """Remueve acentos y pasa a minúsculas para comparaciones semánticas robustas."""
    text_nfd = unicodedata.normalize('NFD', text.lower())
    return ''.join(c for c in text_nfd if unicodedata.category(c) != 'Mn')

class PolaridadEnum(str, Enum):
    positivo = "positivo"
    neutral = "neutral"
    negativo = "negativo"

class CategoriaEstablecimientoEnum(str, Enum):
    servicio = "servicio"
    ambiente = "ambiente"
    limpieza = "limpieza"
    tiempo_espera = "tiempo_espera"

class PlatilloExtraidoLLM(BaseModel):
    texto_mencionado: str = Field(
        description="Frase o fragmento textual literal donde el comensal menciona o describe el platillo"
    )
    platillo_sugerido: str = Field(
        description="Nombre EXACTO de uno de los platillos del catálogo oficial, o 'Sin Clasificar' si menciona otra comida fuera del catálogo"
    )
    polaridad: PolaridadEnum = Field(
        description="Polaridad general de la opinión sobre este platillo: positivo, neutral o negativo"
    )
    atributos: List[str] = Field(
        default_factory=list,
        description="Lista de cualidades, adjetivos o quejas mencionadas del platillo (ej: ['fríos', 'porción muy chica'], ['exquisito'])"
    )

class AspectoEstablecimientoLLM(BaseModel):
    categoria: CategoriaEstablecimientoEnum = Field(
        description="Categoría del aspecto del establecimiento: 'servicio', 'ambiente', 'limpieza' o 'tiempo_espera'"
    )
    texto_mencionado: str = Field(
        description="Fragmento literal donde el comensal menciona este aspecto del restaurante"
    )
    polaridad: PolaridadEnum = Field(
        description="Polaridad de la opinión sobre este aspecto: positivo, neutral o negativo"
    )
    valor_mencionado: str = Field(
        description="Cualidad o queja específica resumida (ej: 'excelente atención', 'muy limpio el lugar', 'música agradable')"
    )

class AnalisisResenaLLM(BaseModel):
    platillos: List[PlatilloExtraidoLLM] = Field(
        default_factory=list,
        description="Lista de menciones de platillos o alimentos encontradas en la reseña. Vacía [] si no se menciona comida."
    )
    establecimiento: List[AspectoEstablecimientoLLM] = Field(
        default_factory=list,
        description="Lista de opiniones sobre el establecimiento (servicio, ambiente, limpieza, tiempo_espera). Vacía [] si solo se habla de comida."
    )

class NLPResultItem:
    def __init__(
        self,
        texto_mencionado: str,
        platillo_final: str,
        platillo_original_llm: str,
        polaridad: str,
        score_numerico: float,
        atributos: List[dict],
        fue_reasignado_por_guardrail: bool,
        motivo_guardrail: Optional[str] = None
    ):
        self.texto_mencionado = texto_mencionado
        self.platillo_final = platillo_final
        self.platillo_original_llm = platillo_original_llm
        self.polaridad = polaridad
        self.score_numerico = score_numerico
        self.atributos = atributos
        self.fue_reasignado_por_guardrail = fue_reasignado_por_guardrail
        self.motivo_guardrail = motivo_guardrail

class NLPEstablishmentItem:
    def __init__(
        self,
        categoria: str,
        texto_mencionado: str,
        polaridad: str,
        score_numerico: float,
        valor_mencionado: str
    ):
        self.categoria = categoria
        self.texto_mencionado = texto_mencionado
        self.polaridad = polaridad
        self.score_numerico = score_numerico
        self.valor_mencionado = valor_mencionado

class NLPAnalysisResult:
    """
    Contenedor de resultados NLP que expone .platillos y .establecimiento,
    manteniendo compatibilidad iterable con List[NLPResultItem].
    """
    def __init__(
        self,
        platillos: List[NLPResultItem],
        establecimiento: Optional[List[NLPEstablishmentItem]] = None
    ):
        self.platillos = platillos
        self.establecimiento = establecimiento if establecimiento is not None else []

    def __iter__(self) -> Iterator[NLPResultItem]:
        return iter(self.platillos)

    def __len__(self) -> int:
        return len(self.platillos)

    def __getitem__(self, index: int) -> NLPResultItem:
        return self.platillos[index]

    def __bool__(self) -> bool:
        return bool(self.platillos or self.establecimiento)

class NLPServiceError(Exception):
    """Excepción lanzada cuando Ollama no responde o falla la validación del esquema."""
    pass

class NLPService:
    def __init__(self):
        self.model_name = settings.OLLAMA_MODEL
        self.negation_keywords = settings.GUARDRAIL_NEGATION_KEYWORDS
        self.client = ollama.Client(host=settings.OLLAMA_BASE_URL)

    def _infer_attribute_category(self, valor: str) -> str:
        """Heurística rápida para clasificar el tipo de atributo con normalización de acentos."""
        val = _normalize_text(valor)
        if any(w in val for w in ["frio", "fria", "frios", "frias", "caliente", "calientes", "tibio", "tibia", "helado", "temperatura"]):
            return "temperatura"
        if any(w in val for w in ["salado", "dulce", "acido", "amargo", "rico", "delicioso", "deliciosa", "exquisito", "desabrido", "sabor", "bueno", "malo"]):
            return "sabor"
        if any(w in val for w in ["porcion", "chica", "chico", "pequena", "pequeno", "grande", "abundante", "escaso", "escasa"]):
            return "porcion"
        if any(w in val for w in ["dura", "duro", "suave", "tierno", "crujiente", "correoso", "textura", "aguado", "grasoso"]):
            return "textura"
        if any(w in val for w in ["caro", "barato", "precio", "costo", "calidad-precio"]):
            return "precio_calidad"
        if any(w in val for w in ["presentacion", "aspecto", "montaje", "bonito", "feo"]):
            return "presentacion"
        return "general"

    def _apply_guardrails(
        self,
        item: PlatilloExtraidoLLM,
        texto_completo: str,
        catalogo_oficial_set: set[str]
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Aplica los dos guardrails deterministas en Python:
        1. Valida pertenencia estricta al catálogo o 'Sin Clasificar'.
        2. Reasigna a 'Sin Clasificar' si detecta cláusulas de exclusión/duda
           en la mención específica de ese platillo.
        """
        platillo_sugerido = item.platillo_sugerido.strip()
        mencion_norm = _normalize_text(item.texto_mencionado)
        completo_norm = _normalize_text(texto_completo)

        # Guardrail 1: Pertenencia al catálogo
        if platillo_sugerido not in catalogo_oficial_set and platillo_sugerido != "Sin Clasificar":
            return (
                "Sin Clasificar",
                True,
                f"El platillo sugerido '{platillo_sugerido}' no pertenece al catálogo oficial."
            )

        # Guardrail 2: Detección de negación/exclusión en la mención directa o en su cláusula contextual
        clausulas = re.split(r'[,.;\n]|\bpero\b|\baunque\b|\bsin embargo\b|\bademas\b', completo_norm)
        palabras_mencion = [w for w in mencion_norm.split() if len(w) > 3]

        for kw in self.negation_keywords:
            kw_norm = _normalize_text(kw)
            pattern = r'\b' + re.escape(kw_norm) + r'\b'

            # 1. Coincidencia directa en texto_mencionado
            if re.search(pattern, mencion_norm):
                return (
                    "Sin Clasificar",
                    True,
                    f"Detectada cláusula de exclusión o duda ('{kw}') en '{item.texto_mencionado}'. Reasignado a 'Sin Clasificar'."
                )

            # 2. Coincidencia en la cláusula contextual donde se nombra este platillo
            for clausula in clausulas:
                if re.search(pattern, clausula):
                    if any(w in clausula for w in palabras_mencion) or any(w in clausula for w in platillo_sugerido.lower().split() if len(w) > 3):
                        return (
                            "Sin Clasificar",
                            True,
                            f"Detectada cláusula de exclusión o duda ('{kw}') asociada a '{item.texto_mencionado}'. Reasignado a 'Sin Clasificar'."
                        )

        return platillo_sugerido, False, None

    def _is_mentioned_in_text(self, fragmento: str, texto_completo: str) -> bool:
        """Verifica que el fragmento extraído tenga presencia léxica real en el texto analizado."""
        frag_norm = _normalize_text(fragmento)
        comp_norm = _normalize_text(texto_completo)
        words = [w for w in re.findall(r'[a-z0-9]+', frag_norm) if len(w) >= 4]
        if not words:
            return bool(frag_norm and frag_norm in comp_norm)
        return any(w in comp_norm for w in words)

    def analyze_review(
        self,
        texto: str,
        catalogo_oficial: List[str]
    ) -> NLPAnalysisResult:
        """
        Analiza una reseña contra el catálogo oficial usando Ollama (llama3.2)
        extrayendo por separado menciones de platillos y sentimientos del establecimiento,
        y aplica la capa de guardrails deterministas en Python sobre los platillos.
        """
        catalogo_set = set(catalogo_oficial)
        catalogo_formateado = "\n".join([f'- "{p}"' for p in catalogo_oficial])

        prompt = f"""Eres un extractor de reseñas gastronómicas para un restaurante.
Dispones ÚNICAMENTE del siguiente CATÁLOGO OFICIAL DE PLATILLOS:
{catalogo_formateado}

REGLAS ESTRICTAS PARA 'platillos' (COMIDA Y BEBIDA):
1. 'platillo_sugerido': Debe ser EXACTAMENTE uno de los nombres del catálogo oficial si hay coincidencia semántica clara.
   - Si se menciona un platillo o comida específica que NO corresponde a ninguno de la lista (ej. pizza, sushi), asigna obligatoriamente "Sin Clasificar".
   - NO inventes ningún nombre fuera del catálogo oficial ni de "Sin Clasificar".
   - Si NO se menciona comida ni platillos (por ejemplo, si solo hablan del servicio, limpieza o ambiente), devuelve 'platillos': [] (lista vacía). NUNCA uses "Sin Clasificar" para opiniones de servicio, ambiente, limpieza o espera general.
2. 'texto_mencionado': El nombre o fragmento textual corto donde se menciona ese platillo (ej: 'la sopa azteca', 'los tacos de barbacoa', 'el ribeye a la parrilla'). NO pongas la reseña entera.
3. 'polaridad': 'positivo', 'neutral' o 'negativo'.
4. 'atributos': Lista de strings con las cualidades, temperaturas, porciones o quejas de ese platillo (ej: ["fría"], ["dura", "porción chica"]). Si no hay atributos, devuelve [].

REGLAS ESTRICTAS PARA 'establecimiento' (RESTAURANTE EN GENERAL):
Extrae en 'establecimiento' únicamente opiniones sobre el restaurante en estas 4 categorías:
- "servicio": atención de meseros, amabilidad, trato del personal.
- "ambiente": música, decoración, ruido, comodidad, iluminación, atmósfera del lugar.
- "limpieza": higiene del local, mesas, baños, cubiertos.
- "tiempo_espera": "tiempo_espera" es exclusivamente para demoras generales (conseguir mesa, traer la cuenta, atención general) — NUNCA uses esta categoría para la demora de un platillo específico; esa queja se queda únicamente como atributo del platillo en cuestión, para evitar reportarla por duplicado.
Si la reseña solo habla de platillos y no menciona servicio, ambiente, limpieza ni tiempo_espera general, devuelve 'establecimiento': [].

Texto a analizar:
\"{texto}\""""

        schema = AnalisisResenaLLM.model_json_schema()

        try:
            res = self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                format=schema,
                options={"temperature": 0.0, "seed": 42}
            )
            raw_content = res.message.content.strip()
            parsed = AnalisisResenaLLM.model_validate_json(raw_content)
        except Exception as e:
            print(f"[NLPService ERROR] Falló la llamada o validación de Ollama: {e}")
            raise NLPServiceError(f"Error en Ollama/LLM: {e}") from e

        textos_est_norm = {_normalize_text(e.texto_mencionado) for e in parsed.establecimiento}
        resultados_platillos: List[NLPResultItem] = []

        for item in parsed.platillos:
            # Filtro determinista 1: Verificar que la mención exista literalmente en el texto original
            if not self._is_mentioned_in_text(item.texto_mencionado, texto):
                continue

            mencion_norm = _normalize_text(item.texto_mencionado)
            platillo_final, fue_reasignado, motivo = self._apply_guardrails(item, texto, catalogo_set)

            # Filtro determinista 2: Si quedó 'Sin Clasificar' y el fragmento exacto ya fue extraído
            # como aspecto de 'establecimiento' (ej. 'el ambiente del restaurante'), no duplicarlo en platillos
            if platillo_final == "Sin Clasificar" and mencion_norm in textos_est_norm:
                continue

            # Cálculo de score numérico
            if item.polaridad == PolaridadEnum.positivo:
                score = 1.0
            elif item.polaridad == PolaridadEnum.negativo:
                score = -1.0
            else:
                score = 0.0

            # Procesamiento de atributos
            atributos_procesados = []
            for attr_str in item.atributos:
                categoria = self._infer_attribute_category(attr_str)
                atributos_procesados.append({
                    "categoria": categoria,
                    "valor": attr_str,
                    "polaridad": item.polaridad.value
                })

            resultados_platillos.append(NLPResultItem(
                texto_mencionado=item.texto_mencionado,
                platillo_final=platillo_final,
                platillo_original_llm=item.platillo_sugerido,
                polaridad=item.polaridad.value,
                score_numerico=score,
                atributos=atributos_procesados,
                fue_reasignado_por_guardrail=fue_reasignado,
                motivo_guardrail=motivo
            ))

        # Recolectar los atributos ya adjudicados a platillos en esta reseña para evitar duplicarlos en establecimiento
        atributos_platillos_norm = [
            _normalize_text(attr["valor"])
            for p in resultados_platillos
            for attr in p.atributos
            if len(_normalize_text(attr["valor"])) >= 4
        ]

        resultados_establecimiento: List[NLPEstablishmentItem] = []
        for est in parsed.establecimiento:
            if not self._is_mentioned_in_text(est.texto_mencionado, texto):
                continue

            est_mencion_norm = _normalize_text(est.texto_mencionado)

            # Filtro determinista 3 (Ajuste 2 quirúrgico): Si la reseña tiene platillos y este fragmento
            # duplica un atributo ya extraído en un platillo (ej. 'tardó mucho', 'frío', '40 minutos')
            # o habla de que el platillo tardó en 'salir', se queda únicamente en el platillo.
            # Nota (limitación conocida): el patrón \bsalir\b|\bsalio\b es ligeramente amplio y en teoría
            # podría descartar una mención de establecimiento no relacionada a demora de platillo si usa ese verbo.
            if resultados_platillos:
                repite_atributo_platillo = any(
                    attr_norm in est_mencion_norm or est_mencion_norm in attr_norm
                    for attr_norm in atributos_platillos_norm
                )
                habla_de_salir_platillo = bool(re.search(r'\bsalir\b|\bsalio\b', est_mencion_norm))
                if repite_atributo_platillo or habla_de_salir_platillo:
                    continue

            if est.polaridad == PolaridadEnum.positivo:
                est_score = 1.0
            elif est.polaridad == PolaridadEnum.negativo:
                est_score = -1.0
            else:
                est_score = 0.0

            valor_limpio = est.texto_mencionado.strip()

            resultados_establecimiento.append(NLPEstablishmentItem(
                categoria=est.categoria.value,
                texto_mencionado=est.texto_mencionado.strip(),
                polaridad=est.polaridad.value,
                score_numerico=est_score,
                valor_mencionado=valor_limpio
            ))

        return NLPAnalysisResult(
            platillos=resultados_platillos,
            establecimiento=resultados_establecimiento
        )

nlp_service = NLPService()
