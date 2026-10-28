import React from 'react';
import { AlertOctagon, TrendingDown, ThumbsDown } from 'lucide-react';
import type { DishRankingItem } from '../types';

interface RiskAlertsProps {
  platillosEnRiesgo: DishRankingItem[];
}

export const RiskAlerts: React.FC<RiskAlertsProps> = ({ platillosEnRiesgo }) => {
  if (!platillosEnRiesgo || platillosEnRiesgo.length === 0) {
    return (
      <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 flex items-center space-x-3 text-emerald-800">
        <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
          <span className="text-sm font-bold">✓</span>
        </div>
        <div>
          <h4 className="text-sm font-bold">Sin Platillos en Riesgo</h4>
          <p className="text-xs text-emerald-700">
            Ningún platillo supera el umbral crítico de menciones negativas actualmente.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-rose-50 border border-rose-200 rounded-2xl p-5 space-y-4">
      <div className="flex items-center space-x-2.5 text-rose-800">
        <AlertOctagon className="w-5 h-5 text-rose-600 flex-shrink-0" />
        <h3 className="text-sm font-bold uppercase tracking-wider">
          Alerta Operativa: Platillos en Riesgo ({platillosEnRiesgo.length})
        </h3>
      </div>
      <p className="text-xs text-rose-700 leading-relaxed">
        Platillos con alta concentración de valoraciones negativas o quejas recurrentes de atributos.
        Requieren atención inmediata de cocina o ajuste de receta.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {platillosEnRiesgo.map((dish) => (
          <div
            key={dish.platillo_id}
            className="bg-white border border-rose-200 rounded-xl p-4 shadow-2xs space-y-2.5"
          >
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-slate-900 truncate">
                {dish.nombre}
              </span>
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 bg-rose-100 text-rose-700 rounded-md">
                {(dish.tasa_negativa * 100).toFixed(0)}% Negativo
              </span>
            </div>

            <div className="flex items-center space-x-4 text-xs text-slate-600">
              <span className="flex items-center space-x-1">
                <ThumbsDown className="w-3.5 h-3.5 text-rose-500" />
                <span>{dish.negativas} quejas</span>
              </span>
              <span className="flex items-center space-x-1">
                <TrendingDown className="w-3.5 h-3.5 text-amber-500" />
                <span>Wilson: {dish.score_ponderado.toFixed(4)}</span>
              </span>
            </div>

            {/* Barra de proporción negativa */}
            <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden flex">
              <div
                className="bg-rose-500 h-full"
                style={{ width: `${(dish.tasa_negativa * 100).toFixed(0)}%` }}
              />
              <div
                className="bg-emerald-500 h-full"
                style={{ width: `${(dish.tasa_positiva * 100).toFixed(0)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
