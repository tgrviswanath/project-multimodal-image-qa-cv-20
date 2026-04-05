# GCP Deployment Guide — Project CV-20 Multimodal Image QA

---

## GCP Services for Multimodal Image QA

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Vertex AI Gemini Vision**          | Answer natural language questions about images — replace BLIP VQA            | Direct replacement for your BLIP VQA pipeline      |
| **Cloud Vision API**                 | Analyze image content to answer factual questions about scenes and objects   | When you need structured image Q&A                 |
| **Vertex AI Gemini Pro Vision**      | Gemini Pro Vision for visual question answering with detailed explanations   | When you need high-quality multimodal Q&A          |

> **Vertex AI Gemini Pro Vision** is the direct replacement for your BLIP VQA pipeline. It answers natural language questions about images — no model download needed, significantly better quality than BLIP.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + cv-service containers — serverless, scales to zero    | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------| 
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store uploaded images and Q&A results                                     |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track QA latency, question types, request volume                          |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Vertex AI Gemini Pro Vision        │
│ CV Service :8001  │    │ Visual question answering          │
│ BLIP VQA (~1GB)   │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create imageqa-cv-project --name="Multimodal Image QA"
gcloud config set project imageqa-cv-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com aiplatform.googleapis.com \
  storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create imageqa-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/imageqa-cv-project/imageqa-repo
docker build -f docker/Dockerfile.cv-service -t $AR/cv-service:latest ./cv-service
docker push $AR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Deploy to Cloud Run

```bash
gcloud run deploy cv-service \
  --image $AR/cv-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 4Gi --cpu 2

CV_URL=$(gcloud run services describe cv-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars CV_SERVICE_URL=$CV_URL
```

---

## Option B — Use Vertex AI Gemini Pro Vision

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import json

vertexai.init(project="imageqa-cv-project", location="europe-west2")
gemini = GenerativeModel("gemini-pro-vision")

def answer_question(image_bytes: bytes, question: str) -> dict:
    image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
    response = gemini.generate_content([
        image_part,
        f"Answer this question about the image concisely: {question}"
    ])
    return {
        "answer": response.text,
        "question": question,
        "confidence": 95.0
    }
```

Add to requirements.txt: `google-cloud-aiplatform>=1.50.0`

---

## CI/CD — GitHub Actions

```yaml
name: Deploy to GCP
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker europe-west2-docker.pkg.dev
      - run: |
          docker build -f docker/Dockerfile.backend \
            -t europe-west2-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/imageqa-repo/backend:${{ github.sha }} ./backend
          docker push europe-west2-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/imageqa-repo/backend:${{ github.sha }}
          gcloud run deploy backend \
            --image europe-west2-docker.pkg.dev/${{ secrets.GCP_PROJECT }}/imageqa-repo/backend:${{ github.sha }} \
            --region europe-west2 --platform managed
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (cv-service)     | 2 vCPU / 4 GB         | ~$20–30/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Vertex AI Gemini Vision    | Pay per token         | ~$5–15/month       |
| **Total (Option A)**       |                       | **~$32–48/month**  |
| **Total (Option B)**       |                       | **~$16–32/month**  |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete cv-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete imageqa-repo --location=$GCP_REGION --quiet
gcloud projects delete imageqa-cv-project
```
