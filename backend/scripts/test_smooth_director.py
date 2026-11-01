import asyncio
import re
from pathlib import Path
import edge_tts
import imageio_ffmpeg
import subprocess
import soundfile as sf

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

USER_SCRIPT = """**[Hook — curious, energetic]**

Socho, tumne WhatsApp par apne dost ko message bheja…  
"Kal milte hain!"

Lekin kya tumne kabhi socha hai, ye message uske phone tak pahunchta kaise hai?

**[Story begins]**

Sabse pehle, tumhara message tumhare phone se WhatsApp ke system tak jaata hai.

Lekin ek interesting baat hai…

Tumhara message end-to-end encrypted hota hai. Matlab, message ka content sirf sender aur receiver ke devices hi padh sakte hain.

Ab WhatsApp ka server message ko sahi destination tak pahunchane mein help karta hai.

Agar dost online hai, message uske device tak deliver ho jaata hai.

Aur agar offline hai? Toh encrypted message temporarily server par wait kar sakta hai, jab tak uska device available na ho.

**[Reveal — slightly dramatic]**

Aur bas, isi process mein networking, servers, encryption aur databases jaise concepts ka role samajh aata hai.

**[Ending]**

Agli baar WhatsApp par message bhejo, toh yaad rakhna… ek simple text ke peeche poora software system kaam kar raha hota hai!

Aise tech concepts simple stories mein samajhne ke liye follow karo **Code Ki Class!**"""

# Pronunciation correction dictionary for tricky Hinglish words
PRONUNCIATION_DICT = {
    r"\bbhejo\b": "भेजो",
    r"\bbheja\b": "भेजा",
    r"\bbhej\b": "भेज",
    r"\bpahunchta\b": "पहुंचता",
    r"\bsocho\b": "सोचो",
    r"\byaad rakhna\b": "याद रखना",
    r"\bkaam kar raha\b": "काम कर रहा",
}

def normalize_hinglish_pronunciation(text: str) -> str:
    for pattern, replacement in PRONUNCIATION_DICT.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def clean_markdown_and_punctuation(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = text.replace("…", "... ")
    text = re.sub(r"[ \t]+", " ", text).strip()
    return normalize_hinglish_pronunciation(text)

def parse_script_into_scenes(script: str):
    tag_regex = re.compile(r"(?:\*\*|\#\#)?\[([^\]]+)\](?:\*\*|\#\#)?")
    parts = tag_regex.split(script)
    scenes = []
    
    i = 0
    current_tone = "story"
    while i < len(parts):
        chunk = parts[i].strip()
        if not chunk:
            i += 1
            continue
        tag_lower = chunk.lower()
        if any(k in tag_lower for k in ["hook", "curious", "energetic", "intro"]):
            current_tone = "hook"
            i += 1
            if i < len(parts):
                content = clean_markdown_and_punctuation(parts[i])
                if content:
                    scenes.append({"tone": "hook", "text": content})
            i += 1
        elif any(k in tag_lower for k in ["story", "explainer", "explanation", "body", "begins"]):
            current_tone = "story"
            i += 1
            if i < len(parts):
                content = clean_markdown_and_punctuation(parts[i])
                if content:
                    scenes.append({"tone": "story", "text": content})
            i += 1
        elif any(k in tag_lower for k in ["reveal", "dramatic", "twist", "surprise", "secret", "climax"]):
            current_tone = "reveal"
            i += 1
            if i < len(parts):
                content = clean_markdown_and_punctuation(parts[i])
                if content:
                    scenes.append({"tone": "reveal", "text": content})
            i += 1
        elif any(k in tag_lower for k in ["ending", "outro", "conclusion", "call to action", "cta"]):
            current_tone = "ending"
            i += 1
            if i < len(parts):
                content = clean_markdown_and_punctuation(parts[i])
                if content:
                    scenes.append({"tone": "ending", "text": content})
            i += 1
        else:
            content = clean_markdown_and_punctuation(chunk)
            if content:
                scenes.append({"tone": current_tone, "text": content})
            i += 1
    return scenes

async def test_smooth_directed():
    scenes = parse_script_into_scenes(USER_SCRIPT)
    print(f"Parsed {len(scenes)} scenes.")
    
    out_dir = Path("backend/user_voice_sample/smooth_test")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Use hi-IN-MadhurNeural for Aarav - authentic Hindi phonetics + tech English
    voice_name = "hi-IN-MadhurNeural"
    
    # Smooth, subtle prosody offsets (natural human vocal range, no jarring 10Hz cliffs)
    PROSODY_MAP = {
        "hook": {"rate": "+6%", "pitch": "+3Hz"},    # Engaging, curious, energetic
        "story": {"rate": "+4%", "pitch": "+1Hz"},   # Clear, warm, explanatory
        "reveal": {"rate": "+2%", "pitch": "+0Hz"},  # Slightly deliberate, grounded
        "ending": {"rate": "+6%", "pitch": "+3Hz"},  # Confident, upbeat CTA
    }
    
    wav_files = []
    
    for idx, s in enumerate(scenes):
        tone = s["tone"]
        text = s["text"]
        p = PROSODY_MAP.get(tone, {"rate": "+4%", "pitch": "+1Hz"})
        
        mp3_path = out_dir / f"scene_{idx}.mp3"
        wav_path = out_dir / f"scene_{idx}.wav"
        
        comm = edge_tts.Communicate(text, voice_name, rate=p["rate"], pitch=p["pitch"])
        await comm.save(str(mp3_path))
        
        # Convert to 24kHz mono WAV
        cmd_conv = [ffmpeg_exe, "-y", "-i", str(mp3_path), "-ar", "24000", "-ac", "1", str(wav_path)]
        subprocess.run(cmd_conv, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wav_files.append(wav_path)
        print(f"Scene {idx+1} ({tone}) generated with rate={p['rate']}, pitch={p['pitch']}")

    # Smooth crossfade assembly between scenes using FFmpeg acrossfade filter
    # If 4 files: [0][1]acrossfade=d=0.25:c1=tri:c2=tri[a01]; [a01][2]acrossfade=d=0.25...
    # This prevents any sudden audio cuts and sounds buttery smooth!
    inputs = []
    filter_parts = []
    
    for idx, w in enumerate(wav_files):
        inputs.extend(["-i", str(w)])
    
    # Chain acrossfade
    last_label = "[0]"
    for idx in range(1, len(wav_files)):
        next_input = f"[{idx}]"
        out_label = f"[a{idx}]" if idx < len(wav_files) - 1 else "[out_audio]"
        filter_parts.append(f"{last_label}{next_input}acrossfade=d=0.20:c1=tri:c2=tri{out_label}")
        last_label = out_label
        
    filter_complex = "; ".join(filter_parts)
    crossfaded_wav = out_dir / "crossfaded.wav"
    mastered_wav = out_dir / "smooth_mastered.wav"
    mastered_mp3 = out_dir / "smooth_mastered.mp3"
    
    cmd_fade = [ffmpeg_exe, "-y"] + inputs + ["-filter_complex", filter_complex, "-map", "[out_audio]", str(crossfaded_wav)]
    subprocess.run(cmd_fade, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Broadcast mastering
    filter_chain = "acompressor=threshold=-14dB:ratio=3.5:attack=10:release=80,equalizer=f=3200:t=q:w=1.2:g=3.0"
    subprocess.run([ffmpeg_exe, "-y", "-i", str(crossfaded_wav), "-af", filter_chain, "-ar", "24000", "-ac", "1", str(mastered_wav)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([ffmpeg_exe, "-y", "-i", str(mastered_wav), "-b:a", "192k", str(mastered_mp3)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    data, sr = sf.read(str(mastered_wav))
    print(f" Smooth Mastered Audio complete! Duration: {len(data)/sr:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_smooth_directed())
