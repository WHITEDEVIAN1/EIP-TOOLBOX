# 🧰 ToolForge

> A powerful, **100% open-source** universal file toolbox for **Image, Audio & Document** processing — enhanced with local AI.

Built by Satvik & AI Team (Antigravity · Claude Code · Qwen · DeepSeek)

---

## ✨ Toolboxes

| Toolbox | Features |
|---------|----------|
| 🖼️ **Image** | Convert, resize, crop, rotate, filters (300+), background removal, upscaling, OCR, watermark, metadata, forensics |
| 🎵 **Audio** | Convert, trim, merge, normalize, noise reduction, transcription (Whisper), stem separation (Demucs), TTS |
| 📄 **Document** | PDF tools (merge/split/compress/OCR), Office conversion, Markdown export, archive manager |

## 🤖 AI-Powered Features (Local, No API Keys)
- 🔍 **Smart tool suggestions** — Qwen 2.5 fine-tuned
- 🎤 **Speech-to-text** — faster-whisper (Whisper)
- 🖼️ **Image upscaling** — Real-ESRGAN
- 🎸 **Stem separation** — Demucs
- 🗑️ **Background removal** — rembg (U2Net)

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/yourteam/toolforge

# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 🏗️ Stack
- **Backend:** Python · FastAPI · Pillow · OpenCV · FFmpeg · PyDub · Librosa · PyPDF2
- **Frontend:** React · Vite · Tailwind CSS
- **AI (Local):** Ollama · faster-whisper · rembg · Real-ESRGAN · Demucs
- **Fine-tuning:** Unsloth · QLoRA · Hugging Face

## 📁 Structure
```
toolforge/
├── backend/          # FastAPI Python backend
│   ├── app/          # Main app, routes, config
│   ├── modules/      # image/, audio/, document/
│   └── ai/           # Local AI model wrappers
├── frontend/         # React + Vite frontend
├── models/           # Fine-tuned model weights
├── scripts/          # Setup, download, benchmark scripts
├── tests/            # Integration tests
└── docs/             # API docs & guides
```

## 📜 License
Apache 2.0 — Free for personal & commercial use.
