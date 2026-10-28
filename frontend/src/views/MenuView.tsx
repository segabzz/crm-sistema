import React, { useState, useEffect } from 'react';
import {
  RotateCcw,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Sparkles,
} from 'lucide-react';
import { api } from '../services/api';
import type { Dish } from '../types';
import { DishCard } from '../components/DishCard';

export const MenuView: React.FC = () => {
  const [dishes, setDishes] = useState<Dish[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('TODOS');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estados del modal de confirmación de Reset
  const [showResetModal, setShowResetModal] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  const loadDishes = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getDishes();
      setDishes(data);
    } catch (err: any) {
      console.error('Error al cargar platillos:', err);
      setError(err.message || 'Error al obtener el catálogo de platillos.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDishes();
  }, []);

  const handleResetDatabase = async () => {
    setIsResetting(true);
    setResetMessage(null);
    try {
      const res = await api.resetDatabase();
      setResetMessage(res.message || 'Base de datos reiniciada correctamente.');
      setShowResetModal(false);
      await loadDishes();
    } catch (err: any) {
      console.error('Error al resetear BD:', err);
      setError(err.message || 'Fallo al reiniciar la base de datos.');
      setShowResetModal(false);
    } finally {
      setIsResetting(false);
    }
  };

  const categories = [
    'TODOS',
    ...Array.from(new Set(dishes.map((d) => d.categoria))),
  ];

  const filteredDishes =
    selectedCategory === 'TODOS'
      ? dishes
      : dishes.filter((d) => d.categoria === selectedCategory);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Cabecera */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 bg-violet-50 text-violet-700 rounded-full text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Catálogo Oficial del Restaurante</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Menú & Administración del Sistema
          </h1>
          <p className="text-xs text-slate-500">
            Catálogo activo utilizado por Llama 3.2 y Whisper para anclaje de entidades del menú
          </p>
        </div>

        {/* Botón de acceso a Reset de BD */}
        <button
          onClick={() => setShowResetModal(true)}
          className="inline-flex items-center space-x-2 px-4 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-xl text-xs font-bold transition-colors cursor-pointer self-start sm:self-auto"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reiniciar Base de Datos</span>
        </button>
      </div>

      {/* Notificación de Reset exitoso */}
      {resetMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs flex items-center justify-between animate-in fade-in">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{resetMessage}</span>
          </div>
          <button
            onClick={() => setResetMessage(null)}
            className="text-xs font-semibold text-emerald-700 hover:text-emerald-900 cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* Manejo de Error */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={loadDishes}
            className="font-bold underline hover:text-rose-900 cursor-pointer"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Filtros de Categoría */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
              selectedCategory === cat
                ? 'bg-slate-900 text-white shadow-xs'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            {cat === 'TODOS' ? 'Todos los Platillos' : cat}
          </button>
        ))}
      </div>

      {/* Grid de Platillos */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-xs">
          Cargando catálogo oficial...
        </div>
      ) : filteredDishes.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-500 text-xs">
          No hay platillos en la categoría seleccionada.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredDishes.map((dish) => (
            <DishCard key={dish.id} dish={dish} />
          ))}
        </div>
      )}

      {/* Modal de Confirmación de Reinicio */}
      {showResetModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4 border border-slate-100">
            <div className="flex items-start space-x-3 text-rose-600">
              <div className="p-2.5 bg-rose-100 rounded-xl flex-shrink-0">
                <AlertTriangle className="w-6 h-6 text-rose-600" />
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-slate-900">
                  ¿Reiniciar Base de Datos?
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Esta acción eliminará todas las reseñas, transcripciones de audio, sentimientos
                  y atributos acumulados. El catálogo de platillos se restaurará limpio al estado
                  inicial.
                </p>
              </div>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800">
              Esta función está diseñada para pruebas de cátedra y benchmarking sin alterar la
              estructura de tablas relacionales.
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                type="button"
                onClick={() => setShowResetModal(false)}
                disabled={isResetting}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleResetDatabase}
                disabled={isResetting}
                className="inline-flex items-center space-x-2 px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl text-xs font-bold shadow-sm transition-colors cursor-pointer disabled:opacity-50"
              >
                {isResetting ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Limpiando BD...</span>
                  </>
                ) : (
                  <>
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Confirmar Reinicio</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
