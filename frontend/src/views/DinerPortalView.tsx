import React, { useState, useEffect, useRef } from 'react';
import {
  ChefHat,
  Star,
  MessageSquare,
  Mic,
  Send,
  Loader2,
  CheckCircle2,
  Utensils,
  Sparkles,
  Upload,
  Square,
  Trash2,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  RefreshCw,
  Building2,
} from 'lucide-react';
import { api } from '../services/api';
import type { Order, Review } from '../types';

interface DinerPortalViewProps {
  qrToken: string;
}

const RATING_LABELS: Record<number, string> = {
  1: 'Muy insatisfecho',
  2: 'Regular, puede mejorar',
  3: 'Buena experiencia',
  4: '¡Muy bueno!',
  5: '¡Excelente experiencia!',
};

export const DinerPortalView: React.FC<DinerPortalViewProps> = ({ qrToken }) => {
  const [order, setOrder] = useState<Order | null>(null);
  const [orderLoading, setOrderLoading] = useState<boolean>(true);
  const [orderError, setOrderError] = useState<string | null>(null);

  // Formulario del comensal
  const [mode, setMode] = useState<'TEXT' | 'AUDIO'>('TEXT');
  const [rating, setRating] = useState<number>(5);
  const [autorNombre, setAutorNombre] = useState<string>('');
  const [texto, setTexto] = useState<string>('');

  // Estado de audio móvil / navegador
  const [audioBlobOrFile, setAudioBlobOrFile] = useState<Blob | File | null>(null);
  const [audioFilename, setAudioFilename] = useState<string>('');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingSeconds, setRecordingSeconds] = useState<number>(0);
  const [audioError, setAudioError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Estado de envío y resultado
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submittedReview, setSubmittedReview] = useState<Review | null>(null);
  const [showAiDemoDetails, setShowAiDemoDetails] = useState<boolean>(false);

  // Detectar si el navegador permite grabación directa por micrófono (HTTPS o localhost)
  const canUseLiveMic =
    typeof window !== 'undefined' &&
    Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) &&
    window.isSecureContext;

  useEffect(() => {
    setOrderLoading(true);
    setOrderError(null);
    api
      .getOrderByToken(qrToken)
      .then((data) => {
        setOrder(data);
      })
      .catch((err: any) => {
        setOrder(null);
        setOrderError(
          err.message || 'No pudimos encontrar la comanda asociada a este código QR.'
        );
      })
      .finally(() => {
        setOrderLoading(false);
      });
  }, [qrToken]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  const handleInsertChip = (label: string) => {
    setMode('TEXT');
    setTexto((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return `${label}: `;
      if (trimmed.toLowerCase().includes(label.toLowerCase())) return prev;
      const separator = trimmed.endsWith('.') || trimmed.endsWith(',') ? ' ' : '. ';
      return `${trimmed}${separator}${label}: `;
    });
  };

  const startLiveRecording = async () => {
    setAudioError(null);
    audioChunksRef.current = [];

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error(
          'Por seguridad del navegador móvil en red local (HTTP), usa el botón de abajo para grabar o adjuntar tu nota de voz.'
        );
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      let mimeType = 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        if (MediaRecorder.isTypeSupported('audio/webm')) {
          mimeType = 'audio/webm';
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          mimeType = 'audio/mp4';
        } else {
          mimeType = '';
        }
      }

      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      recorder.onstop = () => {
        const mime = recorder.mimeType || 'audio/webm';
        const blob = new Blob(audioChunksRef.current, { type: mime });
        const ext = mime.includes('mp4') ? 'mp4' : 'webm';
        const fname = `opinion_voz_${Date.now()}.${ext}`;
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setAudioFilename(fname);
        setAudioBlobOrFile(blob);
        stream.getTracks().forEach((t) => t.stop());
      };

      recorder.start(250);
      setIsRecording(true);
      setRecordingSeconds(0);
      timerRef.current = window.setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      setAudioError(
        'Usa el botón "Grabar / Subir Nota de Voz" para capturar el audio directamente con tu celular.'
      );
    }
  };

  const stopLiveRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAudioError(null);
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      setAudioFilename(file.name);
      setAudioBlobOrFile(file);
    }
  };

  const clearAudio = () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setAudioBlobOrFile(null);
    setAudioFilename('');
    setRecordingSeconds(0);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const formatTime = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setIsSubmitting(true);

    try {
      if (mode === 'TEXT') {
        if (!texto.trim()) {
          throw new Error('Por favor escribe tu opinión antes de enviar.');
        }
        const created = await api.submitTextReview({
          texto: texto.trim(),
          canal_origen: 'QR_MESA',
          autor_nombre: autorNombre.trim() || 'Comensal en Mesa',
          calificacion_general: rating,
          qr_token: qrToken,
        });
        setSubmittedReview(created);
        setTexto('');
      } else {
        if (!audioBlobOrFile) {
          throw new Error('Por favor graba o selecciona una nota de voz antes de enviar.');
        }
        const formData = new FormData();
        const ext = audioFilename.split('.').pop() || 'webm';
        const fileToUpload =
          audioBlobOrFile instanceof File
            ? audioBlobOrFile
            : new File([audioBlobOrFile], audioFilename || `nota_voz_${Date.now()}.${ext}`, {
                type: audioBlobOrFile.type || 'audio/webm',
              });

        formData.append('file', fileToUpload);
        formData.append('canal_origen', 'QR_MESA');
        formData.append('autor_nombre', autorNombre.trim() || 'Comensal en Mesa');
        formData.append('calificacion_general', rating.toString());
        formData.append('qr_token', qrToken);

        const created = await api.submitAudioReview(formData);
        setSubmittedReview(created);
        clearAudio();
      }

      // Refrescar estado del pedido
      api
        .getOrderByToken(qrToken)
        .then((updated) => setOrder(updated))
        .catch(() => {});
    } catch (err: any) {
      setSubmitError(
        err.message || 'Ocurrió un problema al enviar tu opinión. Intenta de nuevo.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetForAnotherDiner = () => {
    setSubmittedReview(null);
    setSubmitError(null);
    setTexto('');
    setAutorNombre('');
    setRating(5);
    setShowAiDemoDetails(false);
    clearAudio();
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-950 via-slate-900 to-slate-950 text-slate-900 flex flex-col justify-between py-6 px-4 sm:px-6">
      <div className="w-full max-w-md mx-auto space-y-5">
        {/* Cabecera Exclusiva del Restaurante para el Comensal */}
        <div className="text-center text-white space-y-2 pt-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center mx-auto shadow-lg shadow-indigo-500/30 border border-white/15">
            <ChefHat className="w-8 h-8 text-white" />
          </div>
          <div>
            <span className="inline-block text-[10px] font-bold uppercase tracking-widest text-indigo-300 bg-white/10 px-3 py-0.5 rounded-full">
              Portal del Comensal
            </span>
            <h1 className="text-xl font-black tracking-tight mt-1">
              ¿Qué te pareció tu visita hoy?
            </h1>
            <p className="text-xs text-indigo-200/80 max-w-xs mx-auto">
              Tu opinión sobre los platillos y nuestro servicio nos ayuda a mejorar cada día
            </p>
          </div>
        </div>

        {/* Estado de Carga o Error del QR */}
        {orderLoading ? (
          <div className="bg-white rounded-3xl p-8 text-center space-y-3 shadow-xl">
            <Loader2 className="w-7 h-7 animate-spin text-indigo-600 mx-auto" />
            <p className="text-xs font-semibold text-slate-600">
              Cargando los detalles de tu mesa...
            </p>
          </div>
        ) : orderError || !order ? (
          <div className="bg-white rounded-3xl p-6 text-center space-y-3 shadow-xl border border-rose-200">
            <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h2 className="text-base font-bold text-slate-900">
              Código QR no encontrado
            </h2>
            <p className="text-xs text-slate-500 leading-relaxed">
              {orderError ||
                'No pudimos encontrar el pedido vinculado a este código QR. Solicita apoyo a tu mesero.'}
            </p>
          </div>
        ) : submittedReview ? (
          /* Pantalla de Agradecimiento Post-Envío */
          <div className="bg-white rounded-3xl p-6 shadow-xl space-y-5 animate-in fade-in duration-200">
            <div className="text-center space-y-2 pt-2">
              <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <span className="inline-block text-[11px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 px-3 py-0.5 rounded-full border border-emerald-200">
                {order.mesa} &bull; Opinión Registrada
              </span>
              <h2 className="text-xl font-black text-slate-900">
                ¡Muchas gracias por tu visita!
              </h2>
              <p className="text-xs text-slate-500 leading-relaxed">
                Hemos recibido tus comentarios sobre tu experiencia en{' '}
                <strong>{order.mesa}</strong>. ¡Esperamos verte pronto de nuevo!
              </p>
            </div>

            {/* Botón para que otro acompañante de la misma mesa pueda opinar */}
            <button
              type="button"
              onClick={handleResetForAnotherDiner}
              className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold text-xs shadow-sm transition-all flex items-center justify-center space-x-2 cursor-pointer"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Enviar otra opinión de esta misma mesa</span>
            </button>

            {/* Acordeón discreto para Demo con el Profesor */}
            <div className="pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowAiDemoDetails((prev) => !prev)}
                className="w-full flex items-center justify-between text-[11px] font-semibold text-slate-400 hover:text-slate-600 py-1.5 cursor-pointer"
              >
                <span className="flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                  <span>Ver lectura de IA en tiempo real (Modo Demo)</span>
                </span>
                {showAiDemoDetails ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>

              {showAiDemoDetails && (
                <div className="mt-3 space-y-3 bg-slate-50 rounded-2xl p-4 border border-slate-200/80 text-xs">
                  {submittedReview.transcripcion && (
                    <div className="p-2.5 bg-white rounded-xl border border-slate-200">
                      <span className="block text-[10px] font-bold uppercase text-indigo-600">
                        Transcripción de Voz (Faster-Whisper):
                      </span>
                      <p className="italic text-slate-700 mt-0.5">
                        "{submittedReview.transcripcion.texto_transcrito}"
                      </p>
                    </div>
                  )}

                  <div className="space-y-1.5">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                      <Utensils className="w-3 h-3 text-indigo-600" />
                      Platillos detectados ({submittedReview.sentimientos.length}):
                    </span>
                    {submittedReview.sentimientos.length === 0 ? (
                      <p className="text-[11px] text-slate-400 italic">
                        Sin menciones a platillos específicos.
                      </p>
                    ) : (
                      submittedReview.sentimientos.map((s) => {
                        const isVerified = s.justificacion?.includes('[Verificado en Pedido]');
                        const isNotOrdered = s.justificacion?.includes(
                          '[Aviso: No figuraba en el pedido]'
                        );
                        return (
                          <div
                            key={s.id}
                            className="p-2.5 bg-white rounded-xl border border-slate-200 space-y-1"
                          >
                            <div className="flex items-center justify-between gap-2">
                              <span className="font-bold text-slate-900">
                                {s.platillo_nombre_referenciado}
                              </span>
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                  s.polaridad === 'positivo'
                                    ? 'bg-emerald-50 text-emerald-700'
                                    : s.polaridad === 'negativo'
                                    ? 'bg-rose-50 text-rose-700'
                                    : 'bg-slate-100 text-slate-700'
                                }`}
                              >
                                {s.polaridad}
                              </span>
                            </div>
                            {isVerified && (
                              <span className="inline-block text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                                ✓ Verificado en Pedido de {order.mesa}
                              </span>
                            )}
                            {isNotOrdered && (
                              <span className="inline-block text-[10px] font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-300">
                                ⚠ No figuraba en la orden de la mesa
                              </span>
                            )}
                          </div>
                        );
                      })
                    )}
                  </div>

                  {submittedReview.sentimientos_establecimiento &&
                    submittedReview.sentimientos_establecimiento.length > 0 && (
                      <div className="space-y-1.5 pt-2 border-t border-slate-200">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                          <Building2 className="w-3 h-3 text-violet-600" />
                          Establecimiento ({submittedReview.sentimientos_establecimiento.length}):
                        </span>
                        {submittedReview.sentimientos_establecimiento.map((est) => (
                          <div
                            key={est.id}
                            className="p-2 bg-white rounded-xl border border-slate-200 flex items-center justify-between"
                          >
                            <div>
                              <span className="text-[10px] font-extrabold uppercase text-violet-700 mr-1.5">
                                {est.categoria}:
                              </span>
                              <span className="text-slate-700 font-medium">
                                {est.valor_mencionado}
                              </span>
                            </div>
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                est.polaridad === 'positivo'
                                  ? 'bg-emerald-50 text-emerald-700'
                                  : est.polaridad === 'negativo'
                                  ? 'bg-rose-50 text-rose-700'
                                  : 'bg-slate-100 text-slate-700'
                              }`}
                            >
                              {est.polaridad}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Vista Principal del Comensal: Resumen de su Mesa + Formulario */
          <>
            {/* Tarjeta de Consumo de la Mesa */}
            <div className="bg-white/10 backdrop-blur-md border border-white/15 rounded-3xl p-4 text-white space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="px-2.5 py-1 rounded-xl bg-indigo-500 text-white text-xs font-black">
                    {order.mesa}
                  </span>
                  <span className="text-xs text-indigo-200 font-medium">
                    Tu orden servida
                  </span>
                </div>
                <span className="text-xs font-bold text-emerald-300">
                  Total: ${order.total.toFixed(2)}
                </span>
              </div>

              {/* Platillos de la mesa como etiquetas interactivas */}
              <div className="space-y-1.5">
                <p className="text-[11px] text-indigo-200/90">
                  Platillos en tu mesa (puedes tocarlos para mencionarlos):
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {order.items.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => handleInsertChip(item.platillo_nombre)}
                      className="text-xs bg-white/15 hover:bg-white/25 active:scale-95 text-white px-2.5 py-1 rounded-xl font-medium transition-all flex items-center gap-1 cursor-pointer border border-white/10"
                    >
                      <Utensils className="w-3 h-3 text-indigo-300" />
                      <span>
                        {item.cantidad}x {item.platillo_nombre}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Tarjeta Blanca del Formulario del Comensal */}
            <form
              onSubmit={handleSubmit}
              className="bg-white rounded-3xl p-5 sm:p-6 shadow-2xl space-y-5"
            >
              {submitError && (
                <div className="p-3.5 bg-rose-50 border border-rose-200 text-rose-700 rounded-2xl text-xs font-medium flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>{submitError}</span>
                </div>
              )}

              {/* 1. Calificación con Estrellas */}
              <div className="text-center space-y-2 pb-3 border-b border-slate-100">
                <label className="block text-xs font-extrabold uppercase tracking-wider text-slate-500">
                  1. Calificación General
                </label>
                <div className="flex items-center justify-center space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setRating(star)}
                      className="p-1.5 active:scale-90 hover:scale-110 transition-transform cursor-pointer"
                    >
                      <Star
                        className={`w-8 h-8 transition-colors ${
                          star <= rating
                            ? 'fill-amber-400 text-amber-400 drop-shadow-2xs'
                            : 'text-slate-200'
                        }`}
                      />
                    </button>
                  ))}
                </div>
                <p className="text-xs font-bold text-amber-700">
                  {RATING_LABELS[rating]} ({rating}/5)
                </p>
              </div>

              {/* 2. Selector Escribir vs Nota de Voz */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-extrabold uppercase tracking-wider text-slate-500">
                    2. Cuéntanos tu experiencia
                  </label>
                </div>

                <div className="grid grid-cols-2 gap-2 bg-slate-100 p-1 rounded-2xl">
                  <button
                    type="button"
                    onClick={() => setMode('TEXT')}
                    className={`flex items-center justify-center space-x-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      mode === 'TEXT'
                        ? 'bg-white text-indigo-700 shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <MessageSquare className="w-4 h-4" />
                    <span>Escribir Opinión</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setMode('AUDIO')}
                    className={`flex items-center justify-center space-x-1.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      mode === 'AUDIO'
                        ? 'bg-white text-indigo-700 shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <Mic className="w-4 h-4" />
                    <span>Nota de Voz</span>
                  </button>
                </div>

                {mode === 'TEXT' ? (
                  <div className="space-y-2.5">
                    {/* Chips de aspectos rápidos */}
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-[11px] text-slate-400">Temas sugeridos:</span>
                      {['El servicio', 'El ambiente', 'La limpieza', 'El tiempo de espera'].map(
                        (tema) => (
                          <button
                            key={tema}
                            type="button"
                            onClick={() => handleInsertChip(tema)}
                            className="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-indigo-50 text-slate-600 hover:text-indigo-700 transition-colors cursor-pointer"
                          >
                            + {tema}
                          </button>
                        )
                      )}
                    </div>

                    <textarea
                      value={texto}
                      onChange={(e) => setTexto(e.target.value)}
                      rows={4}
                      placeholder={`¿Qué te parecieron tus platillos (${order.items
                        .map((i) => i.platillo_nombre)
                        .join(', ')}) y la atención en ${order.mesa}?`}
                      className="w-full text-sm p-3.5 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white leading-relaxed"
                    />
                  </div>
                ) : (
                  <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-3">
                    {audioError && (
                      <div className="p-2.5 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-xs">
                        {audioError}
                      </div>
                    )}

                    {!audioUrl ? (
                      <div className="space-y-3 text-center">
                        {canUseLiveMic && (
                          <div>
                            {!isRecording ? (
                              <button
                                type="button"
                                onClick={startLiveRecording}
                                className="w-full py-3 px-4 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold text-xs shadow-sm flex items-center justify-center space-x-2 cursor-pointer"
                              >
                                <Mic className="w-4 h-4 animate-pulse" />
                                <span>Grabar con Micrófono Ahora</span>
                              </button>
                            ) : (
                              <button
                                type="button"
                                onClick={stopLiveRecording}
                                className="w-full py-3 px-4 bg-slate-900 text-white rounded-xl font-bold text-xs shadow-sm flex items-center justify-center space-x-2 cursor-pointer"
                              >
                                <Square className="w-4 h-4 text-rose-400 fill-current" />
                                <span>Detener Grabación ({formatTime(recordingSeconds)})</span>
                              </button>
                            )}
                          </div>
                        )}

                        <div>
                          <input
                            ref={fileInputRef}
                            type="file"
                            accept="audio/*,.m4a,.mp3,.wav,.webm,.ogg,.mp4"
                            onChange={handleFileChange}
                            disabled={isSubmitting || isRecording}
                            className="hidden"
                            id="diner-audio-input"
                          />
                          <label
                            htmlFor="diner-audio-input"
                            className="w-full py-3 px-4 bg-white border-2 border-indigo-200 hover:border-indigo-400 text-indigo-700 rounded-xl font-bold text-xs flex items-center justify-center space-x-2 cursor-pointer transition-all"
                          >
                            <Upload className="w-4 h-4" />
                            <span>
                              {canUseLiveMic
                                ? 'O subir archivo / nota de voz'
                                : 'Grabar o Adjuntar Nota de Voz del Celular'}
                            </span>
                          </label>
                          <p className="text-[11px] text-slate-400 mt-1.5">
                            Compatible con notas de voz de iPhone y Android
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-white p-3 rounded-xl border border-slate-200 space-y-2.5">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-emerald-700 truncate">
                            ✓ Audio listo ({audioFilename})
                          </span>
                          <button
                            type="button"
                            onClick={clearAudio}
                            className="text-xs text-rose-600 font-semibold flex items-center gap-1 cursor-pointer"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                            <span>Quitar</span>
                          </button>
                        </div>
                        <audio controls src={audioUrl} className="w-full h-9" />
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* 3. Nombre Opcional */}
              <div>
                <label className="block text-xs font-bold text-slate-600 mb-1">
                  Tu nombre (opcional)
                </label>
                <input
                  type="text"
                  value={autorNombre}
                  onChange={(e) => setAutorNombre(e.target.value)}
                  placeholder="Ej. Sofía G."
                  className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white"
                />
              </div>

              {/* Botón de Enviar Opinión */}
              <button
                type="submit"
                disabled={
                  isSubmitting ||
                  (mode === 'TEXT' && !texto.trim()) ||
                  (mode === 'AUDIO' && !audioBlobOrFile)
                }
                className="w-full py-3.5 px-5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-2xl font-black text-sm shadow-md shadow-indigo-500/20 transition-all flex items-center justify-center space-x-2 cursor-pointer"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Enviando tu opinión...</span>
                  </>
                ) : (
                  <>
                    <span>Enviar mi Opinión</span>
                    <Send className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </>
        )}
      </div>

      {/* Pie discreto del Portal del Comensal */}
      <footer className="text-center text-[11px] text-indigo-300/50 pt-6">
        Experiencia Gastronómica &bull; Encuesta Digital de Mesa
      </footer>
    </div>
  );
};
