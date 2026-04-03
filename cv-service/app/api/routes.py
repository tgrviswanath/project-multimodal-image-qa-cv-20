from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.core.qa import ask

router = APIRouter(prefix="/api/v1/cv", tags=["image-qa"])

ALLOWED = {"jpg", "jpeg", "png", "bmp", "webp"}


def _validate(filename: str):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported format: .{ext}")


@router.post("/ask")
async def ask_question(file: UploadFile = File(...), question: str = Form(...)):
    _validate(file.filename)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return ask(content, question.strip())
