# Project CV-20 - Multimodal Image QA

Microservice CV system that answers natural language questions about any image using BLIP (Bootstrapping Language-Image Pre-training) for visual question answering — no GPU required.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (React - Port 3000)                              │
│  axios POST /api/v1/ask                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  BACKEND  (FastAPI - Port 8000)                             │
│  httpx POST /api/v1/cv/ask  →  calls cv-service             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  CV SERVICE  (FastAPI - Port 8001)                          │
│  BLIP processor tokenizes image + text                      │
│  BLIP VQA model forward pass → decode top answer            │
│  Returns { answer, confidence, question }                   │
└─────────────────────────────────────────────────────────────┘
```

---

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

---

## What's Different from Earlier Projects

| | CV-05 (Image Similarity) | CV-20 (Multimodal QA) |
|---|---|---|
| Task | Find similar images | Answer questions about image |
| Model | CNN feature extractor + cosine | BLIP VQA (vision-language) |
| Input | Image only | Image + natural language question |
| Output | Similar image list | Text answer |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, MUI |
| Backend | FastAPI, httpx |
| CV | HuggingFace Transformers (BLIP VQA), PyTorch, Pillow |
| Model | Salesforce/blip-vqa-base (~1GB, auto-downloaded) |
| Deployment | Docker, docker-compose |

---

## Prerequisites

- Python 3.12+
- Node.js — run `nvs use 20.14.0` before starting the frontend
- 8GB RAM recommended (BLIP model ~1GB)

---

## Local Run

### Step 1 — Start CV Service (Terminal 1)

```bash
cd cv-service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
# BLIP model downloads ~1GB on first request
```

Verify: http://localhost:8001/health → `{"status":"ok"}`

### Step 2 — Start Backend (Terminal 2)

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 3 — Start Frontend (Terminal 3)

```bash
cd frontend
npm install && npm start
```

Opens at: http://localhost:3000

---

## Environment Files

### `backend/.env`

```
APP_NAME=Multimodal Image QA API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
CV_SERVICE_URL=http://localhost:8001
```

### `cv-service/.env`

```
MODEL_NAME=Salesforce/blip-vqa-base
```

### `frontend/.env`

```
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Run

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| CV Service docs | http://localhost:8001/docs |

---

## Run Tests

```bash
cd cv-service && venv\Scripts\activate
pytest ../tests/cv-service/ -v

cd backend && venv\Scripts\activate
pytest ../tests/backend/ -v
```

---

## Project Structure

```
project-multimodal-image-qa-cv-20/
├── frontend/                    ← React (Port 3000)
├── backend/                     ← FastAPI (Port 8000)
├── cv-service/                  ← FastAPI CV (Port 8001)
│   └── app/
│       ├── api/routes.py
│       ├── core/vqa.py          ← BLIP VQA inference
│       └── main.py
├── samples/
├── tests/
├── docker/
└── docker-compose.yml
```

---

## API Reference

```
POST /api/v1/ask
Body:     { "image": "<base64>", "question": "What color is the car?" }
Response: {
  "answer": "red",
  "confidence": 94.2,
  "question": "What color is the car?"
}
```

---

## Model

Salesforce/blip-vqa-base from HuggingFace — auto-downloaded on first request (~1GB).
