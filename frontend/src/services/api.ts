import type {
  Dish,
  Review,
  RankingResponse,
  TrendsResponse,
  TextReviewPayload,
  Order,
  OrderCreatePayload,
} from '../types';

const API_BASE = '/api/v1';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `Error HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map((d: { msg?: string }) => d.msg || JSON.stringify(d)).join(', ');
        } else {
          errorMessage = JSON.stringify(errorData.detail);
        }
      }
    } catch {
      // response is not JSON
    }
    throw new Error(errorMessage);
  }
  return response.json() as Promise<T>;
}

export const api = {
  // Platillos
  getDishes: async (): Promise<Dish[]> => {
    const res = await fetch(`${API_BASE}/dishes`);
    return handleResponse<Dish[]>(res);
  },

  // Pedidos y QR (Mesero)
  createOrder: async (payload: OrderCreatePayload): Promise<Order> => {
    const res = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    return handleResponse<Order>(res);
  },

  getOrders: async (limit: number = 20): Promise<Order[]> => {
    const res = await fetch(`${API_BASE}/orders?limit=${limit}`);
    return handleResponse<Order[]>(res);
  },

  getOrderByToken: async (qrToken: string): Promise<Order> => {
    const res = await fetch(`${API_BASE}/orders/by-token/${encodeURIComponent(qrToken)}`);
    return handleResponse<Order>(res);
  },

  // Reseña de texto
  submitTextReview: async (payload: TextReviewPayload): Promise<Review> => {
    const res = await fetch(`${API_BASE}/reviews/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    return handleResponse<Review>(res);
  },

  // Reseña de audio
  submitAudioReview: async (formData: FormData): Promise<Review> => {
    const res = await fetch(`${API_BASE}/reviews/upload-audio`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse<Review>(res);
  },

  // Analíticas y Ranking
  getRanking: async (): Promise<RankingResponse> => {
    const res = await fetch(`${API_BASE}/analytics/ranking`);
    return handleResponse<RankingResponse>(res);
  },

  // `dias` es el tamaño de la ventana: el backend compara los últimos `dias` días
  // contra los `dias` días inmediatamente anteriores.
  getTrends: async (dias: number = 7): Promise<TrendsResponse> => {
    const res = await fetch(`${API_BASE}/analytics/trends?dias=${dias}`);
    return handleResponse<TrendsResponse>(res);
  },

  // Reset administrativo de la BD
  resetDatabase: async (): Promise<{ status: string; message: string }> => {
    const res = await fetch(`${API_BASE}/admin/reset-database`, {
      method: 'POST',
    });
    return handleResponse<{ status: string; message: string }>(res);
  },
};
