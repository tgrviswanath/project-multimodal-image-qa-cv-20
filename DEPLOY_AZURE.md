# Azure Deployment Guide — Project CV-20 Multimodal Image QA

---

## Azure Services for Multimodal Image QA

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure OpenAI Vision (GPT-4o)**     | Answer natural language questions about images — replace BLIP VQA            | Direct replacement for your BLIP VQA pipeline      |
| **Azure AI Vision**                  | Analyze image content to answer factual questions about scenes and objects   | When you need structured image Q&A                 |
| **Azure OpenAI Vision**              | GPT-4V for visual question answering with detailed explanations              | When you need high-quality multimodal Q&A          |

> **Azure OpenAI GPT-4o** is the direct replacement for your BLIP VQA pipeline. It answers natural language questions about images — no model download needed, significantly better quality than BLIP.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, cv-service)        | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 4. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store uploaded images and Q&A results                                    |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track QA latency, question types, request volume                     |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure OpenAI GPT-4o Vision         │
│ CV Service :8001  │    │ Visual question answering          │
│ BLIP VQA (~1GB)   │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-image-qa --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-image-qa --name imageqaacr --sku Basic --admin-enabled true
az acr login --name imageqaacr
ACR=imageqaacr.azurecr.io
docker build -f docker/Dockerfile.cv-service -t $ACR/cv-service:latest ./cv-service
docker push $ACR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Deploy Container Apps

```bash
az containerapp env create --name imageqa-env --resource-group rg-image-qa --location uksouth

az containerapp create \
  --name cv-service --resource-group rg-image-qa \
  --environment imageqa-env --image $ACR/cv-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 2 --memory 4.0Gi

az containerapp create \
  --name backend --resource-group rg-image-qa \
  --environment imageqa-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars CV_SERVICE_URL=http://cv-service:8001
```

---

## Option B — Use Azure OpenAI GPT-4o Vision

```python
from openai import AzureOpenAI
import base64

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01"
)

def answer_question(image_bytes: bytes, question: str) -> dict:
    image_b64 = base64.b64encode(image_bytes).decode()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            {"type": "text", "text": f"Answer this question about the image concisely: {question}"}
        ]}],
        max_tokens=200
    )
    return {
        "answer": response.choices[0].message.content,
        "question": question,
        "confidence": 95.0
    }
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost          |
|--------------------------|-----------|--------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month      |
| Container Apps (cv-svc)  | 2 vCPU    | ~$25–35/month      |
| Container Registry       | Basic     | ~$5/month          |
| Static Web Apps          | Free      | $0                 |
| Azure OpenAI (GPT-4o)    | Pay per token | ~$5–20/month   |
| **Total (Option A)**     |           | **~$40–55/month**  |
| **Total (Option B)**     |           | **~$20–40/month**  |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-image-qa --yes --no-wait
```
