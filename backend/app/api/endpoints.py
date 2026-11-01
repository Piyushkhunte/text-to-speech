import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response, status
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.schemas.tts import (
    GenerationUpdateRequest,
    HealthResponse,
    HistoryItem,
    HistoryResponse,
    TTSGenerateRequest,
    TTSGenerateResponse,
    VoiceMetadata,
    VoicesListResponse,
)
from backend.app.services.history_manager import history_manager
from backend.app.services.tts_engine import HINDI_VOICES, tts_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["Text to Speech"])


@router.post(
    "/generate",
    response_model=TTSGenerateResponse,
    summary="Generate Hindi Speech",
    description="Synthesize natural Hindi speech from Devanagari text using Indic Parler-TTS.",
)
async def generate_speech(request: TTSGenerateRequest):
    try:
        response = await tts_engine.generate_speech(request)
        return response
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis error: {str(e)}",
        )


@router.get(
    "/voices",
    response_model=VoicesListResponse,
    summary="Get Supported Hindi Voices",
    description="Retrieve all verified Hindi voices and metadata supported by the model.",
)
async def get_voices():
    voices = tts_engine.get_voices()
    return VoicesListResponse(voices=voices, default_voice="aarav")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Hardware Telemetry",
    description="Check backend server health, model readiness, device (CPU/GPU) info, and uptime.",
)
async def health_check():
    info = tts_engine.get_health_status()
    return HealthResponse(**info)


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Get Generation History (Searchable & Filterable)",
    description="List previously synthesized Hindi speech records with optional search, speaker, and favorite filters.",
)
async def get_history(
    search: Optional[str] = Query(None, description="Search keyword in title, text, or notes"),
    speaker: Optional[str] = Query(None, description="Filter by speaker_id"),
    favorite: Optional[bool] = Query(None, description="Filter by favorite/starred status"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Offset pagination"),
    sort_by: str = Query("created_at", pattern="^(created_at|duration_seconds|title|speaker_name)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    items, total, fav_count = history_manager.query_items(
        search=search,
        speaker_id=speaker,
        is_favorite=favorite,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return HistoryResponse(items=items, total=total, favorites_count=fav_count)


@router.get(
    "/history/{audio_id}",
    response_model=HistoryItem,
    summary="Get Single History Record",
    description="Retrieve full metadata of a specific speech generation record.",
)
async def get_single_history(audio_id: str):
    item = history_manager.get_item(audio_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation record not found",
        )
    return item


@router.patch(
    "/history/{audio_id}",
    response_model=HistoryItem,
    summary="Update History Record (Title, Favorite, Notes, Tags)",
    description="Update mutable attributes of a generated speech project.",
)
async def update_history_item(audio_id: str, updates: GenerationUpdateRequest):
    updated = history_manager.update_item(
        audio_id=audio_id,
        title=updates.title,
        is_favorite=updates.is_favorite,
        notes=updates.notes,
        tags=updates.tags,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation record not found",
        )
    return updated


@router.delete(
    "/history/{audio_id}",
    summary="Delete History Item",
    description="Delete a generated audio record and its associated audio files.",
)
async def delete_history_item(audio_id: str):
    success = history_manager.delete_item(audio_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio record not found",
        )
    return {"success": True, "message": "History item deleted successfully"}


@router.get(
    "/audio/{audio_id}",
    summary="Retrieve Generated Audio File",
    description="Stream or download the generated audio file in WAV or MP3 format.",
)
async def get_audio(
    audio_id: str,
    format: str = Query("mp3", pattern="^(mp3|wav)$"),
    download: bool = Query(False),
):
    extension = format.lower()
    file_path = settings.AUDIO_STORAGE_DIR / f"{audio_id}.{extension}"

    if not file_path.exists():
        # Fallback to wav if mp3 not found
        if extension == "mp3":
            wav_path = settings.AUDIO_STORAGE_DIR / f"{audio_id}.wav"
            if wav_path.exists():
                file_path = wav_path
                extension = "wav"
            else:
                raise HTTPException(status_code=404, detail="Audio file not found")
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")

    media_type = "audio/mpeg" if extension == "mp3" else "audio/wav"
    filename = f"hindivoice_{audio_id[:8]}.{extension}"

    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    else:
        headers["Content-Disposition"] = f'inline; filename="{filename}"'

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers=headers,
    )


@router.get(
    "/preview/{speaker_id}",
    summary="Get Speaker Sample Audio Preview",
    description="Returns pre-generated sample audio preview for the selected speaker identity.",
)
async def get_speaker_preview(speaker_id: str):
    speaker = speaker_id.lower()
    if speaker not in HINDI_VOICES:
        raise HTTPException(status_code=404, detail="Speaker identity not found")

    # Check if cached preview audio exists
    preview_path = settings.AUDIO_STORAGE_DIR / f"preview_{speaker}.mp3"
    preview_wav = settings.AUDIO_STORAGE_DIR / f"preview_{speaker}.wav"

    if preview_path.exists():
        return FileResponse(path=str(preview_path), media_type="audio/mpeg")
    elif preview_wav.exists():
        return FileResponse(path=str(preview_wav), media_type="audio/wav")

    # If preview hasn't been generated yet, dynamically generate it using sample_text
    meta = HINDI_VOICES[speaker]
    req = TTSGenerateRequest(
        text=meta.sample_text,
        speaker_id=speaker,
        speed=1.0,
    )
    res = await tts_engine.generate_speech(req)
    gen_file = settings.AUDIO_STORAGE_DIR / f"{res.audio_id}.mp3"
    if gen_file.exists():
        # Cache as preview file
        import shutil
        shutil.copyfile(gen_file, preview_path)
        return FileResponse(path=str(preview_path), media_type="audio/mpeg")

    raise HTTPException(status_code=500, detail="Could not generate speaker preview")
