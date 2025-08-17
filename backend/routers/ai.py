from fastapi import APIRouter, Request, HTTPException
from tasks.celery_app import process_message_task

router = APIRouter()

VERIFY_TOKEN = "EAAPns20P7vwBPBr16vuZC1aeTLN7ZAW2qwc3a3cYzJqT9PbsC3rWut0fWYCwyCzeNFj8XIS8uYmBFZB6vsZCmpOB4XkRMhQ18CWoxIv7vvtsCtA8CHNhLKJQMYPbiGDnQ8ZAb1H0houReY46gph870JVkkYOWrZAFkUcr7fFZBNmQYZCcmJHD57kJrQRdHPOm4KKYQZDZD"  # Replace with your actual token


@router.get("/webhook")
async def verify_webhook(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    payload = await request.json()
    # Enqueue the incoming message payload to Celery for processing
    process_message_task.delay(payload)
    return {"status": "task received"}
