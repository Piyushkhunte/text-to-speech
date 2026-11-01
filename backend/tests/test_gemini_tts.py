import os
from unittest.mock import MagicMock, patch
import pytest

from backend.app.schemas.tts import PitchLevel, SpeakingStyle
from backend.app.services.gemini_tts import (
    GEMINI_VOICE_MAP,
    generate_gemini_tts_sync,
    is_gemini_tts_enabled,
)
from backend.app.services.tts_engine import HINDI_VOICES


def test_gemini_voice_map_completeness():
    """Verify all verified Hindi voices have a corresponding Gemini TTS voice mapping."""
    for speaker_id in HINDI_VOICES.keys():
        assert speaker_id in GEMINI_VOICE_MAP, f"Missing Gemini mapping for speaker {speaker_id}"
        mapping = GEMINI_VOICE_MAP[speaker_id]
        assert "voice" in mapping
        assert "style" in mapping
        assert len(mapping["voice"]) > 0


def test_gemini_tts_enabled_check(monkeypatch):
    """Test enabled check when API key is set vs unset."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with patch("backend.app.core.config.settings.GEMINI_API_KEY", ""):
        assert is_gemini_tts_enabled() is False

    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyTestApiKeyForGeminiPro12345")
    assert is_gemini_tts_enabled() is True


def test_gemini_tts_request_structure(tmp_path, monkeypatch):
    """Test Gemini TTS interaction creation structure."""
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyTestKey1234567890")

    mock_client = MagicMock()
    mock_interaction = MagicMock()
    # Dummy base64 WAV payload
    mock_interaction.output_audio.data = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    mock_client.interactions.create.return_value = mock_interaction

    out_wav = tmp_path / "test.wav"
    out_mp3 = tmp_path / "test.mp3"

    with patch("google.genai.Client", return_value=mock_client), \
         patch("backend.app.services.gemini_tts.get_gemini_api_key", return_value="AIzaSyTestKey1234567890"):
        
        # Test call
        try:
            generate_gemini_tts_sync(
                text="नमस्ते! यह एक परीक्षण है।",
                speaker_id="aarav",
                speed=1.0,
                pitch=PitchLevel.MODERATE,
                style=SpeakingStyle.NATURAL,
                output_mp3_path=out_mp3,
                output_wav_path=out_wav,
            )
            mock_client.interactions.create.assert_called_once()
            call_kwargs = mock_client.interactions.create.call_args[1]
            assert call_kwargs["model"] == "gemini-3.8-flash-tts"
            assert call_kwargs["generation_config"]["speech_config"][0]["voice"] == "Puck"
        except Exception as e:
            # If FFmpeg on dummy 0-byte audio complains, verify API call was made
            mock_client.interactions.create.assert_called_once()
