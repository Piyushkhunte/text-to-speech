import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..core.config import settings
from .database import get_db_connection

logger = logging.getLogger(__name__)


def create_generation(data: Dict) -> Dict:
    """Inserts a new generation record into SQLite."""
    now = datetime.now(timezone.utc).isoformat()
    text = data.get("text", "")
    default_title = text[:45].replace("\n", " ").strip() + ("..." if len(text) > 45 else "")
    title = data.get("title") or default_title or f"Reel ({data.get('speaker_name', 'Voice')})"

    tags_val = data.get("tags", [])
    if isinstance(tags_val, list):
        tags_str = json.dumps(tags_val)
    else:
        tags_str = str(tags_val)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO generations (
                id, title, text, speaker_id, speaker_name,
                speed, pitch, style, audio_format, duration_seconds,
                file_path_wav, file_path_mp3, wav_url, mp3_url,
                is_favorite, tags, notes, conditioning_prompt,
                generation_time_ms, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                title,
                text,
                data.get("speaker_id", "aarav"),
                data.get("speaker_name", "Aarav"),
                data.get("speed", 1.0),
                data.get("pitch", "moderate"),
                data.get("style", "natural"),
                data.get("audio_format", "mp3"),
                data.get("duration_seconds", 0.0),
                data.get("file_path_wav"),
                data.get("file_path_mp3"),
                data.get("wav_url", f"/api/tts/audio/{data['id']}?format=wav"),
                data.get("mp3_url", f"/api/tts/audio/{data['id']}?format=mp3"),
                1 if data.get("is_favorite") else 0,
                tags_str,
                data.get("notes", ""),
                data.get("conditioning_prompt", ""),
                data.get("generation_time_ms", 0.0),
                data.get("created_at") or now,
                now,
            ),
        )
    return get_generation(data["id"])  # type: ignore


def get_generation(audio_id: str) -> Optional[Dict]:
    """Retrieves a single generation record by its audio_id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM generations WHERE id = ?", (audio_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return _row_to_dict(row)


def get_generations(
    search: Optional[str] = None,
    speaker_id: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Tuple[List[Dict], int, int]:
    """
    Retrieves filtered generation records.
    Returns: (items, total_filtered_count, total_favorites_count)
    """
    conditions = []
    params = []

    if search and search.strip():
        term = f"%{search.strip()}%"
        conditions.append("(title LIKE ? OR text LIKE ? OR notes LIKE ?)")
        params.extend([term, term, term])

    if speaker_id and speaker_id != "all":
        conditions.append("speaker_id = ?")
        params.append(speaker_id)

    if is_favorite is not None:
        conditions.append("is_favorite = ?")
        params.append(1 if is_favorite else 0)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    allowed_sorts = {"created_at", "duration_seconds", "title", "speaker_name"}
    col = sort_by if sort_by in allowed_sorts else "created_at"
    direction = "ASC" if sort_order.lower() == "asc" else "DESC"

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Count total matching
        count_sql = f"SELECT COUNT(*) as cnt FROM generations{where_clause}"
        cursor.execute(count_sql, params)
        total_filtered = cursor.fetchone()["cnt"]

        # Count total favorites overall
        cursor.execute("SELECT COUNT(*) as fav_cnt FROM generations WHERE is_favorite = 1")
        total_favorites = cursor.fetchone()["fav_cnt"]

        # Query items
        query_sql = f"""
            SELECT * FROM generations
            {where_clause}
            ORDER BY {col} {direction}
            LIMIT ? OFFSET ?
        """
        cursor.execute(query_sql, params + [limit, offset])
        rows = cursor.fetchall()

        items = [_row_to_dict(r) for r in rows]
        return items, total_filtered, total_favorites


def update_generation(
    audio_id: str,
    title: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Optional[Dict]:
    """Updates mutable metadata of a generation record."""
    fields = []
    params = []
    now = datetime.now(timezone.utc).isoformat()

    if title is not None:
        fields.append("title = ?")
        params.append(title.strip())

    if is_favorite is not None:
        fields.append("is_favorite = ?")
        params.append(1 if is_favorite else 0)

    if notes is not None:
        fields.append("notes = ?")
        params.append(notes)

    if tags is not None:
        fields.append("tags = ?")
        params.append(json.dumps(tags))

    if not fields:
        return get_generation(audio_id)

    fields.append("updated_at = ?")
    params.append(now)
    params.append(audio_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        sql = f"UPDATE generations SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(sql, params)
        if cursor.rowcount == 0:
            return None

    return get_generation(audio_id)


def delete_generation(audio_id: str) -> bool:
    """Deletes generation record from SQLite and unlinks physical audio files."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path_wav, file_path_mp3 FROM generations WHERE id = ?", (audio_id,))
        row = cursor.fetchone()
        if not row:
            return False

        # Remove audio files from disk if stored
        storage_dir = settings.AUDIO_STORAGE_DIR
        wav_file = Path(row["file_path_wav"]) if row["file_path_wav"] else (storage_dir / f"{audio_id}.wav")
        mp3_file = Path(row["file_path_mp3"]) if row["file_path_mp3"] else (storage_dir / f"{audio_id}.mp3")

        for f in (wav_file, mp3_file):
            try:
                if f.exists():
                    f.unlink()
            except Exception as e:
                logger.warning(f"Error removing file {f}: {e}")

        cursor.execute("DELETE FROM generations WHERE id = ?", (audio_id,))
        return cursor.rowcount > 0


def _row_to_dict(row) -> Dict:
    d = dict(row)
    # Parse tags JSON string back to list
    if "tags" in d and isinstance(d["tags"], str):
        try:
            d["tags"] = json.loads(d["tags"])
        except Exception:
            d["tags"] = []
    d["is_favorite"] = bool(d.get("is_favorite", 0))
    return d
