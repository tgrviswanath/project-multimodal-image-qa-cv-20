import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.core.qa import ask
from app.core.validate import validate_image

router = APIRouter(prefix="/api/v1/cv", tags=["image-qa"])


@router.post("/ask")
async def ask_question(file: UploadFile = File(...), question: str = Form(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    validate_image(file, content)
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        return await asyncio.get_running_loop().run_in_executor(None, ask, content, question.strip())
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA error: {e}")
