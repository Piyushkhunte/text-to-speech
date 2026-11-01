import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.db.crud_generations import (
    create_generation,
    delete_generation,
    get_generation,
    get_generations,
    update_generation,
)
from backend.app.main import app

client = TestClient(app)


def test_crud_generations_lifecycle():
    test_id = f"test-{uuid.uuid4().hex[:8]}"

    # 1. Create
    data = {
        "id": test_id,
        "title": "WhatsApp Reel Hook Demo",
        "text": "Socho, tumne WhatsApp par apne dost ko message bheja...",
        "speaker_id": "aarav",
        "speaker_name": "Aarav (आरव)",
        "speed": 1.0,
        "pitch": "moderate",
        "style": "natural",
        "audio_format": "mp3",
        "duration_seconds": 12.5,
        "is_favorite": False,
        "notes": "Testing initial creation",
    }
    created = create_generation(data)
    assert created["id"] == test_id
    assert created["title"] == "WhatsApp Reel Hook Demo"
    assert created["is_favorite"] is False

    # 2. Read Single
    item = get_generation(test_id)
    assert item is not None
    assert item["speaker_id"] == "aarav"
    assert "WhatsApp" in item["text"]

    # 3. Read Query / Filter
    items, total, fav_count = get_generations(search="WhatsApp")
    assert any(i["id"] == test_id for i in items)

    # 4. Update (Title, Favorite, Notes)
    updated = update_generation(
        audio_id=test_id,
        title="WhatsApp Reel Hook Demo (Renamed)",
        is_favorite=True,
        notes="Starred as favorite for Instagram reel",
    )
    assert updated is not None
    assert updated["title"] == "WhatsApp Reel Hook Demo (Renamed)"
    assert updated["is_favorite"] is True
    assert "Starred" in updated["notes"]

    # Filter by favorite
    fav_items, _, new_fav_count = get_generations(is_favorite=True)
    assert any(i["id"] == test_id for i in fav_items)
    assert new_fav_count >= 1

    # 5. Delete
    deleted = delete_generation(test_id)
    assert deleted is True
    assert get_generation(test_id) is None


def test_api_crud_endpoints():
    test_id = f"api-test-{uuid.uuid4().hex[:8]}"

    # Insert a test record directly first
    create_generation({
        "id": test_id,
        "title": "System Design Search Autocomplete",
        "text": "Google jaisa search engine kaise design karte hain?",
        "speaker_id": "aarav",
        "speaker_name": "Aarav",
        "speed": 1.0,
        "pitch": "moderate",
        "style": "natural",
        "audio_format": "mp3",
        "duration_seconds": 15.0,
        "is_favorite": False,
    })

    # Test GET /api/tts/history
    res = client.get("/api/tts/history?search=Autocomplete")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert any(i["id"] == test_id for i in data["items"])

    # Test GET /api/tts/history/{id}
    res_single = client.get(f"/api/tts/history/{test_id}")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == test_id

    # Test PATCH /api/tts/history/{id}
    patch_payload = {
        "title": "System Design Autocomplete - Final Cut",
        "is_favorite": True,
        "notes": "Ready for export to premiere pro",
    }
    res_patch = client.patch(f"/api/tts/history/{test_id}", json=patch_payload)
    assert res_patch.status_code == 200
    patched_data = res_patch.json()
    assert patched_data["title"] == "System Design Autocomplete - Final Cut"
    assert patched_data["is_favorite"] is True

    # Test DELETE /api/tts/history/{id}
    res_del = client.delete(f"/api/tts/history/{test_id}")
    assert res_del.status_code == 200
    assert res_del.json()["success"] is True

    # Confirm 404 after deletion
    res_404 = client.get(f"/api/tts/history/{test_id}")
    assert res_404.status_code == 404
