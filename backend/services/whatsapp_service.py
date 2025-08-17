from pymongo import MongoClient
from utils.config_loader import MONGO_URI
from tasks import process_message_task  # Import directly from tasks.py
import logging

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI)
db = client["whatsapp_db"]
raw_collection = db["raw_payloads"]

def handle_incoming_payload(payload: dict):
    result = raw_collection.insert_one({"data": payload})
    logger.info("Saved payload", extra={"inserted_id": str(result.inserted_id)})

    # Enqueue the task to Celery using the imported task
    process_message_task.delay(payload)
    logger.info("Task enqueued to Celery")  

import os
import requests

def send_whatsapp_message(to_number: str, message_text: str) -> dict:
    phone_number_id = os.getenv("15551744987")
    access_token = os.getenv("EAAPns20P7vwBPBr16vuZC1aeTLN7ZAW2qwc3a3cYzJqT9PbsC3rWut0fWYCwyCzeNFj8XIS8uYmBFZB6vsZCmpOB4XkRMhQ18CWoxIv7vvtsCtA8CHNhLKJQMYPbiGDnQ8ZAb1H0houReY46gph870JVkkYOWrZAFkUcr7fFZBNmQYZCcmJHD57kJrQRdHPOm4KKYQ")

    url = f"https://graph.facebook.com/v15.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text},
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

