"""
Visual Question Answering using BLIP (Salesforce/blip-vqa-base).
- Accepts image bytes + natural language question
- Returns text answer with confidence score
"""
from PIL import Image
import io
import torch
from transformers import BlipProcessor, BlipForQuestionAnswering
from app.core.config import settings

_processor = None
_model = None


def _get_model():
    global _processor, _model
    if _processor is None:
        try:
            _processor = BlipProcessor.from_pretrained(settings.BLIP_MODEL)
            _model = BlipForQuestionAnswering.from_pretrained(settings.BLIP_MODEL)
            _model.eval()
        except Exception as e:
            raise FileNotFoundError(f"BLIP model unavailable: {e}")
    return _processor, _model


def _load_image(image_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > settings.MAX_IMAGE_SIZE:
        scale = settings.MAX_IMAGE_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)))
    return img


def ask(image_bytes: bytes, question: str) -> dict:
    processor, model = _get_model()
    img = _load_image(image_bytes)

    inputs = processor(img, question, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, output_scores=True, return_dict_in_generate=True, max_new_tokens=20)

    answer = processor.decode(out.sequences[0], skip_special_tokens=True)

    # Compute confidence from first token score if available
    confidence = None
    if out.scores:
        probs = torch.softmax(out.scores[0][0], dim=-1)
        confidence = round(float(probs.max()) * 100, 2)

    return {
        "question": question,
        "answer": answer,
        "confidence": confidence,
    }
