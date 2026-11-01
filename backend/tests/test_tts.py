import pytest
from backend.app.core.config import settings
from backend.app.schemas.tts import PitchLevel, SpeakingStyle
from backend.app.services.audio_converter import AudioConverter
from backend.app.services.history_manager import HistoryManager
from backend.app.services.tts_engine import HINDI_VOICES, TTSEngine
from backend.app.utils.hindi_validator import (
    contains_devanagari,
    normalize_hindi_text,
    validate_hindi_input,
)


def test_hindi_validator_valid():
    text = "नमस्ते, यह एक परीक्षण वाक्य है।"
    is_valid, norm, err = validate_hindi_input(text, max_chars=3000)
    assert is_valid is True
    assert "नमस्ते" in norm
    assert err == ""


def test_hindi_validator_hinglish():
    text = "Namaste dosto, kya aapne kabhi socha hai ki programming me values kaise store karte hain?"
    is_valid, norm, err = validate_hindi_input(text, max_chars=3000)
    assert is_valid is True
    assert "Namaste" in norm
    assert err == ""


def test_hindi_validator_mixed_tech():
    text = "आजकल कंप्यूटर और AI तकनीक का उपयोग बढ़ रहा है।"
    is_valid, norm, err = validate_hindi_input(text, max_chars=3000)
    assert is_valid is True
    assert "AI" in norm
    assert err == ""


def test_hindi_validator_empty():
    is_valid, _, err = validate_hindi_input("", max_chars=3000)
    assert is_valid is False
    assert "खाली" in err


def test_hindi_validator_symbols_only():
    is_valid, _, err = validate_hindi_input("!@#$%^&*()_+=-{}[]", max_chars=3000)
    assert is_valid is False
    assert "मान्य हिंदी" in err


def test_hindi_validator_exceeds_max():
    long_text = "नमस्ते " * 600
    is_valid, _, err = validate_hindi_input(long_text, max_chars=100)
    assert is_valid is False
    assert "अधिक लंबा" in err


def test_verified_speakers_present():
    expected_speakers = {"aarav", "kabir", "ananya", "rohit", "divya", "aman", "rani"}
    assert expected_speakers.issubset(set(HINDI_VOICES.keys()))

    # Check Kabir & Ananya
    kabir = HINDI_VOICES["kabir"]
    assert kabir.gender == "male"
    assert kabir.recommended is True

    ananya = HINDI_VOICES["ananya"]
    assert ananya.gender == "female"
    assert ananya.recommended is True

    # Check Rohit & Divya
    assert HINDI_VOICES["rohit"].gender == "male"
    assert HINDI_VOICES["divya"].gender == "female"


def test_conditioning_prompt_builder():
    engine = TTSEngine.get_instance()
    prompt = engine.build_conditioning_prompt(
        speaker_id="rohit",
        speed=1.0,
        pitch=PitchLevel.MODERATE,
        style=SpeakingStyle.NATURAL,
    )
    assert "Rohit" in prompt
    assert "Speed" in prompt

    prompt_divya = engine.build_conditioning_prompt(
        speaker_id="divya",
        speed=1.3,
        pitch=PitchLevel.HIGH,
        style=SpeakingStyle.EXPRESSIVE,
    )
    assert "Divya" in prompt_divya
    assert "high" in prompt_divya


def test_history_manager(tmp_path):
    mgr = HistoryManager(storage_dir=tmp_path)
    from backend.app.schemas.tts import HistoryItem
    from datetime import datetime, timezone

    item = HistoryItem(
        id="test-audio-1",
        speaker_id="rohit",
        speaker_name="Rohit",
        text="परीक्षण टेक्स्ट",
        duration_seconds=2.5,
        wav_url="/api/tts/audio/test-audio-1?format=wav",
        mp3_url="/api/tts/audio/test-audio-1?format=mp3",
        created_at=datetime.now(timezone.utc),
        speed=1.0,
        pitch="moderate",
        style="natural",
    )
    mgr.add_item(item)
    items = mgr.get_items()
    assert any(i.id == "test-audio-1" for i in items)

    # Delete
    deleted = mgr.delete_item("test-audio-1")
    assert deleted is True
    assert not any(i.id == "test-audio-1" for i in mgr.get_items())


def test_pronunciation_safeguards():
    from backend.app.services.story_director import normalize_hinglish_pronunciation

    # Test "par" -> "पर" (avoiding "paar") and "bhejo" -> "भेजो" (avoiding "bhenjo")
    text = "Agli baar WhatsApp par message bhejo, toh yaad rakhna"
    normalized = normalize_hinglish_pronunciation(text)
    assert "भेजो" in normalized
    assert "याद रखना" in normalized
    assert "पर" in normalized

    # Test "socha" and "pahunchta"
    text2 = "Lekin kya tumne kabhi socha hai, ye message uske phone tak pahunchta kaise hai?"
    normalized2 = normalize_hinglish_pronunciation(text2)
    assert "सोचा" in normalized2
    assert "पहुंचता" in normalized2

    # Test "temporarily" -> "टेम्परेरली"
    text3 = "Toh encrypted message temporarily server par wait kar sakta hai"
    normalized3 = normalize_hinglish_pronunciation(text3)
    assert "टेम्परेरली" in normalized3
    assert "पर" in normalized3


def test_scene_tag_parsing():
    from backend.app.services.story_director import has_scene_tags, parse_script_into_scenes

    script = """**[Hook — curious, energetic]**
Socho, tumne WhatsApp par message bheja...

**[Story begins]**
Sabse pehle message server tak jaata hai.

**[Reveal — slightly dramatic]**
Aur bas, yahi encryption ka role hai.

**[Ending]**
Follow karo Code Ki Class!"""

    assert has_scene_tags(script) is True
    scenes = parse_script_into_scenes(script)
    assert len(scenes) == 4
    assert scenes[0]["tone"] == "hook"
    assert scenes[1]["tone"] == "story"
    assert scenes[2]["tone"] == "reveal"
    assert scenes[3]["tone"] == "ending"
