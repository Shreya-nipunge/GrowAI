# rag_agent.py
# Place this file inside your ai/rag/ folder

import os
from typing import Dict, Any


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
from GrowAI.ai.stt.whisper_infer import transcribe
from GrowAI.ai.tts.google_tts import GoogleTTS


def decide_tool(query: str) -> str:
    """
    Use NLU to detect intent and map to agentic tools
    """
    nlu_result = nlu.process(query)
    action = nlu_result["next_action"]

    # Map NLU actions to tools
    action_map = {
        "disease_detection": "plant_disease",
        "get_crop_price": "soil_analysis",
        "general_query": "retriever",
        "weather_forecast": "retriever",
    }

    return action_map.get(action, "retriever")


class AgenticRAG:
    """
    Agentic RAG agent
    """

    def __init__(self, model_name="llama3-70b-8192"):
        print("Initializing Agentic RAG...")
        self.retriever = get_retriever()
        self.qa_chain = build_rag_chain(self.retriever, model_name=model_name)

    def handle_query(self, query: str) -> Dict[str, Any]:
        tool = decide_tool(query)

        if tool == "plant_disease":
            prediction = predict_disease(query)
            return {"tool": "plant_disease_model", "result": prediction}

        elif tool == "soil_analysis":
            analysis = predict_crop(query)  # Or analyze_soil(query)
            return {"tool": "soil_analysis_model", "result": analysis}

        elif tool == "tts":
            audio_file_path = GoogleTTS().speak(query)
            return {"tool": "text_to_speech", "audio_file": audio_file_path}

        elif tool == "stt":
            text = transcribe(query)
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
