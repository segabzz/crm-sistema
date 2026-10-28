import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ShieldCheck,
  Star,
  Mic,
  FileText,
  Clock,
  Sparkles,
  Info,
  Building2,
  QrCode,
} from 'lucide-react';
import type { Review } from '../types';

interface ReviewResultCardProps {
  review: Review | null;
  error: string | null;
  onDismissError?: () => void;
}

export const ReviewResultCard: React.FC<ReviewResultCardProps> = ({
  review,
  error,
  onDismissError,
}) => {
  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-6 shadow-sm transition-all animate-in fade-in duration-200">
        <div className="flex items-start space-x-4">
          <div className="p-2.5 bg-red-100 text-red-600 rounded-xl flex-shrink-0">
            <XCircle className="w-6 h-6" />
          </div>
          <div className="flex-1 space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-red-900">
                Error en el Procesamiento de la Reseña
              </h3>
              {onDismissError && (
                <button
                  onClick={onDismissError}
                  className="text-xs font-semibold text-red-700 hover:text-red-900 underline cursor-pointer"
                >
                  Cerrar
                </button>
              )}
            </div>
            <p className="text-sm text-red-700 leading-relaxed font-medium">
              {error}
            </p>
            <div className="pt-2 text-xs text-red-600 flex items-center space-x-1.5">
              <Info className="w-4 h-4 flex-shrink-0" />
              <span>
                Verifica que el backend esté en ejecución y que el audio contenga voz clara en español.
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!review) return null;

  const isAudioFailed =
    review.transcripcion &&
    review.transcripcion.estado_procesamiento === 'FALLIDO';

  const sentimientosEstablecimiento = review.sentimientos_establecimiento || [];

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden transition-all space-y-6 p-6">
      {/* Cabecera del Resultado */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-emerald-100 text-emerald-700 rounded-xl">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-mono uppercase bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-semibold">
                ID: {review.id.slice(0, 8)}...
              </span>
              {review.pedido_id && (
                <span className="inline-flex items-center gap-1 text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded">
                  <QrCode className="w-3 h-3" />
                  Pedido QR #{review.pedido_id.slice(0, 6)}
                </span>
              )}
              <span className="text-xs text-slate-400 font-medium">
                {new Date(review.created_at).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                })}
              </span>
            </div>
            <h3 className="text-base font-bold text-slate-900">
              Reseña de {review.autor_nombre || 'Anónimo'}
            </h3>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {review.calificacion_general && (
            <div className="flex items-center space-x-1 bg-amber-50 border border-amber-200 px-2.5 py-1 rounded-lg">
              <div className="flex text-amber-500">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-3.5 h-3.5 ${
                      i < (review.calificacion_general || 0)
                        ? 'fill-amber-400 text-amber-400'
                        : 'text-slate-200'
                    }`}
                  />
                ))}
              </div>
              <span className="text-xs font-bold text-amber-800">
                {review.calificacion_general}/5
              </span>
            </div>
          )}

          <span className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 bg-slate-100 text-slate-600 rounded-lg font-medium">
            {review.tipo_input === 'AUDIO' ? (
              <Mic className="w-3.5 h-3.5 text-indigo-600" />
            ) : (
              <FileText className="w-3.5 h-3.5 text-blue-600" />
            )}
            <span>{review.canal_origen}</span>
          </span>
        </div>
      </div>

      {/* Banner de Fallo en Transcripción */}
      {isAudioFailed && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <h4 className="font-semibold text-amber-900">
              Advertencia: Audio sin contenido inteligible
            </h4>
            <p className="text-amber-700 mt-0.5">
              El motor STT marcó este audio como <strong>FALLIDO</strong> porque no detectó
              voz o se encontró en silencio absoluto.
            </p>
          </div>
        </div>
      )}

      {/* Banner de Fallo en Extracción NLP */}
      {review.estado_analisis === 'FALLIDO_NLP' && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <h4 className="font-semibold text-amber-900">
              Advertencia: Extracción IA no disponible
            </h4>
            <p className="text-amber-700 mt-0.5">
              El servicio local de IA (Ollama / Llama 3.2) no estuvo disponible o falló al interpretar la reseña. La reseña se guardó correctamente para fines de auditoría, pero no se extrajeron platillos ni sentimientos.
            </p>
          </div>
        </div>
      )}

      {/* Sección de Transcripción (solo audio) */}
      {review.transcripcion && !isAudioFailed && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <div className="flex items-center space-x-1.5">
              <Mic className="w-4 h-4 text-indigo-600" />
              <span className="font-semibold text-slate-700">Transcripción Faster-Whisper</span>
            </div>
            <div className="flex items-center space-x-3">
              {review.transcripcion.duracion_segundos != null && (
                <span className="flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{review.transcripcion.duracion_segundos}s</span>
                </span>
              )}
              {review.transcripcion.confianza != null && (
                <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[11px]">
                  Confianza: {(review.transcripcion.confianza * 100).toFixed(1)}%
                </span>
              )}
            </div>
          </div>
          <p className="text-sm text-slate-800 italic bg-white p-3 rounded-lg border border-slate-200/60 font-mono">
            "{review.transcripcion.texto_transcrito}"
          </p>
        </div>
      )}

      {/* Texto de la reseña */}
      <div className="space-y-1.5">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Texto Analizado por NLP
        </h4>
        <p className="text-sm text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200/50 leading-relaxed">
          {review.texto_original}
        </p>
      </div>

      {/* Desglose de Sentimientos por Platillo */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <h4 className="text-sm font-bold text-slate-800">
              Extracción Estructurada por Platillo ({review.sentimientos.length})
            </h4>
          </div>
          <span className="text-xs text-slate-400">Llama 3.2 + Guardrails</span>
        </div>

        {review.sentimientos.length === 0 ? (
          <div className="p-4 bg-slate-50 border border-dashed border-slate-300 rounded-xl text-center text-xs text-slate-500">
            No se detectaron menciones de platillos en esta reseña.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            {review.sentimientos.map((sent) => {
              const isPositivo = sent.polaridad === 'positivo';
              const isNegativo = sent.polaridad === 'negativo';

              const polarityBadgeClass = isPositivo
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : isNegativo
                ? 'bg-red-50 text-red-700 border-red-200'
                : 'bg-slate-100 text-slate-700 border-slate-200';

              const scoreSign = sent.score_numerico > 0 ? '+' : '';
              const hasVerifiedBadge =
                sent.justificacion &&
                sent.justificacion.includes('[Verificado en Pedido]');
              const hasWarningOrderBadge =
                sent.justificacion &&
                sent.justificacion.includes('[Aviso: No figuraba en el pedido]');

              return (
                <div
                  key={sent.id}
                  className="bg-white border border-slate-200 hover:border-slate-300 rounded-xl p-4 shadow-2xs space-y-3 transition-colors"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-bold text-sm text-slate-900">
                        {sent.platillo_nombre_referenciado}
                      </span>
                      {sent.platillo_id ? (
                        <span className="text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 px-1.5 py-0.5 rounded">
                          Catálogo Oficial
                        </span>
                      ) : (
                        <span className="text-[10px] font-semibold bg-amber-50 text-amber-700 border border-amber-200 px-1.5 py-0.5 rounded">
                          Sin Clasificar
                        </span>
                      )}

                      {hasVerifiedBadge && (
                        <span className="text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full">
                          ✓ Verificado en Pedido
                        </span>
                      )}
                      {hasWarningOrderBadge && (
                        <span className="text-[10px] font-bold bg-amber-50 text-amber-800 border border-amber-300 px-2 py-0.5 rounded-full">
                          ⚠ Aviso: No figuraba en el pedido
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${polarityBadgeClass}`}
                      >
                        {sent.polaridad} ({scoreSign}
                        {sent.score_numerico.toFixed(2)})
                      </span>
                    </div>
                  </div>

                  {/* Fragmento extraído */}
                  {sent.fragmento_texto && (
                    <p className="text-xs text-slate-600 italic bg-slate-50 px-2.5 py-1.5 rounded border border-slate-100">
                      "{sent.fragmento_texto}"
                    </p>
                  )}

                  {/* Guardrail aplicado */}
                  {sent.justificacion && sent.justificacion.includes('[Guardrail]') && (
                    <div className="flex items-start space-x-2 p-2 bg-purple-50 border border-purple-200 rounded-lg text-xs text-purple-800 font-medium">
                      <ShieldCheck className="w-4 h-4 flex-shrink-0 text-purple-600 mt-0.5" />
                      <span>{sent.justificacion}</span>
                    </div>
                  )}

                  {/* Atributos Mencionados */}
                  {sent.atributos.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[11px] font-semibold text-slate-400 mr-1">
                        Atributos:
                      </span>
                      {sent.atributos.map((attr) => (
                        <span
                          key={attr.id}
                          className="inline-flex items-center space-x-1 text-[11px] px-2 py-0.5 bg-slate-100 border border-slate-200 rounded-md text-slate-700"
                        >
                          <span className="font-semibold text-slate-500">
                            {attr.categoria_atributo}:
                          </span>
                          <span className="font-bold">{attr.valor_mencionado}</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Desglose de Sentimientos del Establecimiento */}
      <div className="space-y-3 pt-2 border-t border-slate-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Building2 className="w-4 h-4 text-violet-600" />
            <h4 className="text-sm font-bold text-slate-800">
              Sentimiento del Establecimiento ({sentimientosEstablecimiento.length})
            </h4>
          </div>
          <span className="text-xs text-slate-400">
            Servicio &bull; Ambiente &bull; Limpieza &bull; Espera
          </span>
        </div>

        {sentimientosEstablecimiento.length === 0 ? (
          <div className="p-3 bg-slate-50 border border-dashed border-slate-200 rounded-xl text-center text-xs text-slate-400">
            No se mencionaron aspectos generales del establecimiento en esta reseña.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {sentimientosEstablecimiento.map((est) => {
              const isPos = est.polaridad === 'positivo';
              const isNeg = est.polaridad === 'negativo';
              const badgeClass = isPos
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : isNeg
                ? 'bg-red-50 text-red-700 border-red-200'
                : 'bg-slate-100 text-slate-700 border-slate-200';

              return (
                <div
                  key={est.id}
                  className="p-3.5 rounded-xl border border-slate-200 bg-violet-50/30 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-violet-900 bg-violet-100 px-2 py-0.5 rounded">
                      {est.categoria}
                    </span>
                    <span
                      className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${badgeClass}`}
                    >
                      {est.polaridad}
                    </span>
                  </div>
                  <p className="text-xs font-bold text-slate-800">
                    {est.valor_mencionado}
                  </p>
                  {est.fragmento_texto && (
                    <p className="text-[11px] text-slate-500 italic">
                      "{est.fragmento_texto}"
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
