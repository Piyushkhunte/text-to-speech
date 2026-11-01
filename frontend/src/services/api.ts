import {
  HealthResponse,
  HistoryResponse,
  TTSGenerateRequest,
  TTSGenerateResponse,
  VoicesListResponse,
} from '@/types/tts';

// Point directly to backend or through Next.js proxy
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/api/tts/health`, {
    cache: 'no-store',
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch health: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchVoices(): Promise<VoicesListResponse> {
  const res = await fetch(`${API_BASE}/api/tts/voices`, {
    cache: 'no-store',
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch voices: ${res.statusText}`);
  }
  return res.json();
}

export async function generateSpeech(
  req: TTSGenerateRequest
): Promise<TTSGenerateResponse> {
  const res = await fetch(`${API_BASE}/api/tts/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || 'Speech synthesis failed');
  }

  return res.json();
}

export interface FetchHistoryParams {
  search?: string;
  speaker?: string;
  favorite?: boolean;
}

export async function fetchHistory(params?: FetchHistoryParams): Promise<HistoryResponse> {
  const query = new URLSearchParams();
  if (params?.search) query.set('search', params.search);
  if (params?.speaker && params.speaker !== 'all') query.set('speaker', params.speaker);
  if (params?.favorite !== undefined) query.set('favorite', String(params.favorite));

  const url = `${API_BASE}/api/tts/history${query.toString() ? `?${query.toString()}` : ''}`;
  const res = await fetch(url, {
    cache: 'no-store',
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch history: ${res.statusText}`);
  }
  return res.json();
}

export async function updateHistoryItem(
  audioId: string,
  updates: {
    title?: string;
    is_favorite?: boolean;
    notes?: string;
    tags?: string[];
  }
) {
  const res = await fetch(`${API_BASE}/api/tts/history/${audioId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updates),
  });
  if (!res.ok) {
    throw new Error(`Failed to update history item: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteHistoryItem(audioId: string): Promise<boolean> {
  const res = await fetch(`${API_BASE}/api/tts/history/${audioId}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error(`Failed to delete history item: ${res.statusText}`);
  }
  const data = await res.json();
  return data.success;
}

export function getAudioDownloadUrl(audioId: string, format: 'wav' | 'mp3'): string {
  return `${API_BASE}/api/tts/audio/${audioId}?format=${format}&download=true`;
}

export function getAudioStreamUrl(audioId: string, format: 'wav' | 'mp3'): string {
  return `${API_BASE}/api/tts/audio/${audioId}?format=${format}`;
}

export function getSpeakerPreviewUrl(speakerId: string): string {
  return `${API_BASE}/api/tts/preview/${speakerId}`;
}
