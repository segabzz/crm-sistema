import pytest
from app.services.nlp_service import (
    nlp_service,
    PlatilloExtraidoLLM,
    PolaridadEnum,
    _normalize_text
)

CATALOGO_PRUEBA = {
    "Tacos de Res Braseada",
    "Ribeye a la Parrilla",
    "Sopa Azteca",
    "Guacamole Rústico"
}

def test_normalize_text():
    """Verifica que remueva acentos y estandarice a minúsculas."""
    assert _normalize_text("Sopa Azteca Fría") == "sopa azteca fria"
    assert _normalize_text("Guacamole RÚSTICO") == "guacamole rustico"

def test_guardrail_catalog_valid_dish():
    """Un platillo existente en catálogo no debe ser alterado."""
    item = PlatilloExtraidoLLM(
        texto_mencionado="la sopa azteca",
        platillo_sugerido="Sopa Azteca",
        polaridad=PolaridadEnum.positivo,
        atributos=["deliciosa"]
    )
    final, reasignado, motivo = nlp_service._apply_guardrails(
        item,
        texto_completo="la sopa azteca estuvo deliciosa",
        catalogo_oficial_set=CATALOGO_PRUEBA
    )
    assert final == "Sopa Azteca"
    assert not reasignado
    assert motivo is None

def test_guardrail_catalog_hallucinated_dish():
    """Si el LLM inventa un platillo fuera de catálogo, debe ser reasignado a Sin Clasificar."""
    item = PlatilloExtraidoLLM(
        texto_mencionado="la pizza de peperoni",
        platillo_sugerido="Pizza Pepperoni",
        polaridad=PolaridadEnum.positivo,
        atributos=[]
    )
    final, reasignado, motivo = nlp_service._apply_guardrails(
        item,
        texto_completo="la pizza de peperoni estuvo buena",
        catalogo_oficial_set=CATALOGO_PRUEBA
    )
    assert final == "Sin Clasificar"
    assert reasignado
    assert "no pertenece al catálogo" in motivo

def test_guardrail_negation_exclusion():
    """Si hay cláusula de exclusión ('no venían en el menú'), debe reasignar a Sin Clasificar."""
    item = PlatilloExtraidoLLM(
        texto_mencionado="dos tacos",
        platillo_sugerido="Tacos de Res Braseada",
        polaridad=PolaridadEnum.negativo,
        atributos=["fríos"]
    )
    final, reasignado, motivo = nlp_service._apply_guardrails(
        item,
        texto_completo="pedí dos tacos que no venían en el menú de especiales y además estaban fríos",
        catalogo_oficial_set=CATALOGO_PRUEBA
    )
    assert final == "Sin Clasificar"
    assert reasignado
    assert "[Guardrail]" not in motivo # El prefijo [Guardrail] se agrega en reviews.py
    assert "no venian" in _normalize_text(motivo)

def test_attribute_categories():
    """Verifica que la heurística clasifique categorías esperadas."""
    assert nlp_service._infer_attribute_category("muy fría") == "temperatura"
    assert nlp_service._infer_attribute_category("caliente") == "temperatura"
    assert nlp_service._infer_attribute_category("demasiado salado") == "sabor"
    assert nlp_service._infer_attribute_category("porción chica") == "porcion"
    assert nlp_service._infer_attribute_category("tardó mucho") == "general"
    assert nlp_service._infer_attribute_category("poco tiempo") == "general"
    assert nlp_service._infer_attribute_category("carne dura") == "textura"
    assert nlp_service._infer_attribute_category("muy caro") == "precio_calidad"
    assert nlp_service._infer_attribute_category("montaje bonito") == "presentacion"
