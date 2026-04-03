from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from PIL import Image
import io
import torch
from app.main import app

client = TestClient(app)


def _sample_image() -> bytes:
    img = Image.new("RGB", (300, 300), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _mock_blip():
    processor = MagicMock()
    processor.return_value = {"input_ids": torch.zeros((1, 10), dtype=torch.long)}
    processor.decode.return_value = "red"
    model = MagicMock()
    scores = [torch.softmax(torch.randn(1, 30522), dim=-1)]
    model.generate.return_value = MagicMock(
        sequences=torch.zeros((1, 5), dtype=torch.long),
        scores=scores,
    )
    return processor, model


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@patch("app.core.qa._get_model", return_value=_mock_blip())
def test_ask_question(mock_model):
    r = client.post(
        "/api/v1/cv/ask",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")},
        data={"question": "What color is the sky?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "question" in data


def test_ask_unsupported_format():
    r = client.post(
        "/api/v1/cv/ask",
        files={"file": ("test.gif", b"GIF89a", "image/gif")},
        data={"question": "What is this?"},
    )
    assert r.status_code == 400


def test_ask_empty_question():
    r = client.post(
        "/api/v1/cv/ask",
        files={"file": ("test.jpg", _sample_image(), "image/jpeg")},
        data={"question": "   "},
    )
    assert r.status_code == 400
