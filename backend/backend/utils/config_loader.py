import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env into environment

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "changeme")
