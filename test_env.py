import os
from dotenv import load_dotenv

load_dotenv()

print("Phone Number ID:", os.getenv("WHATSAPP_PHONE_NUMBER_ID"))
print("Access Token:", os.getenv("WHATSAPP_ACCESS_TOKEN"))
print("Business Account ID:", os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID"))
