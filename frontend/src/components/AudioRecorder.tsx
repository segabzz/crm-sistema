import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Trash2, Upload, Volume2, AlertCircle } from 'lucide-react';

interface AudioRecorderProps {
  onAudioSelected: (audioFile: File | Blob, filename: string) => void;
  onClear: () => void;
  disabled?: boolean;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onAudioSelected,
  onClear,
  disabled = false,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioFilename, setAudioFilename] = useState<string>('');
  const [micError, setMicError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  const startRecording = async () => {
    setMicError(null);
    audioChunksRef.current = [];

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Tu navegador no soporta grabación directa de micrófono.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Determinar mimeType compatible (WebM con fallback)
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

      const options = mimeType ? { mimeType } : undefined;
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const mime = mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: mime });
        const ext = mime.includes('mp4') ? 'mp4' : 'webm';
        const filename = `grabacion_${Date.now()}.${ext}`;

        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        setAudioFilename(filename);
        onAudioSelected(audioBlob, filename);

        // Detener tracks del stream de audio para liberar el micrófono
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start(250); // Emitir chunks cada 250ms
      setIsRecording(true);
      setRecordingDuration(0);

      timerRef.current = window.setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      console.error('Error al acceder al micrófono:', err);
      setMicError(
        err.message ||
          'No se pudo acceder al micrófono. Por favor verifica los permisos o sube un archivo de audio.'
      );
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const handleClear = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioUrl(null);
    setAudioFilename('');
    setRecordingDuration(0);
    audioChunksRef.current = [];
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onClear();
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMicError(null);
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      setAudioFilename(file.name);
      onAudioSelected(file, file.name);
    }
  };

  const formatSeconds = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Volume2 className="w-5 h-5 text-indigo-600" />
          <h3 className="text-sm font-semibold text-slate-800">
            Grabación de Audio / Micrófono
          </h3>
        </div>
        <span className="text-xs font-mono bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-200">
          Native WebM / Opus & Faster-Whisper
        </span>
      </div>

      {micError && (
        <div className="flex items-start space-x-2 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{micError}</span>
        </div>
      )}

      {/* Controles de grabación */}
      {!audioUrl ? (
        <div className="flex flex-col sm:flex-row items-center gap-4">
          {!isRecording ? (
            <button
              type="button"
              disabled={disabled}
              onClick={startRecording}
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 cursor-pointer"
            >
              <Mic className="w-4 h-4 animate-pulse" />
              <span>Iniciar Grabación</span>
            </button>
          ) : (
            <div className="w-full sm:w-auto flex items-center space-x-3">
              <button
                type="button"
                onClick={stopRecording}
                className="inline-flex items-center space-x-2 px-5 py-2.5 bg-slate-900 hover:bg-black text-white rounded-lg font-medium shadow-sm transition-colors cursor-pointer"
              >
                <Square className="w-4 h-4 text-red-400 fill-current" />
                <span>Detener Grabación ({formatSeconds(recordingDuration)})</span>
              </button>
              <div className="flex items-center space-x-1.5">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                </span>
                <span className="text-xs text-red-600 font-semibold uppercase tracking-wider">
                  Grabando
                </span>
              </div>
            </div>
          )}

          <div className="text-xs text-slate-400 font-medium">o bien</div>

          {/* Subir archivo de audio directamente */}
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*,.webm,.wav,.mp3,.m4a,.ogg"
              onChange={handleFileUpload}
              disabled={disabled || isRecording}
              className="hidden"
              id="audio-file-input"
            />
            <label
              htmlFor="audio-file-input"
              className={`inline-flex items-center space-x-2 px-4 py-2.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                disabled || isRecording ? 'opacity-50 pointer-events-none' : ''
              }`}
            >
              <Upload className="w-4 h-4 text-slate-500" />
              <span>Subir archivo de audio</span>
            </label>
          </div>
        </div>
      ) : (
        /* Vista previa del audio capturado */
        <div className="p-4 bg-white border border-slate-200 rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 truncate">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span className="text-xs font-medium text-slate-700 truncate">
                {audioFilename || 'Audio capturado listo para transcribir'}
              </span>
            </div>
            <button
              type="button"
              disabled={disabled}
              onClick={handleClear}
              className="inline-flex items-center space-x-1 text-xs text-red-600 hover:text-red-700 p-1 hover:bg-red-50 rounded transition-colors cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Descartar</span>
            </button>
          </div>

          <audio controls src={audioUrl} className="w-full h-9" />
        </div>
      )}
    </div>
  );
};
