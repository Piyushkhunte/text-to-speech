import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Optional

from ..core.config import settings

logger = logging.getLogger(__name__)

DB_DIR = Path(settings.AUDIO_STORAGE_DIR).parent / "data"
DB_FILE = DB_DIR / "hindivoice.db"


def get_db_path() -> Path:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return DB_FILE


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager providing thread-safe SQLite connection with row dictionary access."""
    path = get_db_path()
    conn = sqlite3.connect(str(path), check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(history_json_path: Optional[Path] = None):
    """Initializes tables and migrates existing JSON history if available."""
    get_db_path()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS generations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                speaker_id TEXT NOT NULL,
                speaker_name TEXT NOT NULL,
                speed REAL DEFAULT 1.0,
                pitch TEXT DEFAULT 'moderate',
                style TEXT DEFAULT 'natural',
                audio_format TEXT DEFAULT 'mp3',
                duration_seconds REAL NOT NULL,
                file_path_wav TEXT,
                file_path_mp3 TEXT,
                wav_url TEXT NOT NULL,
                mp3_url TEXT NOT NULL,
                is_favorite INTEGER DEFAULT 0,
                tags TEXT DEFAULT '[]',
                notes TEXT DEFAULT '',
                conditioning_prompt TEXT DEFAULT '',
                generation_time_ms REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generations_created ON generations(created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generations_favorite ON generations(is_favorite);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_generations_speaker ON generations(speaker_id);")

        # Migrate from history.json if DB table is currently empty
        cursor.execute("SELECT COUNT(*) as count FROM generations")
        row = cursor.fetchone()
        count = row["count"] if row else 0

        if count == 0:
            json_file = history_json_path or (settings.AUDIO_STORAGE_DIR / "history.json")
            if json_file.exists():
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        records = json.load(f)
                    migrated = 0
                    for r in records:
                        audio_id = r.get("id")
                        if not audio_id:
                            continue
                        text = r.get("text", "")
                        title = text[:40].replace("\n", " ").strip() + ("..." if len(text) > 40 else "")
                        created_at = r.get("created_at") or datetime.now(timezone.utc).isoformat()
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO generations (
                                id, title, text, speaker_id, speaker_name,
                                speed, pitch, style, audio_format, duration_seconds,
                                wav_url, mp3_url, is_favorite, tags, notes,
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                audio_id,
                                title or f"Reel ({r.get('speaker_name', 'Voice')})",
                                text,
                                r.get("speaker_id", "aarav"),
                                r.get("speaker_name", "Aarav"),
                                r.get("speed", 1.0),
                                r.get("pitch", "moderate"),
                                r.get("style", "natural"),
                                "mp3",
                                r.get("duration_seconds", 0.0),
                                r.get("wav_url", f"/api/tts/audio/{audio_id}?format=wav"),
                                r.get("mp3_url", f"/api/tts/audio/{audio_id}?format=mp3"),
                                0,
                                "[]",
                                "",
                                created_at,
                                created_at,
                            ),
                        )
                        migrated += 1
                    logger.info(f"Successfully migrated {migrated} records from history.json to SQLite database.")
                except Exception as e:
                    logger.warning(f"Could not migrate history.json: {e}")
