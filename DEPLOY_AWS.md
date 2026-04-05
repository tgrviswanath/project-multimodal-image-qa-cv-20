# AWS Deployment Guide — Project CV-20 Multimodal Image QA

---

## AWS Services for Multimodal Image QA

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Bedrock**         | Claude Vision / Titan Vision for visual question answering via prompt        | Replace your BLIP VQA pipeline                     |
| **Amazon Rekognition**     | Detect objects, text, and scenes to answer factual questions about images    | When you need structured image Q&A                 |
| **Amazon Bedrock**         | Claude 3 Sonnet/Haiku with vision — answer any question about any image      | Direct replacement for BLIP VQA model              |

> **Amazon Bedrock with Claude 3 Vision** is the direct replacement for your BLIP VQA pipeline. It answers natural language questions about images — no model download needed, better quality than BLIP.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + cv-service containers in a private VPC                | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 4. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded images and Q&A results                                     |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track QA latency, question types, request volume                          |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Bedrock (Claude 3 Vision)   │
│ CV Service :8001  │    │ Visual question answering          │
│ BLIP VQA (~1GB)   │    │ No model download needed           │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name imageqa/cv-service --region $AWS_REGION
aws ecr create-repository --repository-name imageqa/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.cv-service -t $ECR/imageqa/cv-service:latest ./cv-service
docker push $ECR/imageqa/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/imageqa/backend:latest ./backend
docker push $ECR/imageqa/backend:latest
```

---

## Step 2 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name imageqa-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/imageqa/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CV_SERVICE_URL": "http://cv-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "2 vCPU", "Memory": "4 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Bedrock Claude 3 Vision

```python
import boto3, json, base64

bedrock = boto3.client("bedrock-runtime", region_name="eu-west-2")

def answer_question(image_bytes: bytes, question: str) -> dict:
    image_b64 = base64.b64encode(image_bytes).decode()
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                {"type": "text", "text": f"Answer this question about the image concisely: {question}"}
            ]}]
        }),
        contentType="application/json"
    )
    answer = json.loads(response["body"].read())["content"][0]["text"]
    return {"answer": answer, "question": question, "confidence": 95.0}
```

---

## CI/CD — GitHub Actions

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: eu-west-2
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -f docker/Dockerfile.backend \
            -t ${{ secrets.ECR_REGISTRY }}/imageqa/backend:${{ github.sha }} ./backend
          docker push ${{ secrets.ECR_REGISTRY }}/imageqa/backend:${{ github.sha }}
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 2 vCPU / 4 GB     | ~$30–40/month      |
| App Runner (cv-service)    | 2 vCPU / 4 GB     | ~$30–40/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Amazon Bedrock (Claude 3)  | Pay per token     | ~$5–15/month       |
| **Total (Option A)**       |                   | **~$63–87/month**  |
| **Total (Option B)**       |                   | **~$38–62/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name imageqa/backend --force
aws ecr delete-repository --repository-name imageqa/cv-service --force
```
