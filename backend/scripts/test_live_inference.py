import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.app.schemas.tts import (
    AudioFormat,
    PitchLevel,
    SpeakingStyle,
    TTSGenerateRequest,
)
from backend.app.services.tts_engine import tts_engine


async def main():
    print("=" * 60)
    print("TESTING HINDI + ENGLISH (HINGLISH) CODE-MIXED SPEECH")
    print("=" * 60)

    user_test_line = "नमस्ते! क्या आपने कभी सोचा है कि Programming में एक साथ कई सारी values कैसे store करते हैं?"
    print(f"\nTarget Text: {user_test_line}")

    # 1. Test Rohit (Male)
    print("\n--- Test 1: Synthesizing with Rohit (Male) ---")
    req_rohit = TTSGenerateRequest(
        text=user_test_line,
        speaker_id="rohit",
        speed=1.0,
        pitch=PitchLevel.MODERATE,
        style=SpeakingStyle.NATURAL,
        audio_format=AudioFormat.MP3,
    )
    t0 = time.time()
    res_rohit = await tts_engine.generate_speech(req_rohit)
    t1 = time.time()
    print(f"Generated Rohit audio in {t1 - t0:.2f}s!")
    print(f"Duration: {res_rohit.duration_seconds}s | MP3: {res_rohit.mp3_url}")

    # 2. Test Divya (Female)
    print("\n--- Test 2: Synthesizing with Divya (Female) ---")
    req_divya = TTSGenerateRequest(
        text=user_test_line,
        speaker_id="divya",
        speed=1.0,
        pitch=PitchLevel.MODERATE,
        style=SpeakingStyle.EXPRESSIVE,
        audio_format=AudioFormat.MP3,
    )
    t2 = time.time()
    res_divya = await tts_engine.generate_speech(req_divya)
    t3 = time.time()
    print(f"Generated Divya audio in {t3 - t2:.2f}s!")
    print(f"Duration: {res_divya.duration_seconds}s | MP3: {res_divya.mp3_url}")

    print("\n" + "=" * 60)
    print("SUCCESS: Code-mixed Hindi + English successfully synthesized!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
