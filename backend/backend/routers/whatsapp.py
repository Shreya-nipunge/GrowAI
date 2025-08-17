
from fastapi import APIRouter, Request, Query, Response, HTTPException
import logging

router = APIRouter()

VERIFY_TOKEN = "EAAPns20P7vwBPBr16vuZC1aeTLN7ZAW2qwc3a3cYzJqT9PbsC3rWut0fWYCwyCzeNFj8XIS8uYmBFZB6vsZCmpOB4XkRMhQ18CWoxIv7vvtsCtA8CHNhLKJQMYPbiGDnQ8ZAb1H0houReY46gph870JVkkYOWrZAFkUcr7fFZBNmQYZCcmJHD57kJrQRdHPOm4KKYQZDZD"
logger = logging.getLogger(__name__)

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info(f"Webhook verified successfully with challenge: {hub_challenge}")
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        logger.warning(f"Webhook verification failed: Mode={hub_mode}, Token={hub_verify_token}")
        raise HTTPException(status_code=403, detail="Invalid verification token")

@router.post("/webhook")
async def receive_message(request: Request):
    try:
        data = await request.json()
        logger.info(f"Received webhook data: {data}")
        # TODO: Call your async task or processing logic here
        return {"status": "Message received"}
    except Exception as e:
        logger.error(f"Error processing webhook message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")
