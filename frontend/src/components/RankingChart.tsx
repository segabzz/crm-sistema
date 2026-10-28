import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { BarChart3 } from 'lucide-react';
import type { DishRankingItem } from '../types';

interface RankingChartProps {
  ranking: DishRankingItem[];
}

export const RankingChart: React.FC<RankingChartProps> = ({ ranking }) => {
  if (!ranking || ranking.length === 0) {
    return null;
  }

  // Preparamos datos para la gráfica
  const chartData = ranking.map((item) => ({
    nombre: item.nombre.length > 18 ? `${item.nombre.slice(0, 16)}...` : item.nombre,
    nombreCompleto: item.nombre,
    wilsonScore: parseFloat(item.score_ponderado.toFixed(4)),
    tasaPositiva: parseFloat((item.tasa_positiva * 100).toFixed(1)),
    menciones: item.total_menciones,
    positivas: item.positivas,
    negativas: item.negativas,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-900 text-white p-3 rounded-xl shadow-lg text-xs space-y-1.5 border border-slate-700">
          <p className="font-bold text-slate-100">{data.nombreCompleto}</p>
          <div className="space-y-0.5 text-slate-300">
            <p>
              Wilson Score:{' '}
              <span className="font-mono font-bold text-indigo-400">
                {data.wilsonScore.toFixed(4)}
              </span>
            </p>
            <p>
              Tasa Positiva:{' '}
              <span className="font-bold text-emerald-400">{data.tasaPositiva}%</span>
            </p>
            <p>
              Menciones Totales:{' '}
              <span className="font-semibold">{data.menciones}</span> ({data.positivas}+ / {data.negativas}-)
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-indigo-600" />
          <h3 className="text-base font-bold text-slate-900">
            Comparativa de Wilson Score vs Satisfacción Directa
          </h3>
        </div>
        <span className="text-xs text-slate-400">Escala Normalizada (0 a 1)</span>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
            <XAxis
              type="number"
              domain={[0, 1]}
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
            <YAxis
              type="category"
              dataKey="nombre"
              tick={{ fontSize: 11, fill: '#334155', fontWeight: 600 }}
              width={120}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 11, paddingTop: 10 }}
              iconType="circle"
            />
            <Bar
              dataKey="wilsonScore"
              name="Wilson Score (Lower Bound)"
              fill="#6366f1"
              radius={[0, 4, 4, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
