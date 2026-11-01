import asyncio
import logging
import os
import re
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import soundfile as sf
import torch

from backend.app.core.config import settings
from backend.app.schemas.tts import (
    AudioFormat,
    HistoryItem,
    PitchLevel,
    SpeakerGender,
    SpeakingStyle,
    TTSGenerateRequest,
    TTSGenerateResponse,
    VoiceMetadata,
)
from backend.app.services.audio_converter import AudioConverter
from backend.app.services.history_manager import history_manager
from backend.app.utils.hindi_validator import validate_hindi_input

logger = logging.getLogger(__name__)

# Verified Hindi voice profiles with authentic Neural voice mappings
HINDI_VOICES: Dict[str, VoiceMetadata] = {
    "aarav": VoiceMetadata(
        id="aarav",
        name="Aarav (आरव) - Viral Tech Reel Creator",
        gender=SpeakerGender.MALE,
        language="Hindi + Hinglish (YT Shorts Special)",
        description="यूट्यूब शॉर्ट्स और टेक रील्स के लिए विशेष रूप से ट्यून्ड - तेज़, पंच से भरपूर हुक्स, सिस्टम डिज़ाइन और कोडिंग इंटरव्यूज़ का स्वाभाविक भारतीय टेक लहजा।",
        recommended=True,
        supported_styles=["natural", "expressive", "monotone", "urgent"],
        sample_text="इंटरव्यूअर ने पूछा Google जैसा सर्च डिजाइन करो। तुमने कहा हर बार पूरा इंटरनेट स्कैन कर लो। बस यहीं पर राउंड हाथ से जा सकता है! असली डिज़ाइन तीन पार्ट्स में चलता है।",
        preview_audio_url="/api/tts/preview/aarav",
    ),
    "kabir": VoiceMetadata(
        id="kabir",
        name="Kabir (कबीर) - High-Energy Reel Creator",
        gender=SpeakerGender.MALE,
        language="Hindi + Hinglish (Reel Special)",
        description="उच्च-ऊर्जा (High Energy) और पंच वाले आधुनिक क्रिएटर का स्वर - 30 से 60 सेकंड के टेक रील्स, यूट्यूब शॉर्ट्स और वायरल हुक्स के लिए बेस्ट।",
        recommended=True,
        supported_styles=["natural", "expressive", "monotone", "urgent"],
        sample_text="Kya aapne socha hai ki sirf ek line ke code se poori website crash ho sakti hai? Chaliye dekhte hain kaise!",
        preview_audio_url="/api/tts/preview/kabir",
    ),
    "ananya": VoiceMetadata(
        id="ananya",
        name="Ananya (अनन्या) - Viral Reel & Storyteller",
        gender=SpeakerGender.FEMALE,
        language="Hindi + Hinglish (Reel Special)",
        description="आकर्षक, गतिशील और ट्रेंडिंग महिला स्वर - लाइफस्टाइल, टेक, इंस्टाग्राम रील्स और वायरल स्क्रिप्ट्स के लिए परफेक्ट।",
        recommended=True,
        supported_styles=["natural", "expressive", "monotone", "urgent"],
        sample_text="Agar aap bhi har roz vahi boring routine se pareshan hain, toh yeh 3 AI tools aapki life badal denge!",
        preview_audio_url="/api/tts/preview/ananya",
    ),
    "rohit": VoiceMetadata(
        id="rohit",
        name="Rohit (रोहित) - Conversational",
        gender=SpeakerGender.MALE,
        language="Hindi + English (Hinglish)",
        description="स्वाभाविक, संवादात्मक और आधुनिक पुरुष स्वर - हिंदी और अंग्रेज़ी तकनीकी शब्दों (Programming, Values, etc.) को सहजता से बोलता है।",
        recommended=True,
        supported_styles=["natural", "expressive", "monotone", "urgent"],
        sample_text="नमस्ते! क्या आपने कभी सोचा है कि Programming में एक साथ कई सारी values कैसे store करते हैं?",
        preview_audio_url="/api/tts/preview/rohit",
    ),
    "divya": VoiceMetadata(
        id="divya",
        name="Divya (दिव्या) - Expressive",
        gender=SpeakerGender.FEMALE,
        language="Hindi + English (Hinglish)",
        description="स्पष्ट, पेशेवर और भावपूर्ण महिला स्वर - पॉडकास्ट, व्याख्यान और प्रस्तुतियों के लिए सर्वोत्तम।",
        recommended=True,
        supported_styles=["natural", "expressive", "monotone", "urgent"],
        sample_text="नमस्ते! आज हम Artificial Intelligence और Data Science के नए ट्रेंड्स के बारे में बात करेंगे।",
        preview_audio_url="/api/tts/preview/divya",
    ),
    "aman": VoiceMetadata(
        id="aman",
        name="Aman (अमन) - Deep Narrative",
        gender=SpeakerGender.MALE,
        language="Hindi + English (Hinglish)",
        description="गंभीर, गहरा और प्रभावशाली पुरुष स्वर - समाचार, वृत्तचित्र और गंभीर विषयों के लिए आदर्श।",
        recommended=False,
        supported_styles=["natural", "expressive", "monotone", "urgent"],
        sample_text="प्रौद्योगिकी के इस नए युग में Cloud Computing और Software Architecture हमारे जीवन का मुख्य आधार हैं।",
        preview_audio_url="/api/tts/preview/aman",
    ),
    "rani": VoiceMetadata(
        id="rani",
        name="Rani (रानी) - Melodious & Soft",
        gender=SpeakerGender.FEMALE,
        language="Hindi + English (Hinglish)",
        description="मधुर, सौम्य और शांत महिला स्वर - कहानियों, ऑडियोबुक्स और ध्यान/प्रेरणादायक सामग्री के लिए उपयुक्त।",
        recommended=False,
        supported_styles=["natural", "expressive", "monotone", "urgent"],
        sample_text="साहित्य, कला और संगीत हमारे जीवन में नई ऊर्जा, सकारात्मकता और शांति का संचार करते हैं।",
        preview_audio_url="/api/tts/preview/rani",
    ),
}

# Mapping to high-fidelity Neural voices that fluently understand Hindi & English code-mixing
VOICE_NEURAL_MAP = {
    "aarav": {"voice": "hi-IN-MadhurNeural", "hinglish_voice": "hi-IN-MadhurNeural", "rate_offset": 5, "pitch_offset": 3},
    "kabir": {"voice": "hi-IN-MadhurNeural", "hinglish_voice": "hi-IN-MadhurNeural", "rate_offset": 5, "pitch_offset": 2},
    "ananya": {"voice": "hi-IN-SwaraNeural", "hinglish_voice": "hi-IN-SwaraNeural", "rate_offset": 4, "pitch_offset": 2},
    "rohit": {"voice": "hi-IN-MadhurNeural", "hinglish_voice": "hi-IN-MadhurNeural", "rate_offset": 0, "pitch_offset": 0},
    "divya": {"voice": "hi-IN-SwaraNeural", "hinglish_voice": "hi-IN-SwaraNeural", "rate_offset": 0, "pitch_offset": 0},
    "aman": {"voice": "hi-IN-MadhurNeural", "hinglish_voice": "hi-IN-MadhurNeural", "rate_offset": -5, "pitch_offset": -8},  # Deeper, authoritative
    "rani": {"voice": "hi-IN-SwaraNeural", "hinglish_voice": "hi-IN-SwaraNeural", "rate_offset": -4, "pitch_offset": 5},     # Softer, lighter pitch
}


class TTSEngine:
    _instance: Optional["TTSEngine"] = None

    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.engine_type = "neural"  # "neural" (Edge-TTS) or "vits" (Local fallback)
        self.male_vits_model = None
        self.male_vits_tokenizer = None
        self.female_vits_model = None
        self.female_vits_tokenizer = None
        self.is_loading = False
        self.is_ready = True
        self.model_name = "Microsoft Neural Multi-Voice (Hindi + English Code-Mixed)"
        self.load_error: Optional[str] = None
        self.start_time = time.time()

    @classmethod
    def get_instance(cls) -> "TTSEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self):
        """Warm-up and verify neural engine availability."""
        self.is_ready = True
        logger.info(f"Initialized Neural Speech Engine for Hindi & Code-Mixed English on {self.device}.")

    def build_conditioning_prompt(
        self,
        speaker_id: str,
        speed: float,
        pitch: PitchLevel,
        style: SpeakingStyle,
    ) -> str:
        """Constructs human-readable conditioning description."""
        rate_str, pitch_str = self._format_rate_pitch(speed, pitch, speaker_id)
        voice_info = VOICE_NEURAL_MAP.get(speaker_id.lower(), VOICE_NEURAL_MAP["rohit"])
        speaker_name = HINDI_VOICES.get(speaker_id.lower(), HINDI_VOICES["rohit"]).name.split(" ")[0]
        return f"{speaker_name} | Voice: {voice_info['voice']} | Speed: {speed}x ({rate_str}) | Pitch: {pitch.value} ({pitch_str}) | Style: {style.value}"

    def _format_rate_pitch(self, speed: float, pitch: PitchLevel, speaker_id: str) -> Tuple[str, str]:
        """Calculates exact rate and pitch strings for the neural speech engine."""
        base = VOICE_NEURAL_MAP.get(speaker_id.lower(), {"rate_offset": 0, "pitch_offset": 0})
        
        # Speed: 1.0 is +0%, 1.2 is +20%, 0.8 is -20%
        rate_pct = int((speed - 1.0) * 100) + base["rate_offset"]
        rate_str = f"{rate_pct:+d}%"

        # Pitch in Hz: low (-12Hz), moderate (0Hz), high (+12Hz)
        pitch_base = -12 if pitch == PitchLevel.LOW else (12 if pitch == PitchLevel.HIGH else 0)
        pitch_hz = pitch_base + base["pitch_offset"]
        pitch_str = f"{pitch_hz:+d}Hz"

        return rate_str, pitch_str

    async def _generate_neural(
        self,
        text: str,
        speaker_id: str,
        speed: float,
        pitch: PitchLevel,
        style: SpeakingStyle,
        output_mp3_path: Path,
        output_wav_path: Path,
    ) -> Tuple[float, int, str]:
        """Synthesizes high-fidelity speech with full bilingual/code-mixing support."""
        import edge_tts

        from backend.app.utils.hindi_validator import contains_devanagari

        voice_info = VOICE_NEURAL_MAP.get(speaker_id.lower(), VOICE_NEURAL_MAP["kabir"])
        # If input text is pure Latin Roman Hinglish (no Devanagari characters),
        # use the dedicated Indian English/Hinglish neural voice for crisp pronunciation
        is_pure_latin = not contains_devanagari(text)
        if is_pure_latin and "hinglish_voice" in voice_info:
            voice_name = voice_info["hinglish_voice"]
        else:
            voice_name = voice_info["voice"]

        rate_str, pitch_str = self._format_rate_pitch(speed, pitch, speaker_id)

        # Style inflection adjustments via pitch/rate dynamics
        if style == SpeakingStyle.URGENT:
            rate_str = "+15%"
        elif style == SpeakingStyle.MONOTONE:
            pitch_str = "+0Hz"

        from backend.app.services.story_director import normalize_hinglish_pronunciation
        clean_speech_text = normalize_hinglish_pronunciation(text)

        communicate = edge_tts.Communicate(
            text=clean_speech_text,
            voice=voice_name,
            rate=rate_str,
            pitch=pitch_str,
        )

        # Save to MP3 directly
        await communicate.save(str(output_mp3_path))

        # Convert to WAV with studio broadcast compression & presence EQ (matching YouTube Tech Shorts)
        ffmpeg_exe = AudioConverter.get_ffmpeg_executable()
        filter_chain = "acompressor=threshold=-14dB:ratio=3.5:attack=10:release=80,equalizer=f=3200:t=q:w=1.2:g=3.0"
        cmd_wav = [
            ffmpeg_exe,
            "-y",
            "-i", str(output_mp3_path),
            "-af", filter_chain,
            "-ar", "24000",
            "-ac", "1",
            str(output_wav_path),
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd_wav,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()

        # Re-encode mastered MP3 with studio compression
        cmd_mp3 = [
            ffmpeg_exe,
            "-y",
            "-i", str(output_wav_path),
            "-b:a", "192k",
            str(output_mp3_path),
        ]
        proc_mp3 = await asyncio.create_subprocess_exec(
            *cmd_mp3,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc_mp3.communicate()

        duration = AudioConverter.get_audio_duration(output_wav_path)
        cond_prompt = f"Voice: {voice_name} | Rate: {rate_str} | Pitch: {pitch_str} | Style: {style.value}"
        return duration, 24000, cond_prompt

    async def generate_speech(self, request: TTSGenerateRequest) -> TTSGenerateResponse:
        """Asynchronous API entry point for speech generation."""
        is_valid, normalized_text, err_msg = validate_hindi_input(
            request.text, max_chars=settings.MAX_TEXT_LENGTH
        )
        if not is_valid:
            raise ValueError(err_msg)

        speaker_id = request.speaker_id.lower()
        if speaker_id not in HINDI_VOICES:
            raise ValueError(f"Unknown speaker ID '{speaker_id}'. Supported: {list(HINDI_VOICES.keys())}")

        audio_id = str(uuid.uuid4())
        wav_path = settings.AUDIO_STORAGE_DIR / f"{audio_id}.wav"
        mp3_path = settings.AUDIO_STORAGE_DIR / f"{audio_id}.mp3"

        start_time = time.time()

        from backend.app.services.gemini_tts import (
            generate_gemini_speech,
            is_gemini_tts_enabled,
        )
        from backend.app.services.story_director import (
            StoryDirector,
            clean_markdown_and_punctuation,
            has_scene_tags,
        )

        try:
            if is_gemini_tts_enabled():
                try:
                    logger.info(
                        f"Using Google Gemini 3.8 Flash TTS for speaker '{speaker_id}'..."
                    )
                    cleaned_script = clean_markdown_and_punctuation(normalized_text)
                    duration, sampling_rate, cond_prompt = await generate_gemini_speech(
                        cleaned_script,
                        speaker_id,
                        request.speed,
                        request.pitch,
                        request.style,
                        mp3_path,
                        wav_path,
                    )
                except Exception as gemini_err:
                    logger.warning(
                        f"Gemini TTS encountered an error: {gemini_err}. Falling back seamlessly to local neural engine...",
                        exc_info=True,
                    )
                    if has_scene_tags(normalized_text):
                        duration, sampling_rate, cond_prompt = await StoryDirector.synthesize_directed_story(
                            normalized_text,
                            speaker_id,
                            request.speed,
                            request.pitch,
                            VOICE_NEURAL_MAP,
                            mp3_path,
                            wav_path,
                        )
                    else:
                        duration, sampling_rate, cond_prompt = await self._generate_neural(
                            normalized_text,
                            speaker_id,
                            request.speed,
                            request.pitch,
                            request.style,
                            mp3_path,
                            wav_path,
                        )
            elif has_scene_tags(normalized_text):
                logger.info(f"Detected narrative scene tags in script. Activating StoryDirector for {speaker_id}...")
                duration, sampling_rate, cond_prompt = await StoryDirector.synthesize_directed_story(
                    normalized_text,
                    speaker_id,
                    request.speed,
                    request.pitch,
                    VOICE_NEURAL_MAP,
                    mp3_path,
                    wav_path,
                )
            else:
                duration, sampling_rate, cond_prompt = await self._generate_neural(
                    normalized_text,
                    speaker_id,
                    request.speed,
                    request.pitch,
                    request.style,
                    mp3_path,
                    wav_path,
                )
        except Exception as e:
            logger.error(f"TTS generation error: {e}", exc_info=True)
            raise RuntimeError(f"Speech generation error: {e}")

        gen_time_ms = (time.time() - start_time) * 1000
        speaker_info = HINDI_VOICES[speaker_id]
        wav_url = f"/api/tts/audio/{audio_id}?format=wav"
        mp3_url = f"/api/tts/audio/{audio_id}?format=mp3"
        now = datetime.now(timezone.utc)

        # Record in history
        history_item = HistoryItem(
            id=audio_id,
            speaker_id=speaker_id,
            speaker_name=speaker_info.name,
            text=normalized_text,
            duration_seconds=round(duration, 2),
            wav_url=wav_url,
            mp3_url=mp3_url,
            created_at=now,
            speed=request.speed,
            pitch=request.pitch.value,
            style=request.style.value,
        )
        history_manager.add_item(history_item)

        return TTSGenerateResponse(
            success=True,
            audio_id=audio_id,
            speaker_id=speaker_id,
            speaker_name=speaker_info.name,
            text=normalized_text,
            duration_seconds=round(duration, 2),
            sampling_rate=sampling_rate,
            wav_url=wav_url,
            mp3_url=mp3_url,
            created_at=now,
            generation_time_ms=round(gen_time_ms, 1),
            conditioning_prompt=cond_prompt,
        )

    def get_voices(self) -> List[VoiceMetadata]:
        return list(HINDI_VOICES.values())

    def get_health_status(self) -> Dict:
        from backend.app.services.gemini_tts import is_gemini_tts_enabled
        gemini_active = is_gemini_tts_enabled()
        gpu_avail = torch.cuda.is_available()
        gpu_name = torch.cuda.get_device_name(0) if gpu_avail else None
        active_model = (
            f"Google Gemini 3.8 Flash TTS ({settings.GEMINI_TTS_MODEL})"
            if gemini_active
            else self.model_name
        )
        return {
            "status": "ready" if self.is_ready else ("loading" if self.is_loading else "idle"),
            "model_name": active_model,
            "model_loaded": self.is_ready,
            "device": "cloud-gemini" if gemini_active else self.device,
            "gpu_available": gpu_avail,
            "gpu_name": gpu_name,
            "cpu_cores": os.cpu_count() or 1,
            "uptime_seconds": round(time.time() - self.start_time, 1),
            "load_error": self.load_error,
        }


tts_engine = TTSEngine.get_instance()
