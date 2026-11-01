import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "HindiVoice AI" in data["app"]


def test_health_endpoint():
    response = client.get("/api/tts/health")
    assert response.status_code == 200
    data = response.json()
    assert "device" in data
    assert "cpu_cores" in data
    assert "status" in data


def test_voices_endpoint():
    response = client.get("/api/tts/voices")
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert len(data["voices"]) >= 4
    ids = [v["id"] for v in data["voices"]]
    assert "rohit" in ids
    assert "divya" in ids
    assert "aman" in ids
    assert "rani" in ids


def test_history_endpoint():
    response = client.get("/api/tts/history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_generate_validation_empty():
    response = client.post("/api/tts/generate", json={"text": "", "speaker_id": "rohit"})
    assert response.status_code in [400, 422]


def test_generate_validation_symbols_only():
    response = client.post(
        "/api/tts/generate",
        json={"text": "!@#$%^&*()_+=", "speaker_id": "rohit"},
    )
    assert response.status_code == 422
    assert "मान्य हिंदी" in response.json()["detail"]



def test_generate_validation_unknown_speaker():
    response = client.post(
        "/api/tts/generate",
        json={"text": "नमस्ते", "speaker_id": "unknown_voice"},
    )
    assert response.status_code == 422
    assert "Unknown speaker" in response.json()["detail"]
