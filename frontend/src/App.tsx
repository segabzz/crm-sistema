import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  MessageSquarePlus,
  UtensilsCrossed,
  ChefHat,
  QrCode,
  ArrowLeft,
  Smartphone,
} from 'lucide-react';
import { IngestaView } from './views/IngestaView';
import { DashboardView } from './views/DashboardView';
import { MenuView } from './views/MenuView';
import { WaiterOrderView } from './views/WaiterOrderView';
import { DinerPortalView } from './views/DinerPortalView';

type ActiveTab = 'RANKING' | 'MESERO' | 'INGESTA' | 'CATALOGO';

export const App: React.FC = () => {
  // Detectar si el usuario entró escaneando directamente un QR de comensal
  const [isDirectQrScan] = useState<boolean>(() => {
    const params = new URLSearchParams(window.location.search);
    return Boolean(params.get('portal') === 'comensal' || params.get('qr_token'));
  });

  // Modo simulación del Portal del Comensal cuando se abre desde la laptop del restaurante
  const [isDinerPortalPreview, setIsDinerPortalPreview] = useState<boolean>(false);

  const [activeQrToken, setActiveQrToken] = useState<string | null>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('qr_token');
  });

  const [activeTab, setActiveTab] = useState<ActiveTab>(() => {
    const params = new URLSearchParams(window.location.search);
    const tab = params.get('tab')?.toUpperCase();
    if (
      tab === 'INGESTA' ||
      tab === 'CATALOGO' ||
      tab === 'RANKING' ||
      tab === 'MESERO'
    ) {
      return tab as ActiveTab;
    }
    return 'RANKING';
  });

  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    // Comprobar estado de conexión con el backend
    fetch('/api/v1/dishes')
      .then((res) => {
        if (res.ok) setBackendStatus('online');
        else setBackendStatus('offline');
      })
      .catch(() => setBackendStatus('offline'));
  }, []);

  const handleOpenQrReview = (token: string) => {
    setActiveQrToken(token);
    setIsDinerPortalPreview(true);
  };

  const handleExitDinerPortalPreview = () => {
    setIsDinerPortalPreview(false);
  };

  const handleClearQrToken = () => {
    setActiveQrToken(null);
    const url = new URL(window.location.href);
    url.searchParams.delete('qr_token');
    url.searchParams.delete('portal');
    window.history.replaceState({}, '', url.toString());
  };

  // Si el comensal escaneó el QR en su celular (o estamos simulando su vista desde el botón del mesero),
  // mostrar EXCLUSIVAMENTE el Portal del Comensal sin las pestañas administrativas del CRM.
  if ((isDirectQrScan || isDinerPortalPreview) && activeQrToken) {
    return (
      <div className="min-h-screen flex flex-col font-sans">
        {/* Barra superior visible SOLO cuando se abre como simulación desde la laptop */}
        {isDinerPortalPreview && !isDirectQrScan && (
          <div className="bg-slate-900 text-white border-b border-slate-800 px-4 py-2.5 flex items-center justify-between text-xs sticky top-0 z-50">
            <div className="flex items-center space-x-2">
              <Smartphone className="w-4 h-4 text-emerald-400" />
              <span className="font-bold">
                Simulación: Portal Móvil del Comensal
              </span>
              <span className="hidden sm:inline text-slate-400 font-mono">
                ({activeQrToken})
              </span>
            </div>
            <button
              type="button"
              onClick={handleExitDinerPortalPreview}
              className="inline-flex items-center space-x-1.5 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold transition-colors cursor-pointer"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Volver al Panel del Restaurante</span>
            </button>
          </div>
        )}
        <DinerPortalView qrToken={activeQrToken} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Barra de Navegación Superior (Exclusiva para el Restaurante / Admin) */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-center justify-between min-h-16 py-2 gap-3">
            {/* Logo y Título */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center text-white shadow-sm">
                <ChefHat className="w-6 h-6" />
              </div>
              <div>
                <span className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-1.5">
                  CRM Gourmet AI
                  <span className="text-[10px] font-bold bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded">
                    MVP
                  </span>
                </span>
                <p className="text-[11px] text-slate-500 font-medium">
                  Análisis de Sentimiento & Ranking Wilson Score
                </p>
              </div>
            </div>

            {/* Pestañas de Navegación */}
            <nav className="flex space-x-1 sm:space-x-2">
              <button
                onClick={() => setActiveTab('RANKING')}
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeTab === 'RANKING'
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span>Dashboard & Ranking</span>
              </button>

              <button
                onClick={() => setActiveTab('MESERO')}
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeTab === 'MESERO'
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <QrCode className="w-4 h-4" />
                <span>Mesero / Pedidos QR</span>
              </button>

              <button
                onClick={() => setActiveTab('INGESTA')}
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeTab === 'INGESTA'
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <MessageSquarePlus className="w-4 h-4" />
                <span>Ingesta de Reseñas</span>
              </button>

              <button
                onClick={() => setActiveTab('CATALOGO')}
                className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeTab === 'CATALOGO'
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <UtensilsCrossed className="w-4 h-4" />
                <span>Catálogo & Admin</span>
              </button>
            </nav>

            {/* Status Backend */}
            <div className="hidden md:flex items-center space-x-2 text-xs">
              <span
                className={`w-2.5 h-2.5 rounded-full ${
                  backendStatus === 'online'
                    ? 'bg-emerald-500 animate-pulse'
                    : backendStatus === 'offline'
                    ? 'bg-red-500'
                    : 'bg-amber-500'
                }`}
              />
              <span className="text-slate-500 font-medium capitalize">
                Backend: {backendStatus}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Contenido Principal */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'RANKING' && <DashboardView />}
        {activeTab === 'MESERO' && (
          <WaiterOrderView onOpenQrReview={handleOpenQrReview} />
        )}
        {activeTab === 'INGESTA' && (
          <IngestaView
            qrToken={activeQrToken}
            onClearQrToken={handleClearQrToken}
          />
        )}
        {activeTab === 'CATALOGO' && <MenuView />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-400">
        CRM Gastronómico con IA Local &bull; Llama 3.2 &bull; Faster-Whisper &bull; Wilson Score Interval (Lower Bound 95%)
      </footer>
    </div>
  );
};

export default App;
