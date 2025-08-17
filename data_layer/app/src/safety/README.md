# Call the safety function with that payload and expect the above response.”



# Safety Layer Interface (MVP)

Endpoint (example contract) - PROVIDED AS DOC FOR BACKEND:

Request payload (what the backend will send to safety):
{
  "user_query": "<original user text>",
  "candidate_answer": "<LLM/RAG answer text>",
  "nlu_confidence": 0.0-1.0,
  "retrieval_score": 0.0-1.0,
  "context": {
    "location": "district, state",
    "next7day_rain_mm": 12.3
  }
}

Safety response (what safety returns):
{
  "decision": "ok|warn|escalate",
  "confidence": 0.0-1.0,
  "flags": [
    {"rule":"pesticide_ban_check","severity":"high","match":"paraquat"}
  ],
  "escalate_payload": {
     "user_query": "...",
     "candidate_answer": "...",
     "reason": "banned pesticide/dosage exceed"
  }
}


