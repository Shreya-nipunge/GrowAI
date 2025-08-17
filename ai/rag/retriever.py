import os
import requests
from typing import Any, Dict
from langchain_chroma import Chroma

from GrowAI.ai.rag.chromadb_setup import HFLLamaEmbeddings, EMBEDDING_MODEL, CHROMA_DB_PATH

# =============================
# 1. Load API Keys securely from .env
# =============================
from dotenv import load_dotenv
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGMARKNET_API_KEY = os.getenv("AGMARKNET_API_KEY")

if not OPENWEATHER_API_KEY:
    raise ValueError("❌ Missing OPENWEATHER_API_KEY in .env file")
if not AGMARKNET_API_KEY:
    raise ValueError("❌ Missing AGMARKNET_API_KEY in .env file")

# =============================
# 2. Real API Calls
# =============================
def fetch_weather(city: str, api_key: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"Weather in {city}: {temp}°C, {desc}"
    except Exception as e:
        return f"⚠️ Weather API error: {str(e)}"


def fetch_market_price(crop: str, api_key: str):
    url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key={api_key}&format=json&limit=1&filters[commodity]={crop}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("records"):
            record = data["records"][0]
            market = record.get("market", "Unknown")
            price = record.get("modal_price", "N/A")
            return f"Market price of {crop} in {market}: {price} INR/quintal"
        else:
            return f"No market data found for {crop}"
    except Exception as e:
        return f"⚠️ Agmarknet API error: {str(e)}"


# =============================
# 3. Retriever Setup
# =============================
def get_retriever(k: int = 4):
    """Load existing Chroma DB with proper embeddings and return a retriever."""
    if not os.path.exists(CHROMA_DB_PATH):
        raise FileNotFoundError("❌ Chroma vector DB not found. Run chromadb_setup.py first.")

    vectordb = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=HFLLamaEmbeddings(model_name=EMBEDDING_MODEL)
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": k})
    return retriever


# =============================
# 4. API Router
# =============================
def call_api_tool(query: str) -> Dict[str, Any]:
    query_lower = query.lower()

    # Weather queries
    if "weather" in query_lower or "temperature" in query_lower:
        city = query.split()[-1]
        return {"source": "openweather", "result": fetch_weather(city, api_key=OPENWEATHER_API_KEY)}

    # Market price queries
    if "price" in query_lower or "market" in query_lower:
        crop = query.split()[0]
        return {"source": "agmarknet", "result": fetch_market_price(crop, api_key=AGMARKNET_API_KEY)}

    # Fallback if no condition matches
    return {"source": "unknown", "result": "❌ Query not recognized. Try asking about weather or crop prices."}
