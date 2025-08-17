
from fastapi import APIRouter, Request, Query, HTTPException
import logging
from backend.tasks.celery_app import process_message_task

router = APIRouter()

# Define your webhook verify token here (should match WhatsApp configuration)
VERIFY_TOKEN = "EAAPns20P7vwBPBr16vuZC1aeTLN7ZAW2qwc3a3cYzJqT9PbsC3rWut0fWYCwyCzeNFj8XIS8uYmBFZB6vsZCmpOB4XkRMhQ18CWoxIv7vvtsCtA8CHNhLKJQMYPbiGDnQ8ZAb1H0houReY46gph870JVkkYOWrZAFkUcr7fFZBNmQYZCcmJHD57kJrQRdHPOm4KKYQ"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return int(hub_challenge)
    else:
        logger.warning(f"Webhook verification failed: Mode={hub_mode}, Token={hub_verify_token}")
        raise HTTPException(status_code=403, detail="Invalid verification token")

@router.post("/webhook")
async def webhook_post(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received webhook data: {data}")
        
        # Call Celery task to process incoming data asynchronously
        process_message_task.delay(data)
        
        return {"status": "Task submitted"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook data")
