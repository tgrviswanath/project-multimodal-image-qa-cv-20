# Project 20 - Multimodal Image QA (CV)

Ask natural language questions about any image. Uses BLIP (Bootstrapping Language-Image Pre-training) for visual question answering — no GPU required.

## Architecture

```
Frontend :3000  →  Backend :8000  →  CV Service :8001
  React/MUI        FastAPI/httpx      FastAPI/BLIP (HuggingFace)
```

## How It Works

```
Image + Question uploaded
    ↓
BLIP processor tokenizes image + text
    ↓
BLIP VQA model forward pass
    ↓
Decode top answer token
    ↓
Return: answer + confidence
```

## What's Different from Earlier Projects

| | Project 05 (Image Similarity) | Project 20 (Multimodal QA) |
|---|---|---|
| Task | Find similar images | Answer questions about image |
| Model | CNN feature extractor + FAISS | BLIP VQA (vision-language) |
| Input | Image only | Image + natural language question |
| Output | Similar image list | Text answer |

## Local Run

```bash
# Terminal 1 - CV Service (BLIP model downloads ~1GB on first run)
cd cv-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

- CV Service docs: http://localhost:8001/docs
- Backend docs:   http://localhost:8000/docs
- UI:             http://localhost:3000

## Docker

```bash
docker-compose up --build
```

## Model
Salesforce/blip-vqa-base from HuggingFace — auto-downloaded on first request (~1GB).
