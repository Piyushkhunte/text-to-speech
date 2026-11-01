import asyncio
import re
from pathlib import Path
import edge_tts
import imageio_ffmpeg
import subprocess

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


def clean_markdown(text: str) -> str:
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    return text.strip()


def parse_script_into_scenes(script: str):
    # Regex to find tags like **[Hook — curious, energetic]** or [Story begins]
    tag_regex = re.compile(r'(?:\*\*|\#\#)?\[([^\]]+)\](?:\*\*|\#\#)?')
    
    parts = tag_regex.split(script)
    scenes = []
    
    # If the text starts with a tag: parts[0] is empty, parts[1] is tag, parts[2] is text, etc.
    if len(parts) == 1:
        # No tags found, single regular scene
        scenes.append({"tone": "story", "text": clean_markdown(script), "pause_after_ms": 300})
        return scenes
        
    i = 0
    current_tag = "story"
    while i < len(parts):
        chunk = parts[i].strip()
        if not chunk:
            i += 1
            continue
            
        # Check if this chunk is a tag or content
        tag_lower = chunk.lower()
        if any(k in tag_lower for k in ["hook", "curious", "energetic", "intro"]):
            current_tag = "hook"
            i += 1
            if i < len(parts):
                content = clean_markdown(parts[i])
                if content:
                    scenes.append({"tone": "hook", "text": content, "pause_after_ms": 400})
            i += 1
        elif any(k in tag_lower for k in ["story", "explainer", "explanation", "body", "begins"]):
            current_tag = "story"
            i += 1
            if i < len(parts):
                content = clean_markdown(parts[i])
                if content:
                    scenes.append({"tone": "story", "text": content, "pause_after_ms": 350})
            i += 1
        elif any(k in tag_lower for k in ["reveal", "dramatic", "twist", "surprise", "secret"]):
            current_tag = "reveal"
            i += 1
            if i < len(parts):
                content = clean_markdown(parts[i])
                if content:
                    scenes.append({"tone": "reveal", "text": content, "pause_after_ms": 400})
            i += 1
        elif any(k in tag_lower for k in ["ending", "outro", "conclusion", "call to action", "cta"]):
            current_tag = "ending"
            i += 1
            if i < len(parts):
                content = clean_markdown(parts[i])
                if content:
                    scenes.append({"tone": "ending", "text": content, "pause_after_ms": 100})
            i += 1
        else:
            # Regular text without a preceding tag
            scenes.append({"tone": current_tag, "text": clean_markdown(chunk), "pause_after_ms": 300})
            i += 1
            
    return scenes


async def generate_directed_story():
    scenes = parse_script_into_scenes(USER_SCRIPT)
    print(f"Parsed {len(scenes)} scenes from script:")
    for idx, s in enumerate(scenes):
        print(f"  Scene {idx+1} [{s['tone']}]: {s['text'][:50]}... (pause: {s['pause_after_ms']}ms)")

    out_dir = Path("backend/user_voice_sample/whatsapp_reel")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    segment_files = []
    
    # Voice configuration for Aarav (Tech Reel Creator)
    voice_name = "en-IN-PrabhatNeural" # Best for Roman Hinglish
    
    for idx, s in enumerate(scenes):
        tone = s["tone"]
        text = s["text"]
        
        # Ellipses replacement with micro pause comma
        speech_text = text.replace("…", "... ").replace("  ", " ")
        
        if tone == "hook":
            # Curious, energetic: +7Hz pitch, +10% rate
            rate = "+10%"
            pitch = "+7Hz"
        elif tone == "story":
            # Engaging, explanatory: +3Hz pitch, +6% rate
            rate = "+6%"
            pitch = "+3Hz"
        elif tone == "reveal":
            # Slightly dramatic, impactful: -3Hz pitch, +0% rate (deliberate)
            rate = "+1%"
            pitch = "-3Hz"
        elif tone == "ending":
            # Enthusiastic, CTA: +6Hz pitch, +9% rate
            rate = "+9%"
            pitch = "+6Hz"
        else:
            rate = "+6%"
            pitch = "+4Hz"
            
        seg_file = out_dir / f"scene_{idx}.mp3"
        comm = edge_tts.Communicate(speech_text, voice_name, rate=rate, pitch=pitch)
        await comm.save(str(seg_file))
        segment_files.append((seg_file, s["pause_after_ms"]))
        print(f"  Synthesized scene {idx+1} ({tone}) with rate={rate}, pitch={pitch}")

    # Generate silence files and concatenate
    concat_list = []
    concat_txt_path = out_dir / "concat_list.txt"
    
    for idx, (fpath, pause_ms) in enumerate(segment_files):
        # Convert to standard WAV 24000Hz
        wav_path = out_dir / f"scene_{idx}.wav"
        subprocess.run([ffmpeg_exe, "-y", "-i", str(fpath), "-ar", "24000", "-ac", "1", str(wav_path)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        concat_list.append(wav_path)
        
        if pause_ms > 0 and idx < len(segment_files) - 1:
            # Generate exact silence gap
            silence_path = out_dir / f"silence_{idx}.wav"
            sec = pause_ms / 1000.0
            cmd_silence = [
                ffmpeg_exe, "-y",
                "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono",
                "-t", str(sec),
                str(silence_path)
            ]
            subprocess.run(cmd_silence, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            concat_list.append(silence_path)

    with open(concat_txt_path, "w", encoding="utf-8") as f:
        for p in concat_list:
            escaped = str(p.resolve()).replace("\\", "/")
            f.write(f"file '{escaped}'\n")

    # Concatenate & apply broadcast studio mastering
    raw_joined = out_dir / "raw_joined.wav"
    mastered_wav = out_dir / "whatsapp_reel_mastered.wav"
    mastered_mp3 = out_dir / "whatsapp_reel_mastered.mp3"
    
    subprocess.run([ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt_path), "-c", "copy", str(raw_joined)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    filter_chain = "acompressor=threshold=-14dB:ratio=3.5:attack=10:release=80,equalizer=f=3200:t=q:w=1.2:g=3.0"
    subprocess.run([ffmpeg_exe, "-y", "-i", str(raw_joined), "-af", filter_chain, "-ar", "24000", "-ac", "1", str(mastered_wav)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([ffmpeg_exe, "-y", "-i", str(mastered_wav), "-b:a", "192k", str(mastered_mp3)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Calculate duration
    import soundfile as sf
    data, sr = sf.read(str(mastered_wav))
    dur = len(data) / sr
    print(f"\n Mastered WhatsApp Reel Audio complete! Total duration: {dur:.2f}s ({dur:.1f} sec Reel)")

if __name__ == "__main__":
    asyncio.run(generate_directed_story())
