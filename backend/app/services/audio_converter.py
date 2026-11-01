import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import soundfile as sf

logger = logging.getLogger(__name__)


class AudioConverter:
    _ffmpeg_path: Optional[str] = None

    @classmethod
    def get_ffmpeg_executable(cls) -> str:
        """
        Locates FFmpeg executable dynamically.
        Checks:
        1. imageio_ffmpeg bundled binary
        2. System PATH (where ffmpeg)
        """
        if cls._ffmpeg_path and os.path.exists(cls._ffmpeg_path):
            return cls._ffmpeg_path

        # Check imageio_ffmpeg first
        try:
            import imageio_ffmpeg
            exe = imageio_ffmpeg.get_ffmpeg_exe()
            if exe and os.path.exists(exe):
                cls._ffmpeg_path = exe
                logger.info(f"Using FFmpeg from imageio_ffmpeg: {exe}")
                return exe
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Could not load imageio_ffmpeg: {e}")

        # Check system PATH
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            cls._ffmpeg_path = system_ffmpeg
            logger.info(f"Using system FFmpeg: {system_ffmpeg}")
            return system_ffmpeg

        raise RuntimeError(
            "FFmpeg executable not found. Please ensure imageio-ffmpeg is installed "
            "or FFmpeg is added to your system PATH."
        )

    @classmethod
    def wav_to_mp3(cls, wav_path: Path, mp3_path: Path, bitrate: str = "192k") -> bool:
        """
        Converts a WAV file to high quality MP3 using FFmpeg.
        """
        try:
            ffmpeg_exe = cls.get_ffmpeg_executable()
            cmd = [
                ffmpeg_exe,
                "-y",  # Overwrite output
                "-i", str(wav_path),
                "-codec:a", "libmp3lame",
                "-b:a", bitrate,
                "-ar", "24000",
                str(mp3_path),
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=30,
            )
            return mp3_path.exists() and mp3_path.stat().st_size > 0
        except Exception as e:
            logger.error(f"Failed to convert WAV to MP3: {e}")
            raise RuntimeError(f"Audio conversion error: {e}")

    @staticmethod
    def get_audio_duration(file_path: Path) -> float:
        """Reads audio duration in seconds using soundfile."""
        try:
            with sf.SoundFile(str(file_path)) as f:
                return float(len(f)) / float(f.samplerate)
        except Exception as e:
            logger.warning(f"Could not calculate audio duration: {e}")
            return 0.0
