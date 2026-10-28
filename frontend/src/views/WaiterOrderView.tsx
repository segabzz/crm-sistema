import React, { useState, useEffect, useCallback } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import {
  Utensils,
  Plus,
  Minus,
  QrCode,
  ShoppingBag,
  CheckCircle2,
  ExternalLink,
  RefreshCw,
  Trash2,
  Sparkles,
  Users,
} from 'lucide-react';
import { api } from '../services/api';
import type { Dish, Order } from '../types';

interface WaiterOrderViewProps {
  onOpenQrReview: (qrToken: string) => void;
}

const MESAS_RAPIDAS = ['Mesa 1', 'Mesa 2', 'Mesa 3', 'Mesa 4', 'Terraza 1', 'Barra'];

export const WaiterOrderView: React.FC<WaiterOrderViewProps> = ({ onOpenQrReview }) => {
  const [dishes, setDishes] = useState<Dish[]>([]);
  const [recentOrders, setRecentOrders] = useState<Order[]>([]);
  const [mesa, setMesa] = useState<string>('Mesa 1');
  const [baseUrl, setBaseUrl] = useState<string>(() => window.location.origin);
  const [cart, setCart] = useState<Record<string, number>>({});
  const [activeOrder, setActiveOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [dishesData, ordersData] = await Promise.all([
        api.getDishes(),
        api.getOrders(10),
      ]);
      setDishes(dishesData.filter((d) => d.activo));
      setRecentOrders(ordersData);
    } catch (err: any) {
      setError(err.message || 'No se pudo cargar el catálogo de platillos.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const updateQuantity = (dishId: string, delta: number) => {
    setCart((prev) => {
      const current = prev[dishId] || 0;
      const next = current + delta;
      if (next <= 0) {
        const copy = { ...prev };
        delete copy[dishId];
        return copy;
      }
      return { ...prev, [dishId]: next };
    });
  };

  const clearCart = () => {
    setCart({});
  };

  const cartItems = Object.entries(cart)
    .map(([dishId, cantidad]) => {
      const dish = dishes.find((d) => d.id === dishId);
      if (!dish) return null;
      return {
        dish,
        cantidad,
        subtotal: dish.precio * cantidad,
      };
    })
    .filter(Boolean) as { dish: Dish; cantidad: number; subtotal: number }[];

  const totalPedido = cartItems.reduce((acc, item) => acc + item.subtotal, 0);
  const totalUnidades = cartItems.reduce((acc, item) => acc + item.cantidad, 0);

  const handleConfirmOrder = async () => {
    if (cartItems.length === 0) return;
    setIsSubmitting(true);
    setError(null);
    try {
      const created = await api.createOrder({
        mesa: mesa.trim() || 'Mesa General',
        items: cartItems.map((it) => ({
          platillo_id: it.dish.id,
          cantidad: it.cantidad,
        })),
      });
      setActiveOrder(created);
      setCart({});
      setRecentOrders((prev) => [created, ...prev.filter((o) => o.id !== created.id)]);
    } catch (err: any) {
      setError(err.message || 'Error al registrar el pedido.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getQrUrl = (qrToken: string) => {
    const cleanBase = baseUrl.trim().replace(/\/+$/, '') || window.location.origin;
    return `${cleanBase}/?portal=comensal&qr_token=${encodeURIComponent(qrToken)}`;
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Cabecera */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Modo Tablet POS &bull; Sin Autenticación</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Comanda de Mesero & Generación de QR
          </h1>
          <p className="text-xs text-slate-500">
            Selecciona la mesa y los platillos servidos para generar el código QR único de evaluación vinculada
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={isLoading}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-2xs transition-all cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-indigo-600' : ''}`} />
          <span>Actualizar Pedidos</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs font-medium">
          {error}
        </div>
      )}

      {/* Layout Principal: Catálogo táctil (Izquierda) + Resumen y QR (Derecha) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Columna Izquierda: Selector de Mesa y Platillos */}
        <div className="lg:col-span-7 space-y-6">
          {/* Selección de Mesa */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Users className="w-4 h-4 text-indigo-600" />
                <span>Identificador de Mesa</span>
              </label>
              <input
                type="text"
                value={mesa}
                onChange={(e) => setMesa(e.target.value)}
                placeholder="Ej. Mesa 5"
                className="text-xs font-bold px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 w-40 text-right"
              />
            </div>

            <div className="flex flex-wrap gap-2">
              {MESAS_RAPIDAS.map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMesa(m)}
                  className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    mesa === m
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Grid de Platillos para Tablet */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Utensils className="w-4 h-4 text-indigo-600" />
                <span>Catálogo Oficial ({dishes.length} platillos)</span>
              </h2>
              <span className="text-[11px] text-slate-400">
                Toca + para agregar a la comanda
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {dishes.map((dish) => {
                const qty = cart[dish.id] || 0;
                return (
                  <div
                    key={dish.id}
                    className={`p-4 rounded-xl border transition-all flex flex-col justify-between gap-3 ${
                      qty > 0
                        ? 'border-indigo-500 bg-indigo-50/40 shadow-xs'
                        : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                          {dish.categoria}
                        </span>
                        <span className="text-sm font-black text-indigo-700">
                          ${dish.precio.toFixed(2)}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-slate-900 pt-1">
                        {dish.nombre}
                      </h3>
                      {dish.descripcion && (
                        <p className="text-[11px] text-slate-500 line-clamp-2">
                          {dish.descripcion}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-200/70">
                      <span className="text-xs font-semibold text-slate-600">
                        {qty > 0 ? `${qty} en comanda` : 'Sin seleccionar'}
                      </span>
                      <div className="flex items-center space-x-2">
                        <button
                          type="button"
                          onClick={() => updateQuantity(dish.id, -1)}
                          disabled={qty === 0}
                          className="w-9 h-9 rounded-xl bg-white border border-slate-300 flex items-center justify-center text-slate-700 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer shadow-2xs"
                        >
                          <Minus className="w-4 h-4" />
                        </button>
                        <span className="w-6 text-center text-sm font-black text-slate-900">
                          {qty}
                        </span>
                        <button
                          type="button"
                          onClick={() => updateQuantity(dish.id, 1)}
                          className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center hover:bg-indigo-700 cursor-pointer shadow-2xs"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Columna Derecha: Comanda Actual + Código QR */}
        <div className="lg:col-span-5 space-y-6">
          {/* Resumen del Pedido por Confirmar */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <ShoppingBag className="w-5 h-5 text-indigo-600" />
                <div>
                  <h2 className="text-base font-bold text-slate-900">
                    Comanda Actual ({mesa || 'Mesa'})
                  </h2>
                  <p className="text-[11px] text-slate-500">
                    {totalUnidades} platillo(s) seleccionado(s)
                  </p>
                </div>
              </div>
              {cartItems.length > 0 && (
                <button
                  type="button"
                  onClick={clearCart}
                  className="text-xs text-rose-600 hover:text-rose-800 font-semibold flex items-center gap-1 cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Vaciar</span>
                </button>
              )}
            </div>

            {cartItems.length === 0 ? (
              <div className="py-8 text-center space-y-2 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                <Utensils className="w-6 h-6 text-slate-400 mx-auto" />
                <p className="text-xs text-slate-500 font-medium">
                  Selecciona platillos del catálogo para armar el pedido de la mesa.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="divide-y divide-slate-100 max-h-60 overflow-y-auto pr-1">
                  {cartItems.map(({ dish, cantidad, subtotal }) => (
                    <div
                      key={dish.id}
                      className="py-2.5 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-bold text-slate-900">
                          {cantidad}x {dish.nombre}
                        </span>
                        <span className="block text-[11px] text-slate-400">
                          ${dish.precio.toFixed(2)} c/u
                        </span>
                      </div>
                      <span className="font-bold text-slate-800">
                        ${subtotal.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-200 flex items-center justify-between">
                  <span className="text-sm font-bold text-slate-700">Total Pedido</span>
                  <span className="text-lg font-black text-indigo-700">
                    ${totalPedido.toFixed(2)} MXN
                  </span>
                </div>
              </div>
            )}

            <button
              type="button"
              onClick={handleConfirmOrder}
              disabled={cartItems.length === 0 || isSubmitting}
              className="w-full py-3.5 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl font-bold text-sm shadow-sm transition-all flex items-center justify-center space-x-2 cursor-pointer"
            >
              <QrCode className="w-4 h-4" />
              <span>
                {isSubmitting
                  ? 'Generando Pedido y Token QR...'
                  : 'Confirmar Pedido y Generar QR'}
              </span>
            </button>
          </div>

          {/* Tarjeta de Código QR Generado */}
          {activeOrder && (
            <div className="bg-gradient-to-br from-indigo-950 via-slate-900 to-indigo-900 text-white rounded-2xl p-6 shadow-md space-y-5 animate-in fade-in duration-200">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <span className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 px-2.5 py-0.5 rounded-full">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    QR Listo para Comensal
                  </span>
                  <h3 className="text-lg font-black tracking-tight pt-1">
                    {activeOrder.mesa} &bull; ${activeOrder.total.toFixed(2)}
                  </h3>
                  <p className="text-xs text-indigo-200 font-mono">
                    Token: {activeOrder.qr_token}
                  </p>
                </div>
                <span className="text-[11px] font-bold bg-white/10 px-2.5 py-1 rounded-lg">
                  {activeOrder.estado}
                </span>
              </div>

              {/* QR SVG en contenedor blanco de alto contraste */}
              <div className="bg-white p-5 rounded-2xl flex flex-col items-center justify-center space-y-3 shadow-inner">
                <QRCodeSVG
                  value={getQrUrl(activeOrder.qr_token)}
                  size={200}
                  level="M"
                  includeMargin={true}
                />
                <p className="text-[11px] text-slate-500 text-center font-medium max-w-xs">
                  Escanea este código con la cámara del celular para abrir el formulario de reseña vinculado a este pedido.
                </p>
              </div>

              {/* Configuración de URL Base para escaneo desde celular en LAN */}
              <div className="bg-white/10 rounded-xl p-3 space-y-1">
                <label className="block text-[10px] font-bold uppercase tracking-wider text-indigo-200">
                  URL Base para el QR (Cambia localhost por la IP Wi-Fi de tu laptop para escanear desde celular):
                </label>
                <input
                  type="text"
                  value={baseUrl}
                  onChange={(e) => setBaseUrl(e.target.value)}
                  className="w-full text-xs font-mono bg-slate-900/80 border border-indigo-400/30 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:ring-2 focus:ring-emerald-400"
                />
              </div>

              {/* Platillos incluidos en este QR */}
              <div className="bg-white/10 rounded-xl p-3.5 space-y-1.5 text-xs">
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-200">
                  Platillos registrados en la orden:
                </span>
                <ul className="space-y-1">
                  {activeOrder.items.map((it) => (
                    <li key={it.id} className="flex justify-between text-indigo-50">
                      <span>
                        {it.cantidad}x {it.platillo_nombre}
                      </span>
                      <span className="font-semibold">${it.subtotal.toFixed(2)}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Botón de Simulación Directa para Demo */}
              <button
                type="button"
                onClick={() => onOpenQrReview(activeOrder.qr_token)}
                className="w-full py-3 px-4 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-black text-xs rounded-xl shadow-sm transition-all flex items-center justify-center space-x-2 cursor-pointer"
              >
                <ExternalLink className="w-4 h-4" />
                <span>Simular Escaneo QR (Abrir Vista Comensal)</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Historial de Pedidos Recientes */}
      {recentOrders.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-2xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">
              Pedidos Recientes ({recentOrders.length})
            </h3>
            <span className="text-xs text-slate-400">
              Haz clic en "Ver QR" o "Evaluar" para probar múltiples comensales en la misma mesa
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {recentOrders.map((ord) => (
              <div
                key={ord.id}
                className="p-4 rounded-xl border border-slate-200 hover:border-indigo-300 bg-slate-50/60 flex flex-col justify-between gap-3 transition-all"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-slate-900">
                      {ord.mesa}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        ord.estado === 'EVALUADO'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {ord.estado} ({ord.total_resenas} reseña{ord.total_resenas === 1 ? '' : 's'})
                    </span>
                  </div>
                  <p className="text-[11px] font-mono text-slate-500">
                    Token: {ord.qr_token}
                  </p>
                  <p className="text-xs text-slate-700 font-medium line-clamp-2">
                    {ord.items.map((i) => `${i.cantidad}x ${i.platillo_nombre}`).join(', ')}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-200/80">
                  <span className="text-xs font-black text-indigo-700">
                    ${ord.total.toFixed(2)}
                  </span>
                  <div className="flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={() => setActiveOrder(ord)}
                      className="px-2.5 py-1 text-[11px] font-bold bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-100 cursor-pointer"
                    >
                      Ver QR
                    </button>
                    <button
                      type="button"
                      onClick={() => onOpenQrReview(ord.qr_token)}
                      className="px-2.5 py-1 text-[11px] font-bold bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 cursor-pointer"
                    >
                      Evaluar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
