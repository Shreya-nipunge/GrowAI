# rag_agent.py
# Place this file inside your `ai/rag/` folder for imports to work as below

import re
from rag_pipeline import rag_pipeline  # Your Step 3 RAG pipeline

# Importing CV models from cv/models/
from ..cv.models import predict_disease
from ..cv.models import analyze_soil

# Importing STT and TTS modules
from ..stt.whisper_infer import speech_to_text  # or whisper_infer if you prefer
from ..tts.google_tts import text_to_speech


def decide_tool(query: str):
    """
    Decide which tool to use based on keywords in the query.
    Can be upgraded to LLM-based intent classification later.
    """
    q = query.lower()

    # Voice commands
    if any(word in q for word in ["speak", "say this", "read aloud", "listen", "voice"]):
        return "tts"
    if any(word in q for word in ["listen to me", "what i say", "dictate", "voice input"]):
        return "stt"

    # Prediction/CV tasks
    if any(word in q for word in ["disease", "plant condition", "leaf spot", "blight"]):
        return "plant_disease"

    if any(word in q for word in ["soil analysis", "soil health", "soil nutrients"]):
        return "soil_analysis"

    # Default: use retriever
    return "retriever"


def agentic_rag(query: str):
    tool = decide_tool(query)

    if tool == "plant_disease":
        # For illustration, assuming query is image filepath or identifier
        prediction = predict_disease(query)
        return {
            "tool": "plant_disease_model",
            "result": prediction
        }

    elif tool == "soil_analysis":
        analysis = analyze_soil(query)
        return {
            "tool": "soil_analysis_model",
            "result": analysis
        }

    elif tool == "tts":
        audio_file_path = text_to_speech(query)
        return {
            "tool": "text_to_speech",
            "audio_file": audio_file_path
        }

    elif tool == "stt":
        text = speech_to_text(query)
        return {
            "tool": "speech_to_text",
            "text": text
        }

    else:
        response = rag_pipeline(query)
        return {
            "tool": "retriever",
            "answer": response["answer"],
            "context": response["context_used"]
        }


if __name__ == "__main__":
    user_input = input("Enter your query or command: ").strip()
    output = agentic_rag(user_input)

    print(f"\n--- Tool Used: {output['tool']} ---")
    if output["tool"] in ["plant_disease_model", "soil_analysis_model"]:
        print("Prediction / Analysis Result:")
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
        for i, chunk in enumerate(output["context"], 1):
            print(f"{i}. {chunk['content'][:200]}...")
