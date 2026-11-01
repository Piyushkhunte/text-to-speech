export type SpeakerGender = 'male' | 'female';
export type PitchLevel = 'low' | 'moderate' | 'high';
export type SpeakingStyle = 'natural' | 'expressive' | 'monotone' | 'urgent';
export type AudioFormat = 'mp3' | 'wav';

export interface VoiceMetadata {
  id: string;
  name: string;
  gender: SpeakerGender;
  language: string;
  description: string;
  recommended: boolean;
  supported_styles: string[];
  sample_text: string;
  preview_audio_url?: string;
}

export interface VoicesListResponse {
  voices: VoiceMetadata[];
  default_voice: string;
}

export interface TTSGenerateRequest {
  text: string;
  speaker_id: string;
  speed: number;
  pitch: PitchLevel;
  style: SpeakingStyle;
  audio_format: AudioFormat;
}

export interface TTSGenerateResponse {
  success: boolean;
  audio_id: string;
  speaker_id: string;
  speaker_name: string;
  text: string;
  duration_seconds: number;
  sampling_rate: number;
  wav_url: string;
  mp3_url: string;
  created_at: string;
  generation_time_ms: number;
  conditioning_prompt: string;
}

export interface HistoryItem {
  id: string;
  title?: string;
  speaker_id: string;
  speaker_name: string;
  text: string;
  duration_seconds: number;
  wav_url: string;
  mp3_url: string;
  created_at: string;
  speed: number;
  pitch: string;
  style: string;
  is_favorite?: boolean;
  notes?: string;
  tags?: string[];
  updated_at?: string;
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  favorites_count?: number;
}

export interface HealthResponse {
  status: string;
  model_name: string;
  model_loaded: boolean;
  device: string;
  gpu_available: boolean;
  gpu_name?: string | null;
  cpu_cores: number;
  uptime_seconds: number;
  load_error?: string | null;
}
