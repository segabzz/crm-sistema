import React, { useState, useEffect, useCallback } from 'react';
import {
  RefreshCw,
  TrendingUp,
  Award,
  AlertTriangle,
  Layers,
  Sparkles,
  Building2,
} from 'lucide-react';
import { api } from '../services/api';
import type { RankingResponse, TrendsResponse } from '../types';
import { RankingTable } from '../components/RankingTable';
import { RankingChart } from '../components/RankingChart';
import { AttributesChart } from '../components/AttributesChart';
import { RiskAlerts } from '../components/RiskAlerts';

export const DashboardView: React.FC = () => {
  const [rankingData, setRankingData] = useState<RankingResponse | null>(null);
  const [trendsData, setTrendsData] = useState<TrendsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [rankingRes, trendsRes] = await Promise.all([
        api.getRanking(),
        api.getTrends(7),
      ]);
      setRankingData(rankingRes);
      setTrendsData(trendsRes);
    } catch (err: any) {
      console.error('Error al cargar datos del dashboard:', err);
      setError(err.message || 'No se pudieron cargar los datos analíticos del backend.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Métricas calculadas para tarjetas KPI
  const topDish = rankingData?.top_platillos?.[0];
  const riskDishesCount = rankingData?.platillos_en_riesgo?.length || 0;
  const totalMenciones = rankingData?.top_platillos?.reduce(
    (acc, item) => acc + item.total_menciones,
    0
  ) || 0;

  const estSummary = trendsData?.sentimientos_establecimiento;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Cabecera del Dashboard */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Métricas Operativas & Wilson Score</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Dashboard de Satisfacción Gastronómica
          </h1>
          <p className="text-xs text-slate-500">
            Leaderboard estadísticamente confiable (Lower Bound 95%), atributos en cocina y percepción del establecimiento
          </p>
        </div>

        <button
          onClick={loadDashboardData}
          disabled={isLoading}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-2xs transition-all disabled:opacity-50 cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-indigo-600' : ''}`} />
          <span>Actualizar Analíticas</span>
        </button>
      </div>

      {/* Manejo de Error */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={loadDashboardData}
            className="underline font-bold hover:text-rose-900 ml-4 cursor-pointer"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Tarjetas KPI Superiores */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Evaluaciones */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">
              Total Menciones
            </span>
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-black text-slate-900">
            {isLoading ? '...' : totalMenciones}
          </div>
          <p className="text-[11px] text-slate-400">
            {rankingData?.total_evaluaciones || 0} evaluaciones de platillos
          </p>
        </div>

        {/* KPI 2: Platillo Líder */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">
              Platillo Estrella
            </span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-xl">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="text-base font-extrabold text-slate-900 truncate">
            {isLoading ? '...' : topDish ? topDish.nombre : 'Sin datos'}
          </div>
          <p className="text-[11px] text-slate-400">
            {topDish
              ? `Wilson: ${topDish.score_ponderado.toFixed(4)} (${(topDish.tasa_positiva * 100).toFixed(0)}% pos)`
              : 'Se requieren más reseñas'}
          </p>
        </div>

        {/* KPI 3: Platillos en Riesgo */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">
              En Riesgo
            </span>
            <div
              className={`p-2 rounded-xl ${
                riskDishesCount > 0
                  ? 'bg-rose-50 text-rose-600'
                  : 'bg-emerald-50 text-emerald-600'
              }`}
            >
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div
            className={`text-2xl font-black ${
              riskDishesCount > 0 ? 'text-rose-600' : 'text-emerald-600'
            }`}
          >
            {isLoading ? '...' : riskDishesCount}
          </div>
          <p className="text-[11px] text-slate-400">
            {riskDishesCount > 0
              ? 'Requieren revisión en cocina'
              : 'Menú en niveles saludables'}
          </p>
        </div>

        {/* KPI 4: Confiabilidad Wilson */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">
              Algoritmo de Ranking
            </span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-base font-extrabold text-slate-900">
            Wilson Bound
          </div>
          <p className="text-[11px] text-slate-400">
            Penaliza muestras bajas (z = 1.96)
          </p>
        </div>
      </div>

      {/* Alerta de Platillos en Riesgo */}
      {rankingData && rankingData.platillos_en_riesgo.length > 0 && (
        <RiskAlerts platillosEnRiesgo={rankingData.platillos_en_riesgo} />
      )}

      {/* Gráficas Recharts (2 columnas) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RankingChart ranking={rankingData?.top_platillos || []} />
        <AttributesChart trends={trendsData} />
      </div>

      {/* Nueva Sección Separada: Sentimientos del Establecimiento */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-violet-50 text-violet-600 rounded-xl">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">
                Sentimiento del Establecimiento (Separado de Platillos)
              </h2>
              <p className="text-xs text-slate-500">
                Menciones operativas sobre servicio, ambiente, limpieza y tiempo de espera general
              </p>
            </div>
          </div>

          {estSummary && (
            <div className="flex items-center space-x-2 text-xs font-bold">
              <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700">
                Total: {estSummary.total_menciones}
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700">
                +{estSummary.positivas} Pos
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-rose-50 text-rose-700">
                -{estSummary.negativas} Neg
              </span>
            </div>
          )}
        </div>

        {!estSummary || estSummary.categorias.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            Aún no hay menciones registradas sobre servicio, ambiente, limpieza o tiempo de espera general.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {estSummary.categorias.map((cat) => (
              <div
                key={cat.categoria_atributo}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-extrabold uppercase tracking-wider text-violet-900 bg-violet-100 px-2.5 py-0.5 rounded">
                    {cat.categoria_atributo}
                  </span>
                  <span className="text-xs font-bold text-slate-600">
                    {cat.total_menciones} menc.
                  </span>
                </div>

                <div className="flex items-center space-x-2 text-[11px] font-bold">
                  <span className="text-emerald-700">{cat.positivas} pos</span>
                  <span className="text-slate-300">&bull;</span>
                  <span className="text-rose-600">{cat.negativas} neg</span>
                  <span className="text-slate-300">&bull;</span>
                  <span className="text-slate-500">{cat.neutrales} neu</span>
                </div>

                {cat.ejemplos_valores.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {cat.ejemplos_valores.map((ej, i) => (
                      <span
                        key={i}
                        className="text-[10px] px-2 py-0.5 bg-white border border-slate-200 rounded text-slate-600"
                      >
                        "{ej}"
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tabla Completa del Leaderboard */}
      <RankingTable ranking={rankingData?.top_platillos || []} />
    </div>
  );
};
