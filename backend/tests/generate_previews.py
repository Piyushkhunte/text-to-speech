import asyncio
import os
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.app.core.config import settings
from backend.app.schemas.tts import (
    AudioFormat,
    PitchLevel,
    SpeakingStyle,
    TTSGenerateRequest,
)
from backend.app.services.tts_engine import HINDI_VOICES, tts_engine


async def generate_previews():
    print("Pre-generating genuine audio previews for all 4 Hindi speakers...")

    for speaker_id, meta in HINDI_VOICES.items():
        preview_mp3 = settings.AUDIO_STORAGE_DIR / f"preview_{speaker_id}.mp3"
        preview_wav = settings.AUDIO_STORAGE_DIR / f"preview_{speaker_id}.wav"

        print(f"Generating preview for {meta.name} ({meta.gender})...")
        req = TTSGenerateRequest(
            text=meta.sample_text,
            speaker_id=speaker_id,
            speed=1.0,
            pitch=PitchLevel.LOW if speaker_id == "aman" else (PitchLevel.HIGH if speaker_id == "rani" else PitchLevel.MODERATE),
            style=SpeakingStyle.EXPRESSIVE if meta.gender == "female" else SpeakingStyle.NATURAL,
            audio_format=AudioFormat.MP3,
        )
        res = await tts_engine.generate_speech(req)

        gen_wav = settings.AUDIO_STORAGE_DIR / f"{res.audio_id}.wav"
        gen_mp3 = settings.AUDIO_STORAGE_DIR / f"{res.audio_id}.mp3"

        if gen_wav.exists():
            shutil.copyfile(gen_wav, preview_wav)
        if gen_mp3.exists():
            shutil.copyfile(gen_mp3, preview_mp3)

        print(f"-> Preview generated for {speaker_id}: {preview_mp3} ({preview_mp3.stat().st_size} bytes)")

    print("ALL 4 PREVIEWS SUCCESSFULLY GENERATED!")


if __name__ == "__main__":
    asyncio.run(generate_previews())
