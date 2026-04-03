from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.core.service import ask_question
import httpx

router = APIRouter(prefix="/api/v1", tags=["image-qa"])


def _handle(e: Exception):
    if isinstance(e, httpx.ConnectError):
        raise HTTPException(status_code=503, detail="CV service unavailable")
    if isinstance(e, httpx.HTTPStatusError):
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask")
async def ask(file: UploadFile = File(...), question: str = Form(...)):
    try:
        content = await file.read()
        return await ask_question(file.filename, content, file.content_type or "image/jpeg", question)
    except Exception as e:
        _handle(e)
