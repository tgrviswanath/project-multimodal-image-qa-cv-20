import httpx
from app.core.config import settings

CV_URL = settings.CV_SERVICE_URL


async def ask_question(filename: str, content: bytes, content_type: str, question: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CV_URL}/api/v1/cv/ask",
            files={"file": (filename, content, content_type)},
            data={"question": question},
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json()
