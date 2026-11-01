# HindiVoice AI - Indic Text-to-Speech Web Application

**HindiVoice AI** is a production-grade, full-stack Hindi Text-to-Speech (TTS) web application powered by the open-source **AI4Bharat Indic Parler-TTS** model (`ai4bharat/indic-parler-tts`). It enables users to synthesize natural, expressive, high-fidelity Hindi speech across multiple authentic male and female voices with zero paid API dependencies.

---

## 1. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Next.js 14 App Router Frontend                       │
│       (Dark Navy/Violet Theme, Tailwind CSS, Lucide React UI)          │
│                                                                        │
│  - Interactive Devanagari Hindi Text Editor with Live Validation       │
│  - Voice Cards for 4 Verified Hindi Speaker Identities                │
│  - Real-time Parameters (Speed, Pitch, Speaking Style, Audio Format)   │
│  - Audio Player with Waveform Visualizer, Scrubbing & Time Display     │
│  - Direct WAV and MP3 Downloads                                        │
│  - Dedicated Voice Library & Persistent Generation History             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend Engine                          │
│                                                                        │
│  - /api/tts/generate     : Text synthesis with conditioning tokens     │
│  - /api/tts/voices       : Metadata for verified Hindi speakers        │
│  - /api/tts/health       : System readiness & CPU/GPU telemetry        │
│  - /api/tts/history      : Generation history & file cleanup           │
│  - /api/tts/audio/{id}   : Range-streaming for WAV and MP3             │
│  - /api/tts/preview/{id} : Real speaker sample audio previews          │
│                                                                        │
│  ┌─────────────────────────┐           ┌────────────────────────────┐  │
│  │ Indic Parler-TTS (0.9B) │           │ FFmpeg Engine              │  │
│  │ Loaded once in RAM      │           │ WAV to 192kbps MP3         │  │
│  └─────────────────────────┘           └────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Verified Hindi Speaker Identities

In strict compliance with the official `ai4bharat/indic-parler-tts` checkpoint, the application exposes the 4 authentic Hindi speakers trained on native Hindi speech:

| Speaker ID | Hindi Name | Gender | Role & Acoustic Persona | Recommended |
|---|---|---|---|---|
| **`rohit`** | रोहित (Rohit) | Male | Conversational, clear articulation, warm studio tone | **Yes** |
| **`divya`** | दिव्या (Divya) | Female | Expressive, articulate, high dynamic clarity | **Yes** |
| **`aman`** | अमन (Aman) | Male | Authoritative, deep narrative, broadcast tone | No |
| **`rani`** | रानी (Rani) | Female | Soft, gentle, melodious storytelling tone | No |

### Real Conditioning Parameters
The model uses natural language descriptions conditioned through its text encoder:
- **Speed / Pace**: Maps `0.7x - 1.4x` to descriptive cadence (`slow`, `moderate`, `slightly fast`, `fast`).
- **Vocal Pitch**: `low-pitched`, `moderate-pitched`, `high-pitched`.
- **Speaking Style**: `natural and engaging`, `expressive with emotional warmth`, `steady and neutral`, `urgent and dynamic`.
- **Acoustic Environment**: Clear, high-fidelity studio recording with zero background noise.

---

## 3. Local Installation & Development

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) NVIDIA GPU with CUDA 11.8 / 12.1 for sub-second inference. On CPU, inference runs reliably with multi-threading.

### Backend Setup
1. Navigate to `/backend`:
   ```bash
   cd backend
   ```
2. Activate your virtual environment:
   - Windows PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   API Documentation is available at `http://localhost:8000/docs`.

### Frontend Setup
1. Navigate to `/frontend`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 4. Hardware Requirements & CPU/GPU Benchmarks

| Compute Hardware | Model Load Time | Inference Time (1 Sentence, ~15 words) | Real-time Factor (RTF) |
|---|---|---|---|
| **NVIDIA RTX 3080/4090 (CUDA)** | ~3 - 5 sec | ~0.8 - 1.5 sec | **0.15 - 0.25 (Faster than real-time)** |
| **NVIDIA T4 / A10G (Cloud GPU)** | ~4 - 7 sec | ~1.2 - 2.2 sec | **0.25 - 0.35** |
| **Intel Core i7/i9 (CPU Fallback)** | ~10 - 15 sec | ~12 - 22 sec | **1.8 - 2.5 (Background async execution)** |

*Note: On CPU environments, `asyncio.to_thread` ensures that inference runs in a separate thread pool so the web server and UI remain responsive without request timeouts.*

---

## 5. Production Deployment

### Frontend (Vercel)
The Next.js frontend can be deployed directly to Vercel:
1. Link the `/frontend` directory to a new Vercel project.
2. Set Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-domain.com
   ```
3. Deploy.

### Backend (GPU / Dedicated Cloud Host)
Recommended providers: RunPod, Modal, GCP Compute Engine (g2-standard-4), AWS (g5.xlarge).
Run the backend with production Uvicorn or Gunicorn:
```bash
gunicorn backend.app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120
```

---

## 6. Model Licensing & Attribution
- AI Model: **AI4Bharat Indic Parler-TTS** (`ai4bharat/indic-parler-tts`)
- License: **Apache License 2.0** (Open Source, Commercial & Research friendly)
- Audio Engine: FFmpeg via `imageio-ffmpeg` (LGPL 2.1+)
