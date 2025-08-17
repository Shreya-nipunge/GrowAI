from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_webhook_verification():
    response = client.get(
        "/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "h@ckathon23",
            "hub.challenge": "test_challenge"
        }
    )
    assert response.status_code == 200
    assert response.text == "test_challenge"

def test_webhook_post():
    sample_payload = {"entry": [{"id": "abc123", "changes": []}]}
    response = client.post("/whatsapp/webhook", json=sample_payload)
    assert response.status_code == 200
    assert response.json() == {"status": "received"}
