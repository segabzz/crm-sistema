import math
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.dish import Platillo
from app.models.sentiment import SentimientoPlatillo
from app.models.attribute import AtributoMencionado
from app.models.establishment_sentiment import SentimientoEstablecimiento

def wilson_score_lower_bound(positives: int, total: int, z: float = 1.96) -> float:
    """
    Calcula la cota inferior del intervalo de confianza de Wilson para proporciones binomiales (z=1.96 para 95% de confianza).
    Asegura que platillos con mayor evidencia estadística y alto índice de aprobación superen a platillos con una sola opinión.
    """
    if total <= 0:
        return 0.0

    phat = positives / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = phat + z2 / (2.0 * total)
    spread = z * math.sqrt((phat * (1.0 - phat) + z2 / (4.0 * total)) / total)
    lower_bound = (center - spread) / denominator
    return round(max(0.0, lower_bound), 4)

class RankingService:
    def calculate_ranking(self, db: Session) -> Dict[str, Any]:
        """
        Calcula el ranking ponderado bayesiano de todos los platillos con menciones,
        separando Top Platillos y Platillos en Riesgo.
        """
        # 1. Obtener todos los platillos activos
        platillos = db.query(Platillo).filter(Platillo.activo == True).all()
        platillos_map = {p.id: p for p in platillos}

        # 2. Consultar sentimientos agrupados por platillo_id (excluyendo Sin Clasificar / NULL)
        sentimientos = db.query(SentimientoPlatillo).filter(
            SentimientoPlatillo.platillo_id.isnot(None),
            SentimientoPlatillo.platillo_nombre_referenciado != "Sin Clasificar"
        ).all()

        total_evaluaciones = len(sentimientos)

        # Agrupación por platillo
        stats_platillos = defaultdict(lambda: {"positivas": 0, "negativas": 0, "neutrales": 0, "total": 0})
        for s in sentimientos:
            pid = s.platillo_id
            stats_platillos[pid]["total"] += 1
            if s.polaridad == "positivo":
                stats_platillos[pid]["positivas"] += 1
            elif s.polaridad == "negativo":
                stats_platillos[pid]["negativas"] += 1
            else:
                stats_platillos[pid]["neutrales"] += 1

        items_ranking = []
        for pid, stats in stats_platillos.items():
            dish = platillos_map.get(pid)
            if not dish:
                continue

            total = stats["total"]
            pos = stats["positivas"]
            neg = stats["negativas"]
            neu = stats["neutrales"]

            tasa_pos = round(pos / total, 3) if total > 0 else 0.0
            tasa_neg = round(neg / total, 3) if total > 0 else 0.0

            # Cota inferior pura de Wilson Score Interval (95% confianza)
            score_ponderado = wilson_score_lower_bound(positives=pos, total=total, z=1.96)

            items_ranking.append({
                "platillo_id": dish.id,
                "nombre": dish.nombre,
                "categoria": dish.categoria,
                "total_menciones": total,
                "positivas": pos,
                "negativas": neg,
                "neutrales": neu,
                "score_ponderado": score_ponderado,
                "tasa_positiva": tasa_pos,
                "tasa_negativa": tasa_neg
            })

        # Ordenar Top Platillos por score_ponderado descendente
        top_platillos = sorted(items_ranking, key=lambda x: (x["score_ponderado"], x["total_menciones"]), reverse=True)

        # Platillos en Riesgo: filtrar aquellos con al menos 1 mención negativa
        # Ordenados por tasa_negativa descendente, luego cantidad de negativas
        en_riesgo = [p for p in items_ranking if p["negativas"] > 0]
        en_riesgo = sorted(en_riesgo, key=lambda x: (x["tasa_negativa"], x["negativas"], -x["score_ponderado"]), reverse=True)

        return {
            "total_evaluaciones": total_evaluaciones,
            "top_platillos": top_platillos,
            "platillos_en_riesgo": en_riesgo
        }

    def calculate_trends(self, db: Session, dias: int = 7) -> Dict[str, Any]:
        """
        Agrega menciones y atributos a lo largo del tiempo.
        Maneja explícitamente el caso de periodos previos sin datos (retornando 'SIN_DATOS_PREVIOS').
        Excluye 'Sin Clasificar' del ranking por platillo y lo reporta por separado.
        """
        now = datetime.now(timezone.utc)
        t_reciente_inicio = now - timedelta(days=dias)
        t_previo_inicio = now - timedelta(days=2 * dias)

        # 1. Obtener platillos catalogados
        platillos = db.query(Platillo).filter(Platillo.activo == True).all()
        platillos_map = {p.id: p for p in platillos}

        # 2. Sentimientos de platillos catalogados
        sentimientos_catalogados = db.query(SentimientoPlatillo).filter(
            SentimientoPlatillo.platillo_id.isnot(None),
            SentimientoPlatillo.platillo_nombre_referenciado != "Sin Clasificar"
        ).all()

        # Agrupación temporal por platillo
        datos_por_platillo = defaultdict(lambda: {
            "recientes_scores": [],
            "previos_scores": [],
            "atributos": defaultdict(lambda: {"total": 0, "positivas": 0, "negativas": 0, "neutrales": 0, "valores": set()})
        })

        for s in sentimientos_catalogados:
            pid = s.platillo_id
            # Comparación con timezone UTC
            s_date = s.created_at
            if s_date.tzinfo is None:
                s_date = s_date.replace(tzinfo=timezone.utc)

            if s_date >= t_reciente_inicio:
                datos_por_platillo[pid]["recientes_scores"].append(s.score_numerico)
                # Atributos asociados
                for attr in s.atributos:
                    cat = attr.categoria_atributo
                    datos_por_platillo[pid]["atributos"][cat]["total"] += 1
                    datos_por_platillo[pid]["atributos"][cat]["valores"].add(attr.valor_mencionado)
                    if attr.polaridad == "positivo":
                        datos_por_platillo[pid]["atributos"][cat]["positivas"] += 1
                    elif attr.polaridad == "negativo":
                        datos_por_platillo[pid]["atributos"][cat]["negativas"] += 1
                    else:
                        datos_por_platillo[pid]["atributos"][cat]["neutrales"] += 1

            elif s_date >= t_previo_inicio and s_date < t_reciente_inicio:
                datos_por_platillo[pid]["previos_scores"].append(s.score_numerico)

        tendencias_platillos = []
        for pid, data in datos_por_platillo.items():
            dish = platillos_map.get(pid)
            if not dish:
                continue

            recientes = data["recientes_scores"]
            previos = data["previos_scores"]

            menciones_recientes = len(recientes)
            menciones_previas = len(previos)

            score_reciente = round(sum(recientes) / menciones_recientes, 3) if menciones_recientes > 0 else None

            # MODIFICACIÓN 1: Manejo explícito de 0 menciones en periodo previo
            if menciones_previas == 0:
                score_previo = None
                cambio_polaridad = None
                tendencia = "SIN_DATOS_PREVIOS"
            else:
                score_previo = round(sum(previos) / menciones_previas, 3)
                if score_reciente is not None and score_previo is not None:
                    cambio_polaridad = round(score_reciente - score_previo, 3)
                    if cambio_polaridad >= 0.15:
                        tendencia = "MEJORANDO"
                    elif cambio_polaridad <= -0.15:
                        tendencia = "EMPEORANDO"
                    else:
                        tendencia = "ESTABLE"
                else:
                    cambio_polaridad = None
                    tendencia = "SIN_DATOS_PREVIOS"

            # Formatear atributos destacados del platillo
            atributos_formateados = []
            for cat_name, a_info in data["atributos"].items():
                atributos_formateados.append({
                    "categoria_atributo": cat_name,
                    "total_menciones": a_info["total"],
                    "positivas": a_info["positivas"],
                    "negativas": a_info["negativas"],
                    "neutrales": a_info["neutrales"],
                    "ejemplos_valores": list(a_info["valores"])[:4]
                })
            atributos_formateados.sort(key=lambda x: x["total_menciones"], reverse=True)

            tendencias_platillos.append({
                "platillo_id": dish.id,
                "nombre": dish.nombre,
                "menciones_periodo_reciente": menciones_recientes,
                "score_polaridad_reciente": score_reciente,
                "menciones_periodo_previo": menciones_previas,
                "score_polaridad_previo": score_previo,
                "cambio_polaridad": cambio_polaridad,
                "tendencia": tendencia,
                "atributos_destacados": atributos_formateados
            })

        tendencias_platillos.sort(key=lambda x: x["menciones_periodo_reciente"], reverse=True)

        # 3. Atributos más mencionados globalmente (todos los platillos)
        todos_atributos = db.query(AtributoMencionado).join(SentimientoPlatillo).filter(
            SentimientoPlatillo.platillo_id.isnot(None),
            SentimientoPlatillo.platillo_nombre_referenciado != "Sin Clasificar"
        ).all()

        agrupacion_global = defaultdict(lambda: {"total": 0, "positivas": 0, "negativas": 0, "neutrales": 0, "valores": set()})
        for attr in todos_atributos:
            cat = attr.categoria_atributo
            agrupacion_global[cat]["total"] += 1
            agrupacion_global[cat]["valores"].add(attr.valor_mencionado)
            if attr.polaridad == "positivo":
                agrupacion_global[cat]["positivas"] += 1
            elif attr.polaridad == "negativo":
                agrupacion_global[cat]["negativas"] += 1
            else:
                agrupacion_global[cat]["neutrales"] += 1

        atributos_globales = []
        for cat_name, a_info in agrupacion_global.items():
            atributos_globales.append({
                "categoria_atributo": cat_name,
                "total_menciones": a_info["total"],
                "positivas": a_info["positivas"],
                "negativas": a_info["negativas"],
                "neutrales": a_info["neutrales"],
                "ejemplos_valores": list(a_info["valores"])[:5]
            })
        atributos_globales.sort(key=lambda x: x["total_menciones"], reverse=True)

        # 4. Sección separada: Menciones Sin Clasificar
        sentimientos_sin_clasificar = db.query(SentimientoPlatillo).filter(
            (SentimientoPlatillo.platillo_id.is_(None)) | (SentimientoPlatillo.platillo_nombre_referenciado == "Sin Clasificar")
        ).all()

        tot_unclass = len(sentimientos_sin_clasificar)
        pos_unclass = sum(1 for s in sentimientos_sin_clasificar if s.polaridad == "positivo")
        neg_unclass = sum(1 for s in sentimientos_sin_clasificar if s.polaridad == "negativo")
        neu_unclass = sum(1 for s in sentimientos_sin_clasificar if s.polaridad == "neutral")

        attrs_unclass_map = defaultdict(lambda: {"total": 0, "positivas": 0, "negativas": 0, "neutrales": 0, "valores": set()})
        for s in sentimientos_sin_clasificar:
            for attr in s.atributos:
                cat = attr.categoria_atributo
                attrs_unclass_map[cat]["total"] += 1
                attrs_unclass_map[cat]["valores"].add(attr.valor_mencionado)
                if attr.polaridad == "positivo":
                    attrs_unclass_map[cat]["positivas"] += 1
                elif attr.polaridad == "negativo":
                    attrs_unclass_map[cat]["negativas"] += 1
                else:
                    attrs_unclass_map[cat]["neutrales"] += 1

        attrs_unclass_list = []
        for cat_name, a_info in attrs_unclass_map.items():
            attrs_unclass_list.append({
                "categoria_atributo": cat_name,
                "total_menciones": a_info["total"],
                "positivas": a_info["positivas"],
                "negativas": a_info["negativas"],
                "neutrales": a_info["neutrales"],
                "ejemplos_valores": list(a_info["valores"])[:5]
            })

        menciones_sin_clasificar_summary = {
            "total_menciones": tot_unclass,
            "positivas": pos_unclass,
            "negativas": neg_unclass,
            "neutrales": neu_unclass,
            "atributos_asociados": attrs_unclass_list
        }

        # 5. Sección separada: Sentimientos del Establecimiento (servicio, ambiente, limpieza, tiempo_espera)
        sentimientos_est = db.query(SentimientoEstablecimiento).all()
        tot_est = len(sentimientos_est)
        pos_est = sum(1 for s in sentimientos_est if s.polaridad == "positivo")
        neg_est = sum(1 for s in sentimientos_est if s.polaridad == "negativo")
        neu_est = sum(1 for s in sentimientos_est if s.polaridad == "neutral")

        est_cat_map = defaultdict(lambda: {"total": 0, "positivas": 0, "negativas": 0, "neutrales": 0, "valores": set()})
        for s in sentimientos_est:
            cat = s.categoria
            est_cat_map[cat]["total"] += 1
            if s.valor_mencionado:
                est_cat_map[cat]["valores"].add(s.valor_mencionado)
            if s.polaridad == "positivo":
                est_cat_map[cat]["positivas"] += 1
            elif s.polaridad == "negativo":
                est_cat_map[cat]["negativas"] += 1
            else:
                est_cat_map[cat]["neutrales"] += 1

        est_cat_list = []
        for cat_name, a_info in est_cat_map.items():
            est_cat_list.append({
                "categoria_atributo": cat_name,
                "total_menciones": a_info["total"],
                "positivas": a_info["positivas"],
                "negativas": a_info["negativas"],
                "neutrales": a_info["neutrales"],
                "ejemplos_valores": list(a_info["valores"])[:5]
            })
        est_cat_list.sort(key=lambda x: x["total_menciones"], reverse=True)

        sentimientos_establecimiento_summary = {
            "total_menciones": tot_est,
            "positivas": pos_est,
            "negativas": neg_est,
            "neutrales": neu_est,
            "categorias": est_cat_list
        }

        return {
            "periodo_dias": dias,
            "fecha_corte": now.isoformat(),
            "tendencias_por_platillo": tendencias_platillos,
            "atributos_mas_mencionados_global": atributos_globales,
            "menciones_sin_clasificar": menciones_sin_clasificar_summary,
            "sentimientos_establecimiento": sentimientos_establecimiento_summary
        }

ranking_service = RankingService()
