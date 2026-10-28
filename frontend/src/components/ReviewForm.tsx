import React, { useState, useEffect } from 'react';
import {
  FileText,
  Mic,
  Send,
  Loader2,
  Star,
  Sparkles,
  QrCode,
  X,
} from 'lucide-react';
import { AudioRecorder } from './AudioRecorder';
import { api } from '../services/api';
import type { Review, Order } from '../types';

interface ReviewFormProps {
  onReviewCreated: (review: Review) => void;
  onError: (error: string) => void;
  onStartProcessing: () => void;
  qrToken?: string | null;
  onClearQrToken?: () => void;
}

export const ReviewForm: React.FC<ReviewFormProps> = ({
  onReviewCreated,
  onError,
  onStartProcessing,
  qrToken,
  onClearQrToken,
}) => {
  const [activeTab, setActiveTab] = useState<'TEXT' | 'AUDIO'>('TEXT');
  const [autorNombre, setAutorNombre] = useState('');
  const [canalOrigen, setCanalOrigen] = useState(qrToken ? 'QR_MESA' : 'FORMULARIO_WEB');
  const [calificacionGeneral, setCalificacionGeneral] = useState<number | null>(null);
  const [linkedOrder, setLinkedOrder] = useState<Order | null>(null);
  const [linkedOrderError, setLinkedOrderError] = useState<string | null>(null);

  // Estado Texto
  const [texto, setTexto] = useState('');

  // Estado Audio
  const [audioBlobOrFile, setAudioBlobOrFile] = useState<Blob | File | null>(null);
  const [audioFilename, setAudioFilename] = useState<string>('');

  // Estado de carga
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (qrToken) {
      setCanalOrigen('QR_MESA');
      setLinkedOrderError(null);
      api
        .getOrderByToken(qrToken)
        .then((ord) => setLinkedOrder(ord))
        .catch((err) => {
          setLinkedOrder(null);
          setLinkedOrderError(err.message || 'No se encontró el pedido asociado al QR.');
        });
    } else {
      setLinkedOrder(null);
      setLinkedOrderError(null);
    }
  }, [qrToken]);

  const presets = [
    {
      label: 'Ejemplo Mixto (Sopa + Ribeye)',
      text: 'La Sopa Azteca estuvo deliciosa y muy caliente, pero el Ribeye a la Parrilla llegó frío y un poco salado.',
      rating: 3,
    },
    {
      label: 'Ejemplo Establecimiento (Servicio + Limpieza)',
      text: 'El servicio de los meseros fue excelente y el lugar estaba impecablemente limpio, aunque tardaron mucho en darnos mesa.',
      rating: 4,
    },
    {
      label: 'Ejemplo Guardrail (Negación)',
      text: 'No pedí la Sopa Azteca, pero los Tacos de Barbacoa estuvieron espectaculares.',
      rating: 5,
    },
  ];

  const handleApplyPreset = (presetText: string, rating: number) => {
    setTexto(presetText);
    setCalificacionGeneral(rating);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    onStartProcessing();

    try {
      if (activeTab === 'TEXT') {
        if (!texto.trim()) {
          throw new Error('Por favor ingresa el texto de la reseña.');
        }

        const review = await api.submitTextReview({
          texto: texto.trim(),
          canal_origen: canalOrigen,
          autor_nombre: autorNombre.trim() || 'Anónimo',
          calificacion_general: calificacionGeneral || undefined,
          qr_token: qrToken || undefined,
        });

        onReviewCreated(review);
        setTexto('');
      } else {
        if (!audioBlobOrFile) {
          throw new Error('Por favor graba o sube un archivo de audio antes de enviar.');
        }

        const formData = new FormData();
        const ext = audioFilename.split('.').pop() || 'webm';
        const fileToUpload =
          audioBlobOrFile instanceof File
            ? audioBlobOrFile
            : new File([audioBlobOrFile], audioFilename || `grabacion_${Date.now()}.${ext}`, {
                type: audioBlobOrFile.type || 'audio/webm',
              });

        formData.append('file', fileToUpload);
        formData.append('canal_origen', canalOrigen || 'AUDIO_IN_SITU');
        formData.append('autor_nombre', autorNombre.trim() || 'Anónimo');
        if (calificacionGeneral) {
          formData.append('calificacion_general', calificacionGeneral.toString());
        }
        if (qrToken) {
          formData.append('qr_token', qrToken);
        }

        const review = await api.submitAudioReview(formData);
        onReviewCreated(review);
        setAudioBlobOrFile(null);
        setAudioFilename('');
      }
    } catch (err: any) {
      console.error('Error al procesar reseña:', err);
      onError(err.message || 'Error desconocido al procesar la reseña en el servidor.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6 space-y-6"
    >
      {/* Banner de Pedido QR Vinculado */}
      {qrToken && (
        <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-xl flex items-start justify-between gap-4">
          <div className="flex items-start space-x-3">
            <div className="p-2 bg-indigo-600 text-white rounded-xl flex-shrink-0">
              <QrCode className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-extrabold text-indigo-950">
                  Reseña Vinculada a Pedido por QR
                </span>
                <span className="text-[11px] font-mono bg-white px-2 py-0.5 rounded border border-indigo-200 text-indigo-700">
                  {qrToken}
                </span>
              </div>
              {linkedOrder ? (
                <p className="text-xs text-indigo-800">
                  <strong>{linkedOrder.mesa}:</strong>{' '}
                  {linkedOrder.items
                    .map((i) => `${i.cantidad}x ${i.platillo_nombre}`)
                    .join(', ')}{' '}
                  (${linkedOrder.total.toFixed(2)})
                </p>
              ) : linkedOrderError ? (
                <p className="text-xs text-rose-600 font-medium">{linkedOrderError}</p>
              ) : (
                <p className="text-xs text-indigo-600">Cargando detalles del pedido...</p>
              )}
            </div>
          </div>

          {onClearQrToken && (
            <button
              type="button"
              onClick={onClearQrToken}
              className="text-xs text-indigo-600 hover:text-indigo-900 font-semibold flex items-center gap-1 cursor-pointer"
              title="Desvincular QR"
            >
              <X className="w-4 h-4" />
              <span>Desvincular</span>
            </button>
          )}
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Ingestar Nueva Reseña</h2>
          <p className="text-xs text-slate-500">
            Sube comentarios en texto o notas de voz para extracción automática con IA
          </p>
        </div>

        {/* Selector de modo Texto / Audio */}
        <div className="flex bg-slate-100 p-1 rounded-xl">
          <button
            type="button"
            onClick={() => {
              setActiveTab('TEXT');
              if (canalOrigen === 'AUDIO_IN_SITU') {
                setCanalOrigen(qrToken ? 'QR_MESA' : 'FORMULARIO_WEB');
              }
            }}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'TEXT'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Texto Manual</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setActiveTab('AUDIO');
              if (canalOrigen === 'FORMULARIO_WEB' && !qrToken) {
                setCanalOrigen('AUDIO_IN_SITU');
              }
            }}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'AUDIO'
                ? 'bg-white text-indigo-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Mic className="w-3.5 h-3.5" />
            <span>Audio / Voz</span>
          </button>
        </div>
      </div>

      {/* Metadatos: Autor, Canal, Estrellas */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Comensal / Autor
          </label>
          <input
            type="text"
            value={autorNombre}
            onChange={(e) => setAutorNombre(e.target.value)}
            placeholder="Ej. Roberto M. (Opcional)"
            className="w-full text-xs px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Canal de Origen
          </label>
          <select
            value={canalOrigen}
            onChange={(e) => setCanalOrigen(e.target.value)}
            className="w-full text-xs px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
          >
            <option value="QR_MESA">Código QR en Mesa</option>
            <option value="FORMULARIO_WEB">Formulario Web</option>
            <option value="AUDIO_IN_SITU">Audio In Situ (Micrófono)</option>
            <option value="GOOGLE_MAPS">Google Maps</option>
            <option value="WHATSAPP">WhatsApp</option>
            <option value="MANUAL">Manual / Encuesta</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Calificación General
          </label>
          <div className="flex items-center space-x-1 pt-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() =>
                  setCalificacionGeneral(calificacionGeneral === star ? null : star)
                }
                className="p-1 hover:scale-110 transition-transform cursor-pointer"
              >
                <Star
                  className={`w-5 h-5 ${
                    calificacionGeneral && star <= calificacionGeneral
                      ? 'fill-amber-400 text-amber-400'
                      : 'text-slate-300 hover:text-amber-200'
                  }`}
                />
              </button>
            ))}
            {calificacionGeneral && (
              <span className="text-xs font-bold text-amber-800 ml-1">
                {calificacionGeneral}/5
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Contenido según pestaña activa */}
      {activeTab === 'TEXT' ? (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <label className="block text-xs font-semibold text-slate-700">
              Texto de la Reseña
            </label>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] text-slate-400">Ejemplos rápidos:</span>
              {presets.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleApplyPreset(preset.text, preset.rating)}
                  className="text-[11px] text-indigo-600 hover:text-indigo-800 font-medium hover:underline cursor-pointer"
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>

          <textarea
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            rows={4}
            placeholder="Escribe la reseña libre del comensal. El pipeline identificará automáticamente platillos del catálogo, sentimientos del establecimiento (servicio, ambiente, limpieza, tiempo_espera) y atributos..."
            className="w-full text-xs sm:text-sm p-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white leading-relaxed transition-all"
          />

          <div className="flex justify-end text-[11px] text-slate-400">
            {texto.length} caracteres
          </div>
        </div>
      ) : (
        <AudioRecorder
          disabled={isSubmitting}
          onAudioSelected={(blob, filename) => {
            setAudioBlobOrFile(blob);
            setAudioFilename(filename);
          }}
          onClear={() => {
            setAudioBlobOrFile(null);
            setAudioFilename('');
          }}
        />
      )}

      {/* Botón de Envío */}
      <div className="pt-2">
        <button
          type="submit"
          disabled={
            isSubmitting ||
            (activeTab === 'TEXT' && !texto.trim()) ||
            (activeTab === 'AUDIO' && !audioBlobOrFile)
          }
          className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl font-semibold text-sm shadow-sm transition-all flex items-center justify-center space-x-2 cursor-pointer"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white" />
              <span>
                {activeTab === 'AUDIO'
                  ? 'Transcribiendo audio y extrayendo sentimientos (Whisper + Llama 3.2)...'
                  : 'Analizando sentimientos con IA (Llama 3.2)...'}
              </span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>
                {activeTab === 'AUDIO'
                  ? 'Transcribir y Procesar Audio'
                  : 'Procesar Reseña de Texto'}
              </span>
              <Send className="w-4 h-4 ml-1" />
            </>
          )}
        </button>
      </div>
    </form>
  );
};
