import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.endpoints import router as tts_router
from .core.config import settings
from .services.history_manager import history_manager
from .services.tts_engine import tts_engine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("HindiVoiceAI")


async def periodic_cleanup_task():
    """Background task that runs periodic cleanup of expired generated audio files."""
    while True:
        try:
            await asyncio.sleep(settings.CLEANUP_INTERVAL_MINUTES * 60)
            logger.info("Executing periodic audio file cleanup...")
            history_manager.cleanup_old_files()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in background cleanup task: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    logger.info(f"Model: {settings.MODEL_NAME} | Device: {settings.DEVICE}")

    # Launch periodic cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup_task())

    # Pre-warm model in background thread so server starts accepting requests immediately
    asyncio.create_task(asyncio.to_thread(tts_engine.load_model))

    yield

    # Shutdown actions
    logger.info(f"Shutting down {settings.APP_NAME}...")
    cleanup_task.cancel()


app = FastAPI(
    title="HindiVoice AI - Indic Text-to-Speech API",
    description=(
        "Production-grade REST API for natural Hindi speech synthesis powered by "
        "AI4Bharat Indic Parler-TTS."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local Next.js dev server & external frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include TTS router
app.include_router(tts_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again."},
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/tts/health",
        "voices": "/api/tts/voices",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
