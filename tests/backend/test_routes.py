from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "question": "What color is the car?",
    "answer": "red",
    "confidence": 91.5,
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.ask_question", new_callable=AsyncMock, return_value=MOCK_RESULT)
def test_ask_endpoint(mock_ask):
    r = client.post(
        "/api/v1/ask",
        files={"file": ("test.jpg", b"fake", "image/jpeg")},
        data={"question": "What color is the car?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["answer"] == "red"
    assert data["question"] == "What color is the car?"
