import React from 'react';
import { Award, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import type { DishRankingItem } from '../types';

interface RankingTableProps {
  ranking: DishRankingItem[];
}

export const RankingTable: React.FC<RankingTableProps> = ({ ranking }) => {
  if (!ranking || ranking.length === 0) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white border border-slate-200 rounded-2xl text-xs">
        No hay datos de ranking disponibles en este momento.
      </div>
    );
  }

  const getRankBadge = (index: number) => {
    if (index === 0) {
      return (
        <span className="w-6 h-6 rounded-full bg-amber-100 text-amber-700 font-bold text-xs flex items-center justify-center border border-amber-300">
          🥇
        </span>
      );
    }
    if (index === 1) {
      return (
        <span className="w-6 h-6 rounded-full bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center border border-slate-300">
          🥈
        </span>
      );
    }
    if (index === 2) {
      return (
        <span className="w-6 h-6 rounded-full bg-amber-700/10 text-amber-900 font-bold text-xs flex items-center justify-center border border-amber-700/20">
          🥉
        </span>
      );
    }
    return (
      <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-600 font-bold text-xs flex items-center justify-center">
        {index + 1}
      </span>
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Award className="w-5 h-5 text-indigo-600" />
          <h3 className="text-base font-bold text-slate-900">
            Leaderboard de Platillos (Wilson Score)
          </h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          Intervalo de Confianza 95% (Lower Bound)
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-200/60">
              <th className="py-3 px-4 w-12 text-center">Pos</th>
              <th className="py-3 px-4">Platillo</th>
              <th className="py-3 px-4 text-center">Menciones</th>
              <th className="py-3 px-4 text-center">Desglose (+ / - / =)</th>
              <th className="py-3 px-4">Balance de Satisfacción</th>
              <th className="py-3 px-4 text-right">Wilson Score</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs">
            {ranking.map((dish, idx) => {
              const posPercent = Math.round(dish.tasa_positiva * 100);
              const negPercent = Math.round(dish.tasa_negativa * 100);

              return (
                <tr
                  key={dish.platillo_id}
                  className="hover:bg-slate-50/70 transition-colors"
                >
                  <td className="py-3.5 px-4 text-center">
                    <div className="flex justify-center">{getRankBadge(idx)}</div>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="font-bold text-slate-900">{dish.nombre}</div>
                    <span className="inline-block text-[10px] text-slate-500 font-medium bg-slate-100 px-1.5 py-0.5 rounded mt-0.5">
                      {dish.categoria}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center">
                    <span className="font-bold text-slate-800 bg-slate-100 px-2.5 py-1 rounded-full text-xs">
                      {dish.total_menciones}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center justify-center space-x-2 text-[11px] font-semibold">
                      <span className="inline-flex items-center text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                        <ThumbsUp className="w-3 h-3 mr-0.5" />
                        {dish.positivas}
                      </span>
                      <span className="inline-flex items-center text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded">
                        <ThumbsDown className="w-3 h-3 mr-0.5" />
                        {dish.negativas}
                      </span>
                      <span className="inline-flex items-center text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        <Minus className="w-3 h-3 mr-0.5" />
                        {dish.neutrales}
                      </span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 min-w-[160px]">
                    <div className="space-y-1">
                      <div className="flex justify-between text-[11px] font-semibold">
                        <span className="text-emerald-700">{posPercent}%</span>
                        <span className="text-rose-700">{negPercent}%</span>
                      </div>
                      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden flex">
                        <div
                          className="bg-emerald-500 h-full"
                          style={{ width: `${posPercent}%` }}
                        />
                        <div
                          className="bg-slate-300 h-full"
                          style={{
                            width: `${100 - posPercent - negPercent}%`,
                          }}
                        />
                        <div
                          className="bg-rose-500 h-full"
                          style={{ width: `${negPercent}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="font-mono font-bold text-sm text-indigo-700">
                      {dish.score_ponderado.toFixed(4)}
                    </div>
                    <div className="text-[10px] text-slate-400">Score Lower Bound</div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
