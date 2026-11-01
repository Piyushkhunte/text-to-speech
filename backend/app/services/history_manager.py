import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.app.core.config import settings
from backend.app.db.crud_generations import (
    create_generation,
    delete_generation,
    get_generation,
    get_generations,
    update_generation,
)
from backend.app.db.database import init_db
from backend.app.schemas.tts import HistoryItem

logger = logging.getLogger(__name__)


class HistoryManager:
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or settings.AUDIO_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.storage_dir / "history.json"
        # Initialize SQLite database and run migration if needed
        try:
            init_db(self.history_file)
        except Exception as e:
            logger.error(f"Error initializing SQLite DB in HistoryManager: {e}")

    def add_item(self, item: HistoryItem) -> Dict:
        """Stores a generation record into SQLite."""
        data = item.model_dump()
        try:
            record = create_generation(data)
            return record
        except Exception as e:
            logger.error(f"Error creating generation in DB: {e}", exc_info=True)
            # Fallback to in-memory/JSON if needed
            return data

    def get_items(self) -> List[HistoryItem]:
        """Returns all history items ordered by most recent first."""
        items, _, _ = get_generations(limit=100, sort_by="created_at", sort_order="desc")
        return [HistoryItem(**i) for i in items]

    def query_items(
        self,
        search: Optional[str] = None,
        speaker_id: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[HistoryItem], int, int]:
        """Queries filtered history items. Returns (items, total_filtered, total_favorites)."""
        raw_items, total, fav_count = get_generations(
            search=search,
            speaker_id=speaker_id,
            is_favorite=is_favorite,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [HistoryItem(**i) for i in raw_items], total, fav_count

    def get_item(self, audio_id: str) -> Optional[HistoryItem]:
        """Gets a single history record by ID."""
        record = get_generation(audio_id)
        if not record:
            return None
        return HistoryItem(**record)

    def update_item(
        self,
        audio_id: str,
        title: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[HistoryItem]:
        """Updates metadata of a generation record."""
        record = update_generation(
            audio_id=audio_id,
            title=title,
            is_favorite=is_favorite,
            notes=notes,
            tags=tags,
        )
        if not record:
            return None
        return HistoryItem(**record)

    def delete_item(self, audio_id: str) -> bool:
        """Deletes item from SQLite DB and unlinks audio files from disk."""
        return delete_generation(audio_id)

    def cleanup_old_files(self, retention_hours: Optional[int] = None):
        """Removes expired non-favorite audio files and records older than threshold."""
        hours = retention_hours or settings.AUDIO_RETENTION_HOURS
        cutoff_seconds = time.time() - (hours * 3600)
        logger.info(f"Running history cleanup for files older than {hours} hours...")

        for file in self.storage_dir.glob("*.*"):
            if file.name.endswith(".json") or file.name.endswith(".db"):
                continue
            try:
                if file.stat().st_mtime < cutoff_seconds:
                    logger.info(f"Deleting expired audio file: {file.name}")
                    file.unlink()
            except Exception as e:
                logger.warning(f"Error removing expired file {file}: {e}")


history_manager = HistoryManager()
