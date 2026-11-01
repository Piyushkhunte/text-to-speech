import asyncio
import logging
import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import edge_tts
from backend.app.core.config import settings
from backend.app.schemas.tts import PitchLevel, SpeakingStyle
from backend.app.services.audio_converter import AudioConverter
from backend.app.utils.hindi_validator import contains_devanagari

logger = logging.getLogger(__name__)

# Pronunciation safeguards for common Hinglish words to avoid English G2P phonetic traps (e.g. 'par' -> 'paar', 'bhejo' -> 'bhenjo')
PRONUNCIATION_SAFEGUARDS = {
    # 1. Critical Words Specifically Reported
    r"\bpar\b": "पर",
    r"\bpe\b": "पे",
    r"\btemporarily\b": "टेम्परेरली",
    r"\btemporary\b": "टेम्परेरी",
    r"\bbhejo\b": "भेजो",
    r"\bbheja\b": "भेजा",
    r"\bbhej\b": "भेज",
    r"\bbhejte\b": "भेजते",
    r"\bbhejna\b": "भेजना",
    r"\bsocho\b": "सोचो",
    r"\bsocha\b": "सोचा",
    r"\bpahunchta\b": "पहुंचता",
    r"\bpahunchti\b": "पहुंचती",
    r"\bpahunchte\b": "पहुंचते",
    r"\bpahunchane\b": "पहुंचाने",
    r"\bmilte\b": "मिलते",
    r"\bmilta\b": "मिलता",
    r"\bmilti\b": "मिलती",
    r"\bjaata\b": "जाता",
    r"\bjaati\b": "जाती",
    r"\bjaate\b": "जाते",
    r"\bhota\b": "होता",
    r"\bhoti\b": "होती",
    r"\bhote\b": "होते",
    r"\bkarte\b": "करते",
    r"\bkarti\b": "करती",
    r"\bkarta\b": "करता",
    r"\bsamajh\b": "समझ",
    r"\bsamajhte\b": "समझते",
    r"\bsamajhne\b": "समझने",
    r"\bsamajh aata\b": "समझ आता",
    r"\bdekhkar\b": "देखकर",
    r"\byaad rakhna\b": "याद रखना",
    r"\bkaam kar raha\b": "काम कर रहा",
    r"\bfollow karo\b": "फॉलो करो",

    # 2. Hinglish Postpositions & Pronouns that English G2P mispronounces
    r"\bse\b": "से",
    r"\bko\b": "को",
    r"\bka\b": "का",
    r"\bki\b": "की",
    r"\bke\b": "के",
    r"\bmein\b": "में",
    r"\bme\b": "में",
    r"\bhai\b": "है",
    r"\bhain\b": "हैं",
    r"\bbhi\b": "भी",
    r"\baur\b": "और",
    r"\bkya\b": "क्या",
    r"\bkyun\b": "क्यों",
    r"\bkaise\b": "कैसे",
    r"\btak\b": "तक",
    r"\bjab\b": "जब",
    r"\btab\b": "तब",
    r"\bab\b": "अब",
    r"\btoh\b": "तो",
    r"\bto\b": "तो",
    r"\bsirf\b": "सिर्फ",
    r"\bdost\b": "दोस्त",
    r"\buske\b": "उसके",
    r"\buska\b": "उसका",
    r"\buski\b": "उसकी",
    r"\bapne\b": "अपने",
    r"\bapna\b": "अपना",
    r"\bapni\b": "अपनी",
    r"\btumne\b": "तुमने",
    r"\btumhara\b": "तुम्हारा",
    r"\btumhare\b": "तुम्हारे",
    r"\btumhari\b": "तुम्हारी",
    r"\bhumne\b": "हमने",
    r"\bjaise\b": "जैसे",
    r"\bwaise\b": "वैसे",
    r"\baisa\b": "ऐसा",
    r"\baise\b": "ऐसे",
    r"\baisi\b": "ऐसी",
    r"\blekin\b": "लेकिन",
    r"\bagar\b": "अगर",
    r"\bmagar\b": "मगर",
    r"\bmatlab\b": "मतलब",
    r"\bpoora\b": "पूरा",
    r"\bpoori\b": "पूरी",
    r"\bpoore\b": "पूरे",
    r"\bpeeche\b": "पीछे",
    r"\baage\b": "आगे",
    r"\bpehle\b": "पहले",
    r"\bbaad\b": "बाद",
    r"\bbaat\b": "बात",
    r"\bsabse\b": "सबसे",
    r"\bsahi\b": "सही",
    r"\bbas\b": "बस",
    r"\bisi\b": "इसी",
    r"\bagli\b": "अगली",
    r"\bbaar\b": "बार",
}


def normalize_hinglish_pronunciation(text: str) -> str:
    """Safeguards common Roman Hinglish words with exact phonetic Devanagari substitutions."""
    for pattern, replacement in PRONUNCIATION_SAFEGUARDS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def clean_markdown_and_punctuation(text: str) -> str:
    """Cleans bold, italics, and formats pauses for smooth TTS articulation."""
    if not text:
        return ""
    # Strip markdown bold & italics
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    # Replace unicode ellipsis with pause-friendly punctuation
    text = text.replace("…", "... ")
    # Clean redundant whitespace
    text = re.sub(r"[ \t]+", " ", text).strip()
    # Normalize tricky Hinglish words
    return normalize_hinglish_pronunciation(text)


def has_scene_tags(text: str) -> bool:
    """Checks whether text contains narrative acting tags like [Hook], [Story], [Reveal], [Ending]."""
    tag_pattern = re.compile(
        r"(?:\*\*|\#\#)?\[\s*(?:hook|story|reveal|ending|intro|outro|curious|dramatic|twist|climax|body|explanation|cta|action)\b[^\]]*\](?:\*\*|\#\#)?",
        re.IGNORECASE,
    )
    return bool(tag_pattern.search(text))


def parse_script_into_scenes(script: str) -> List[Dict]:
    """
    Parses a reel script with narrative bracket tags into structured acting scenes.
    Supported tags:
    - [Hook — curious, energetic]
    - [Story begins] / [Explanation]
    - [Reveal — slightly dramatic] / [Twist]
    - [Ending] / [Call to action]
    """
    tag_regex = re.compile(r"(?:\*\*|\#\#)?\[([^\]]+)\](?:\*\*|\#\#)?")
    parts = tag_regex.split(script)

    if len(parts) == 1:
        return [
            {
                "tone": "story",
                "tag_name": "Standard Story",
                "text": clean_markdown_and_punctuation(script),
            }
        ]

    scenes: List[Dict] = []
    i = 0
    current_tone = "story"
    current_label = "Story"

    while i < len(parts):
        chunk = parts[i].strip()
        if not chunk:
            i += 1
            continue

        tag_lower = chunk.lower()
        if any(k in tag_lower for k in ["hook", "curious", "energetic", "intro"]):
            current_tone = "hook"
            current_label = chunk
            i += 1
            if i < len(parts):
                content = clean_markdown_and_punctuation(parts[i])
                if content:
                    scenes.append(
                        {
                            "tone": current_tone,
                            "tag_name": current_label,
                            "text": content,
                        }
                    )
            i += 1
        elif any(k in tag_lower for k in ["story", "explainer", "explanation", "body", "begins"]):
            current_tone = "story"
            current_label = chunk
            i += 1
            if i < len(parts):
                content = clean_markdown_and_punctuation(parts[i])
                if content:
                    scenes.append(
                        {
                            "tone": current_tone,
                            "tag_name": current_label,
                            "text": content,
                        }
                    )
            i += 1
        elif any(k in tag_lower for k in ["reveal", "dramatic", "twist", "surprise", "secret", "climax"]):
            current_tone = "reveal"
            current_label = chunk
            i += 1
            if i < len(parts):
                content = clean_markdown_and_punctuation(parts[i])
                if content:
                    scenes.append(
                        {
                            "tone": current_tone,
                            "tag_name": current_label,
                            "text": content,
                        }
                    )
            i += 1
        elif any(k in tag_lower for k in ["ending", "outro", "conclusion", "call to action", "cta"]):
            current_tone = "ending"
            current_label = chunk
            i += 1
            if i < len(parts):
                content = clean_markdown_and_punctuation(parts[i])
                if content:
                    scenes.append(
                        {
                            "tone": current_tone,
                            "tag_name": current_label,
                            "text": content,
                        }
                    )
            i += 1
        else:
            # Regular text without a tag
            content = clean_markdown_and_punctuation(chunk)
            if content:
                scenes.append(
                    {
                        "tone": current_tone,
                        "tag_name": current_label,
                        "text": content,
                    }
                )
            i += 1

    return scenes


class StoryDirector:
    """Directs multi-scene narrative voice acting with smooth transitions and broadcast mastering."""

    @staticmethod
    async def synthesize_directed_story(
        text: str,
        speaker_id: str,
        base_speed: float,
        base_pitch: PitchLevel,
        voice_neural_map: Dict,
        output_mp3_path: Path,
        output_wav_path: Path,
    ) -> Tuple[float, int, str]:
        scenes = parse_script_into_scenes(text)
        if not scenes:
            raise ValueError("No script content found to synthesize.")

        voice_info = voice_neural_map.get(speaker_id.lower(), voice_neural_map.get("aarav", {}))
        ffmpeg_exe = AudioConverter.get_ffmpeg_executable()

        temp_dir = settings.AUDIO_STORAGE_DIR / f"temp_story_{uuid.uuid4().hex[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        scene_wav_files: List[Path] = []

        try:
            for idx, scene in enumerate(scenes):
                tone = scene["tone"]
                scene_text = scene["text"]

                # Smart voice routing
                is_pure_latin = not contains_devanagari(scene_text)
                if is_pure_latin and "hinglish_voice" in voice_info:
                    voice_name = voice_info["hinglish_voice"]
                else:
                    voice_name = voice_info["voice"]

                # Natural, organic prosody modulation (subtle ±2Hz range, no jarring cliffs)
                rate_offset = voice_info.get("rate_offset", 0)
                pitch_offset = voice_info.get("pitch_offset", 0)

                if tone == "hook":
                    # Curious, energetic, engaging (+5% rate, +3Hz pitch)
                    rate_val = int((base_speed - 1.0) * 100) + rate_offset + 5
                    pitch_val = pitch_offset + 3
                elif tone == "story":
                    # Clear, natural explanatory flow (+3% rate, +1Hz pitch)
                    rate_val = int((base_speed - 1.0) * 100) + rate_offset + 3
                    pitch_val = pitch_offset + 1
                elif tone == "reveal":
                    # Deliberate, grounded revelation (+1% rate, +0Hz pitch)
                    rate_val = int((base_speed - 1.0) * 100) + rate_offset + 1
                    pitch_val = pitch_offset + 0
                elif tone == "ending":
                    # Upbeat, confident call-to-action (+5% rate, +3Hz pitch)
                    rate_val = int((base_speed - 1.0) * 100) + rate_offset + 5
                    pitch_val = pitch_offset + 3
                else:
                    rate_val = int((base_speed - 1.0) * 100) + rate_offset + 3
                    pitch_val = pitch_offset + 1

                rate_str = f"{rate_val:+d}%"
                pitch_str = f"{pitch_val:+d}Hz"

                scene_mp3 = temp_dir / f"scene_{idx}.mp3"
                scene_wav = temp_dir / f"scene_{idx}.wav"

                # Synthesize scene
                comm = edge_tts.Communicate(scene_text, voice_name, rate=rate_str, pitch=pitch_str)
                await comm.save(str(scene_mp3))

                # Convert to standard 24kHz mono WAV
                cmd_conv = [
                    ffmpeg_exe,
                    "-y",
                    "-i",
                    str(scene_mp3),
                    "-ar",
                    "24000",
                    "-ac",
                    "1",
                    str(scene_wav),
                ]
                proc = await asyncio.create_subprocess_exec(
                    *cmd_conv,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
                scene_wav_files.append(scene_wav)

            raw_joined_wav = temp_dir / "raw_joined.wav"

            if len(scene_wav_files) == 1:
                # Only 1 scene, copy directly
                import shutil
                shutil.copyfile(scene_wav_files[0], raw_joined_wav)
            else:
                # Multiple scenes: apply smooth audio crossfade (acrossfade) between each scene
                # This eliminates abrupt splicing or hard silence cuts!
                inputs = []
                filter_parts = []
                for idx, w in enumerate(scene_wav_files):
                    inputs.extend(["-i", str(w)])

                last_label = "[0]"
                for idx in range(1, len(scene_wav_files)):
                    next_input = f"[{idx}]"
                    out_label = f"[a{idx}]" if idx < len(scene_wav_files) - 1 else "[out_audio]"
                    filter_parts.append(f"{last_label}{next_input}acrossfade=d=0.20:c1=tri:c2=tri{out_label}")
                    last_label = out_label

                filter_complex = "; ".join(filter_parts)
                cmd_fade = [ffmpeg_exe, "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[out_audio]", str(raw_joined_wav)]
                proc_fade = await asyncio.create_subprocess_exec(
                    *cmd_fade,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc_fade.communicate()

            # Master joined audio with broadcast compressor & presence EQ
            filter_chain = "acompressor=threshold=-14dB:ratio=3.5:attack=10:release=80,equalizer=f=3200:t=q:w=1.2:g=3.0"
            cmd_master_wav = [
                ffmpeg_exe,
                "-y",
                "-i",
                str(raw_joined_wav),
                "-af",
                filter_chain,
                "-ar",
                "24000",
                "-ac",
                "1",
                str(output_wav_path),
            ]
            proc_master = await asyncio.create_subprocess_exec(
                *cmd_master_wav,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc_master.communicate()

            # Encode high-bitrate MP3
            cmd_master_mp3 = [
                ffmpeg_exe,
                "-y",
                "-i",
                str(output_wav_path),
                "-b:a",
                "192k",
                str(output_mp3_path),
            ]
            proc_mp3 = await asyncio.create_subprocess_exec(
                *cmd_master_mp3,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc_mp3.communicate()

            duration = AudioConverter.get_audio_duration(output_wav_path)
            prompt_summary = f"Smooth Directed Reel ({len(scenes)} Scenes: Hook → Story → Reveal → Ending) | Organic Crossfaded Audio"
            return duration, 24000, prompt_summary

        finally:
            try:
                for file_path in temp_dir.glob("*"):
                    file_path.unlink(missing_ok=True)
                temp_dir.rmdir()
            except Exception as e:
                logger.warning(f"Error cleaning story director temp dir: {e}")
