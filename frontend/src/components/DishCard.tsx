import React from 'react';
import { Utensils, CheckCircle } from 'lucide-react';
import type { Dish } from '../types';

interface DishCardProps {
  dish: Dish;
}

export const DishCard: React.FC<DishCardProps> = ({ dish }) => {
  const getCategoryColor = (categoria: string) => {
    switch (categoria.toLowerCase()) {
      case 'plato fuerte':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'entrada':
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      case 'postre':
        return 'bg-pink-50 text-pink-800 border-pink-200';
      case 'bebida':
        return 'bg-blue-50 text-blue-800 border-blue-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs hover:shadow-xs transition-shadow flex flex-col justify-between space-y-4">
      <div className="space-y-2">
        <div className="flex items-start justify-between gap-2">
          <span
            className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${getCategoryColor(
              dish.categoria
            )}`}
          >
            {dish.categoria}
          </span>
          {dish.activo && (
            <span className="inline-flex items-center space-x-1 text-[11px] text-emerald-600 font-semibold">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Activo</span>
            </span>
          )}
        </div>

        <h3 className="font-bold text-base text-slate-900 leading-snug">
          {dish.nombre}
        </h3>

        {dish.descripcion && (
          <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
            {dish.descripcion}
          </p>
        )}
      </div>

      <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-1 text-slate-400">
          <Utensils className="w-3.5 h-3.5" />
          <span className="text-[11px] font-mono">ID: {dish.id.slice(0, 6)}</span>
        </div>
        <div className="font-extrabold text-sm text-slate-900">
          ${dish.precio.toFixed(2)} <span className="text-[10px] text-slate-400 font-normal">MXN</span>
        </div>
      </div>
    </div>
  );
};
