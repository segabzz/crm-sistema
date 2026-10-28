import React, { useState } from 'react';
import { ReviewForm } from '../components/ReviewForm';
import { ReviewResultCard } from '../components/ReviewResultCard';
import type { Review } from '../types';
import { History, Sparkles } from 'lucide-react';

interface IngestaViewProps {
  qrToken?: string | null;
  onClearQrToken?: () => void;
}

export const IngestaView: React.FC<IngestaViewProps> = ({
  qrToken,
  onClearQrToken,
}) => {
  const [currentReview, setCurrentReview] = useState<Review | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [recentReviews, setRecentReviews] = useState<Review[]>([]);

  const handleReviewCreated = (review: Review) => {
    setCurrentReview(review);
    setError(null);
    setRecentReviews((prev) => [review, ...prev]);
  };

  const handleError = (errorMsg: string) => {
    setError(errorMsg);
  };

  const handleStartProcessing = () => {
    setError(null);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Encabezado de la Vista */}
      <div className="space-y-1">
        <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-full text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Pipeline de IA Multimodal</span>
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">
          Ingesta & Extracción de Reseñas
        </h1>
        <p className="text-sm text-slate-600">
          Captura comentarios por voz o texto. El sistema transcribe con Faster-Whisper,
          detecta entidades del menú y aspectos del establecimiento mediante Llama 3.2,
          aplica guardrails de negación y cruza la orden QR si aplica.
        </p>
      </div>

      {/* Formulario de Ingesta */}
      <ReviewForm
        onReviewCreated={handleReviewCreated}
        onError={handleError}
        onStartProcessing={handleStartProcessing}
        qrToken={qrToken}
        onClearQrToken={onClearQrToken}
      />

      {/* Resultado Inmediato o Error */}
      <div className="space-y-3">
        {(currentReview || error) && (
          <div>
            <h3 className="text-sm font-bold text-slate-700 mb-2">
              Resultado del Procesamiento en Tiempo Real
            </h3>
            <ReviewResultCard
              review={currentReview}
              error={error}
              onDismissError={() => setError(null)}
            />
          </div>
        )}
      </div>

      {/* Historial de la sesión actual */}
      {recentReviews.length > 1 && (
        <div className="pt-6 border-t border-slate-200 space-y-4">
          <div className="flex items-center space-x-2 text-slate-700">
            <History className="w-4 h-4 text-slate-500" />
            <h3 className="text-sm font-bold">
              Otras reseñas procesadas en esta sesión ({recentReviews.length})
            </h3>
          </div>

          <div className="space-y-4">
            {recentReviews.slice(1).map((rev) => (
              <ReviewResultCard key={rev.id} review={rev} error={null} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
