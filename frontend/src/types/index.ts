export interface Dish {
  id: string;
  nombre: string;
  categoria: string;
  descripcion?: string | null;
  precio: number;
  activo: boolean;
  created_at?: string;
}

export interface AttributeMention {
  id: string;
  categoria_atributo: string;
  valor_mencionado: string;
  polaridad: string;
  created_at?: string;
}

export interface Sentiment {
  id: string;
  platillo_id?: string | null;
  platillo_nombre_referenciado: string;
  polaridad: 'positivo' | 'negativo' | 'neutral';
  score_numerico: number;
  fragmento_texto?: string | null;
  justificacion?: string | null;
  created_at?: string;
  atributos: AttributeMention[];
}

export interface EstablishmentSentiment {
  id: string;
  categoria: 'servicio' | 'ambiente' | 'limpieza' | 'tiempo_espera' | string;
  polaridad: 'positivo' | 'negativo' | 'neutral';
  score_numerico: number;
  fragmento_texto?: string | null;
  valor_mencionado: string;
  created_at?: string;
}

export interface AudioTranscription {
  id: string;
  audio_path: string;
  duracion_segundos?: number | null;
  texto_transcrito: string;
  confianza?: number | null;
  idioma_detectado: string;
  estado_procesamiento: string;
  created_at?: string;
}

export interface Review {
  id: string;
  canal_origen: string;
  tipo_input: string;
  calificacion_general?: number | null;
  autor_nombre?: string | null;
  texto_original: string;
  fecha_resena: string;
  created_at: string;
  estado_analisis?: string;
  pedido_id?: string | null;
  transcripcion?: AudioTranscription | null;
  sentimientos: Sentiment[];
  sentimientos_establecimiento?: EstablishmentSentiment[];
}

export interface OrderItem {
  id: string;
  platillo_id: string;
  platillo_nombre: string;
  platillo_categoria: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

export interface Order {
  id: string;
  qr_token: string;
  mesa?: string | null;
  total: number;
  estado: string;
  created_at: string;
  items: OrderItem[];
  total_resenas: number;
}

export interface OrderCreatePayload {
  mesa?: string;
  items: { platillo_id: string; cantidad: number }[];
}

export interface DishRankingItem {
  platillo_id: string;
  nombre: string;
  categoria: string;
  total_menciones: number;
  positivas: number;
  negativas: number;
  neutrales: number;
  score_ponderado: number;
  tasa_positiva: number;
  tasa_negativa: number;
}

export interface RankingResponse {
  total_evaluaciones: number;
  top_platillos: DishRankingItem[];
  platillos_en_riesgo: DishRankingItem[];
}

export interface AttributeFrequencyItem {
  categoria_atributo: string;
  total_menciones: number;
  positivas: number;
  negativas: number;
  neutrales: number;
  ejemplos_valores: string[];
}

export interface DishTrendItem {
  platillo_id: string;
  nombre: string;
  menciones_periodo_reciente: number;
  score_polaridad_reciente: number | null;
  menciones_periodo_previo: number;
  score_polaridad_previo: number | null;
  cambio_polaridad: number | null;
  tendencia: string;
  atributos_destacados: AttributeFrequencyItem[];
}

export interface EstablishmentTrendsSummary {
  total_menciones: number;
  positivas: number;
  negativas: number;
  neutrales: number;
  categorias: AttributeFrequencyItem[];
}

export interface TrendsResponse {
  periodo_dias: number;
  fecha_corte: string;
  tendencias_por_platillo: DishTrendItem[];
  atributos_mas_mencionados_global: AttributeFrequencyItem[];
  menciones_sin_clasificar: {
    total_menciones: number;
    positivas: number;
    negativas: number;
    neutrales: number;
    atributos_asociados: AttributeFrequencyItem[];
  };
  sentimientos_establecimiento?: EstablishmentTrendsSummary;
}

export interface TextReviewPayload {
  texto: string;
  canal_origen?: string;
  calificacion_general?: number | null;
  autor_nombre?: string;
  qr_token?: string;
}
