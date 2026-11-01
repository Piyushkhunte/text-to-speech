import asyncio
import base64
import logging
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

import imageio_ffmpeg
from backend.app.core.config import settings
from backend.app.schemas.tts import PitchLevel, SpeakingStyle
from backend.app.services.audio_converter import AudioConverter
from backend.app.services.story_director import normalize_hinglish_pronunciation

logger = logging.getLogger(__name__)

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

# Mapping between HindiVoice AI speakers and Google Gemini 3.8 Flash TTS voices
GEMINI_VOICE_MAP: Dict[str, Dict[str, str]] = {
    "aarav": {
        "voice": "Puck",
        "style": "curious, energetic, fast-paced Indian tech reel creator speaking natural Hindi and Hinglish",
    },
    "kabir": {
        "voice": "Charon",
        "style": "punchy, confident, high-energy Indian tech influencer speaking Hindi with modern cadence",
    },
    "ananya": {
        "voice": "Aoede",
        "style": "expressive, engaging, vibrant female storyteller in Hindi with enthusiastic reel tone",
    },
    "rohit": {
        "voice": "Rasalgethi",
        "style": "clear, warm, conversational Hindi educator explaining concepts smoothly",
    },
    "divya": {
        "voice": "Kore",
        "style": "articulate, polished, friendly Hindi female explainer with professional studio clarity",
    },
    "aman": {
        "voice": "Algenib",
        "style": "deep, authoritative, cinematic documentary narrator speaking resonant Hindi",
    },
    "rani": {
        "voice": "Sulafat",
        "style": "gentle, soft, melodious Hindi storytelling voice with emotional depth",
    },
}


def get_gemini_api_key() -> str:
    """
    Retrieves Gemini API key from environment variables or .env file.
    """
    # 1. Check OS / process environment first (e.g. test monkeypatch or export)
    val = os.environ.get("GEMINI_API_KEY", "").strip()
    if val and not val.startswith("AQ."):
        return val

    # 2. Check settings (loaded via pydantic-settings from .env)
    if settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("AQ."):
        return settings.GEMINI_API_KEY.strip()

    # 3. Read directly from .env files
    env_paths = [
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
    ]
    for p in env_paths:
        if p.exists():
            try:
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                        file_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if file_val and not file_val.startswith("AQ."):
                            return file_val
            except Exception:
                pass

    return ""


def is_gemini_tts_enabled() -> bool:
    """Returns True if a valid-looking Gemini API key is configured."""
    key = get_gemini_api_key()
    return bool(key and len(key) >= 15)


def generate_gemini_tts_sync(
    text: str,
    speaker_id: str,
    speed: float,
    pitch: PitchLevel,
    style: SpeakingStyle,
    output_mp3_path: Path,
    output_wav_path: Path,
) -> Tuple[float, int, str]:
    """
    Synchronous speech generation using Google Gemini 3.8 Flash TTS (gemini-3.8-flash-tts).
    Requires GEMINI_API_KEY in .env or environment.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in .env or environment")

    # Set environment variables so the SDK is consistently authenticated
    os.environ["GEMINI_API_KEY"] = api_key
    os.environ["GOOGLE_API_KEY"] = api_key

    from google import genai

    client = genai.Client(api_key=api_key)

    mapping = GEMINI_VOICE_MAP.get(speaker_id.lower(), GEMINI_VOICE_MAP["aarav"])
    gemini_voice = mapping["voice"]
    style_desc = mapping["style"]

    # Pre-clean pronunciation traps
    clean_text = normalize_hinglish_pronunciation(text)

    # Annotate with turn-level speech_metadata
    prompt_style = f"{style_desc}, style: {style.value}"

    logger.info(
        f"Calling Google Gemini 3.8 Flash TTS ({settings.GEMINI_TTS_MODEL}) "
        f"with voice '{gemini_voice}' for speaker '{speaker_id}'..."
    )

    interaction = client.interactions.create(
        model=settings.GEMINI_TTS_MODEL,
        input=[{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": clean_text,
                "annotations": [{
                    "type": "speech_metadata",
                    "style": prompt_style,
                }],
            }],
        }],
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": gemini_voice},
            ]
        },
    )

    if not interaction.output_audio or not interaction.output_audio.data:
        raise RuntimeError("Gemini TTS response did not contain audio data")

    # Decode audio binary data (base64)
    raw_wav_bytes = base64.b64decode(interaction.output_audio.data)

    temp_raw_wav = output_wav_path.parent / f"gemini_raw_{output_wav_path.stem}.wav"
    try:
        with open(temp_raw_wav, "wb") as f:
            f.write(raw_wav_bytes)

        # Build FFmpeg filter chain (speed adjustment + mastering)
        filters = []
        if speed and abs(speed - 1.0) > 0.05:
            filters.append(f"atempo={speed:.2f}")

        # Broadcast mastering: light presence EQ and peak limiter
        filters.append("equalizer=f=3200:t=q:w=1.2:g=2.5")
        filters.append("alimiter=limit=-1dB")

        filter_str = ",".join(filters)

        # Generate mastered WAV
        cmd_wav = [
            ffmpeg_exe,
            "-y",
            "-i", str(temp_raw_wav),
            "-af", filter_str,
            "-ar", "24000",
            "-ac", "1",
            str(output_wav_path),
        ]
        subprocess.run(cmd_wav, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Generate mastered MP3
        cmd_mp3 = [
            ffmpeg_exe,
            "-y",
            "-i", str(output_wav_path),
            "-b:a", "192k",
            str(output_mp3_path),
        ]
        subprocess.run(cmd_mp3, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        duration = AudioConverter.get_audio_duration(output_wav_path)
        cond_prompt = (
            f"Google Gemini 3.8 Flash TTS ({gemini_voice}) | "
            f"Speaker: {speaker_id} | Speed: {speed}x | Pitch: {pitch.value} | Style: {style.value}"
        )
        return duration, 24000, cond_prompt

    finally:
        if temp_raw_wav.exists():
            try:
                temp_raw_wav.unlink()
            except Exception:
                pass


async def generate_gemini_speech(
    text: str,
    speaker_id: str,
    speed: float,
    pitch: PitchLevel,
    style: SpeakingStyle,
    output_mp3_path: Path,
    output_wav_path: Path,
) -> Tuple[float, int, str]:
    """Asynchronous wrapper around Gemini 3.8 Flash TTS generation."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        generate_gemini_tts_sync,
        text,
        speaker_id,
        speed,
        pitch,
        style,
        output_mp3_path,
        output_wav_path,
    )
