from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SpeakerGender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class PitchLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class SpeakingStyle(str, Enum):
    NATURAL = "natural"
    EXPRESSIVE = "expressive"
    MONOTONE = "monotone"
    URGENT = "urgent"


class AudioFormat(str, Enum):
    MP3 = "mp3"
    WAV = "wav"


class VoiceMetadata(BaseModel):
    id: str
    name: str
    gender: SpeakerGender
    language: str = "Hindi"
    description: str
    recommended: bool = False
    supported_styles: List[str] = ["natural", "expressive", "monotone", "urgent"]
    sample_text: str
    preview_audio_url: Optional[str] = None


class VoicesListResponse(BaseModel):
    voices: List[VoiceMetadata]
    default_voice: str


class TTSGenerateRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=3000,
        description="Hindi or Hinglish text to be synthesized into speech",
        json_schema_extra={"example": "नमस्ते! हिंदी वॉइस एआई में आपका स्वागत है।"},
    )
    speaker_id: str = Field(
        default="rohit",
        description="Speaker identity (rohit, divya, aman, rani)",
        json_schema_extra={"example": "rohit"},
    )
    speed: float = Field(
        default=1.0,
        ge=0.6,
        le=1.5,
        description="Speech rate/pace multiplier (0.6=slow, 1.0=normal, 1.5=fast)",
    )
    pitch: PitchLevel = Field(
        default=PitchLevel.MODERATE,
        description="Vocal pitch level (low, moderate, high)",
    )
    style: SpeakingStyle = Field(
        default=SpeakingStyle.NATURAL,
        description="Speaking style/emotion",
    )
    audio_format: AudioFormat = Field(
        default=AudioFormat.MP3,
        description="Preferred output audio format",
    )


class TTSGenerateResponse(BaseModel):
    success: bool
    audio_id: str
    speaker_id: str
    speaker_name: str
    text: str
    duration_seconds: float
    sampling_rate: int
    wav_url: str
    mp3_url: str
    created_at: datetime
    generation_time_ms: float
    conditioning_prompt: str


class GenerationUpdateRequest(BaseModel):
    title: Optional[str] = None
    is_favorite: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class HistoryItem(BaseModel):
    id: str
    title: str = ""
    speaker_id: str
    speaker_name: str
    text: str
    duration_seconds: float
    wav_url: str
    mp3_url: str
    created_at: datetime
    speed: float = 1.0
    pitch: str = "moderate"
    style: str = "natural"
    is_favorite: bool = False
    notes: str = ""
    tags: List[str] = []
    updated_at: Optional[datetime] = None


class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    favorites_count: int = 0


class HealthResponse(BaseModel):
    status: str
    model_name: str
    model_loaded: bool
    device: str
    gpu_available: bool
    gpu_name: Optional[str] = None
    cpu_cores: int
    uptime_seconds: float
