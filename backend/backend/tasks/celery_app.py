
from celery import Celery
import logging
from ..utils.config_loader import CELERY_BROKER_URL, CELERY_RESULT_BACKEND 



logger = logging.getLogger(__name__)

celery = Celery(
    "whatsapp_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery.task(name="process_message_task")
def process_message_task(payload):
    logger.info("Processing payload", extra={"payload": payload})
    # Implement your Celery task logic here 

from dotenv import load_dotenv
import os

load_dotenv()  # load variables from .env file

phone_number_id = os.getenv("15551744987")
access_token = os.getenv("EAAPns20P7vwBPBr16vuZC1aeTLN7ZAW2qwc3a3cYzJqT9PbsC3rWut0fWYCwyCzeNFj8XIS8uYmBFZB6vsZCmpOB4XkRMhQ18CWoxIv7vvtsCtA8CHNhLKJQMYPbiGDnQ8ZAb1H0houReY46gph870JVkkYOWrZAFkUcr7fFZBNmQYZCcmJHD57kJrQRdHPOm4KKYQZDZ")
business_account_id = os.getenv("741561912010506") 

from celery import shared_task
from ..services.whatsapp_service import send_whatsapp_message



@shared_task
def process_message_task(data):
    sender_number = data.get("from")  # adjust based on your webhook payload structure
    reply_text = "Thanks for messaging GrowAI! How can we help?"

    send_whatsapp_message(sender_number, reply_text) 





