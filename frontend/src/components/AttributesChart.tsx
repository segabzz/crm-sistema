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
import { Tag } from 'lucide-react';
import type { TrendsResponse } from '../types';

interface AttributesChartProps {
  trends: TrendsResponse | null;
}

export const AttributesChart: React.FC<AttributesChartProps> = ({ trends }) => {
  if (!trends) return null;

  // Usar los atributos globales consolidados devueltos por el backend
  const globalAttrs = trends.atributos_mas_mencionados_global || [];

  const chartData = globalAttrs.map((item) => ({
    categoria:
      item.categoria_atributo.charAt(0).toUpperCase() +
      item.categoria_atributo.slice(1),
    positivas: item.positivas,
    negativas: item.negativas,
    neutrales: item.neutrales,
    total: item.total_menciones,
    ejemplos: (item.ejemplos_valores || []).slice(0, 3).join(', '),
  }));

  if (chartData.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center text-xs text-slate-400">
        No hay atributos específicos registrados en las reseñas aún.
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-900 text-white p-3 rounded-xl shadow-lg text-xs space-y-1 border border-slate-700">
          <p className="font-bold text-slate-100">{data.categoria}</p>
          <div className="space-y-0.5 text-slate-300">
            <p className="text-emerald-400">Positivas: {data.positivas}</p>
            <p className="text-rose-400">Negativas: {data.negativas}</p>
            <p className="text-slate-400">Neutrales: {data.neutrales}</p>
            <p className="text-slate-200 font-semibold pt-1 border-t border-slate-800">
              Total Menciones: {data.total}
            </p>
            {data.ejemplos && (
              <p className="text-[10px] text-slate-400 italic">Ejemplos: {data.ejemplos}</p>
            )}
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
          <Tag className="w-5 h-5 text-indigo-600" />
          <h3 className="text-base font-bold text-slate-900">
            Distribución de Atributos Operativos Más Mencionados
          </h3>
        </div>
        <span className="text-xs text-slate-400">Temperatura, Sabor, Porción, Término...</span>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 20, left: 0, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
            <XAxis
              dataKey="categoria"
              tick={{ fontSize: 11, fill: '#334155', fontWeight: 600 }}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fontSize: 11, fill: '#64748b' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 11, paddingTop: 10 }}
              iconType="circle"
            />
            <Bar
              dataKey="positivas"
              name="Elogios (+)"
              fill="#10b981"
              stackId="a"
              radius={[0, 0, 0, 0]}
            />
            <Bar
              dataKey="negativas"
              name="Quejas (-)"
              fill="#f43f5e"
              stackId="a"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
