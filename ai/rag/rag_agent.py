# rag_agent.py
# Place this file inside your ai/rag/ folder

import os
from typing import Dict, Any
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGMARKNET_API_KEY = os.getenv("AGMARKNET_API_KEY")

# -----------------------------
# NLU Pipeline
# -----------------------------
from GrowAI.ai.nlu.nlu_pipeline import KrishiMitraNLU
nlu = KrishiMitraNLU()

# -----------------------------
# RAG imports
# -----------------------------
from GrowAI.ai.rag.retriever import get_retriever
from GrowAI.ai.rag.rag_pipeline import build_rag_chain, query_rag

# -----------------------------
# CV Models
# -----------------------------
from GrowAI.ai.cv.plant_disease_model import predict_disease
from GrowAI.ai.cv.soil_analysis import predict_crop  # Soil analysis / plant prediction

# -----------------------------
# TTS / STT
# -----------------------------
from GrowAI.ai.stt.whisper_infer import transcribe as whisper_transcribe
from GrowAI.ai.stt.vosk_infer import transcribe as vosk_transcribe
from GrowAI.ai.tts.google_tts import GoogleTTS

# -----------------------------
# External APIs (Weather & Market)
# -----------------------------
import requests

def fetch_weather(city: str):
    """Fetch weather data using OpenWeather API."""
    if not OPENWEATHER_API_KEY:
        return "❌ OpenWeather API key missing."
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if response.status_code == 200:
            desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            return f"🌤 Weather in {city}: {desc}, {temp}°C"
        else:
            return f"❌ Weather API error: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"❌ Weather API call failed: {str(e)}"

def fetch_market_price(commodity: str, state: str = "Maharashtra"):
    """Fetch market price data using Agmarknet API (dummy example)."""
    if not AGMARKNET_API_KEY:
        return "❌ Agmarknet API key missing."
    
    url = f"https://api.agmarknet.gov.in/{commodity}?state={state}&apikey={AGMARKNET_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()  # adapt as per actual API response
    except Exception as e:
        return f"❌ Market API call failed: {str(e)}"

# -----------------------------
# Tool Decision via NLU
# -----------------------------
def decide_tool(query: str) -> str:
    """
    Use NLU to detect intent and map to agentic tools
    """
    nlu_result = nlu.process(query)
    action = nlu_result.get("next_action", "general_query")

    # Map NLU actions to internal tools
    action_map = {
        "Vision_Model": "plant_disease",
        "Agmarknet_API": "market_price",
        "Weather_API": "weather",
        "Soil_Model": "soil_analysis",   # add if you map soil analysis separately
        "Speech_To_Text": "stt",
        "Text_To_Speech": "tts",
        "Knowledge_Base": "retriever",
    }

    return action_map.get(action, "retriever")

# -----------------------------
# Agentic RAG
# -----------------------------
class AgenticRAG:
    """
    Agentic RAG agent
    """

    def __init__(self, model_name="llama3-70b-8192"):
        print("🚀 Initializing Agentic RAG...")
        self.retriever = get_retriever()
        self.qa_chain = build_rag_chain(model_name=model_name)

    def handle_query(self, query: str) -> Dict[str, Any]:
        tool = decide_tool(query)

        if tool == "plant_disease":
            prediction = predict_disease(query)
            return {"tool": "plant_disease_model", "result": prediction}

        elif tool == "soil_analysis":
            analysis = predict_crop(query)
            return {"tool": "soil_analysis_model", "result": analysis}

        elif tool == "weather":
            city = query.split("in")[-1].strip() if "in" in query.lower() else "Mumbai"
            weather = fetch_weather(city)
            return {"tool": "weather_api", "result": weather}

        elif tool == "market_price":
            commodity = query.split("price of")[-1].strip().capitalize() if "price of" in query.lower() else "Wheat"
            market_data = fetch_market_price(commodity)
            return {"tool": "market_api", "result": market_data}

        elif tool == "tts":
            audio_file_path = GoogleTTS().speak(query)
            return {"tool": "text_to_speech", "audio_file": audio_file_path}

        elif tool == "stt":
            # Default to Whisper, could add option to switch to Vosk
            text = whisper_transcribe(query)
            return {"tool": "speech_to_text", "text": text}

        else:  # Default: RAG retrieval
            answer, context_chunks = query_rag(self.qa_chain, query)
            context = [{"content": doc.page_content, "metadata": doc.metadata} for doc in context_chunks]
            return {"tool": "retriever", "answer": answer, "context_used": context}

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    agent = AgenticRAG()
    print("✅ Agentic RAG ready!\n")

    while True:
        user_input = input("Enter your query (or 'exit'): ").strip()
        if user_input.lower() == "exit":
            break

        output = agent.handle_query(user_input)

        print(f"\n--- Tool Used: {output['tool']} ---")
        if output["tool"] in ["plant_disease_model", "soil_analysis_model"]:
            print("Result:")
            print(output["result"])
        elif output["tool"] in ["weather_api", "market_api"]:
            print("Result:")
            print(output["result"])
        elif output["tool"] == "text_to_speech":
            print(f"Audio file created at: {output['audio_file']}")
        elif output["tool"] == "speech_to_text":
            print("Recognized Text:")
            print(output["text"])
        else:
            print("Answer:")
            print(output["answer"])
            print("\nRelevant Context Chunks:")
            for i, chunk in enumerate(output["context_used"], 1):
                print(f"{i}. {chunk['content'][:200]}...")
        print("\n" + "-"*50 + "\n")
