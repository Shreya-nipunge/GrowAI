# nlu_pipeline.py
# Agentic NLU pipeline for KrishiMitra AI

import json
from typing import Dict, Any
from deep_translator import GoogleTranslator
from transformers import pipeline

class KrishiMitraNLU:
    def __init__(self):
        print("Loading NLU models...")

        # Intent classification (zero-shot)
        self.intent_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )

        # Entity extraction (multilingual NER for Indian languages)
        self.entity_extractor = pipeline(
            "ner",
            model="Davlan/xlm-roberta-large-ner-hrl"
        )

        # Tool mapping (agentic decision layer)
        self.tool_map = {
            "get_crop_price": "Agmarknet_API",
            "weather_forecast": "Weather_API",
            "disease_detection": "Vision_Model",
            "general_query": "Knowledge_Base",
        }

    def detect_and_translate(self, user_message: str) -> Dict[str, str]:
        """Translate to English if needed."""
        # Translate using auto-detection
        translated_text = GoogleTranslator(source='auto', target='en').translate(user_message)
        
        # We cannot reliably get the detected language, so default to 'unknown' or 'auto'
        return {"lang": "auto", "translated_text": translated_text}


    def translate_response(self, text: str, target_lang: str) -> str:
        """Translate bot response back to user's language."""
        if target_lang != "en":
            return GoogleTranslator(source='en', target=target_lang).translate(text)
        return text

    def classify_intent(self, text: str) -> str:
        """Classify user intent using zero-shot classification."""
        candidate_labels = list(self.tool_map.keys())
        result = self.intent_classifier(text, candidate_labels=candidate_labels)
        intent = result['labels'][0]
        return intent

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text."""
        entities = self.entity_extractor(text)
        cleaned_entities = [
            {"entity": e.get("entity_group", e.get("entity")), "text": e["word"]}
            for e in entities
        ]
        return cleaned_entities

    def decide_action(self, intent: str) -> str:
        """Map intent to the corresponding tool or API."""
        return self.tool_map.get(intent, "LLM_Fallback")

    def process(self, user_message: str) -> Dict[str, Any]:
        """Full NLU pipeline execution."""
        lang_info = self.detect_and_translate(user_message)

        # Step 2: Intent classification
        intent = self.classify_intent(lang_info["translated_text"])

        # Step 3: Entity extraction
        entities = self.extract_entities(lang_info["translated_text"])

        # Step 4: Decide action
        action = self.decide_action(intent)

        # Step 5: Return structured plan
        return {
            "original_text": user_message,
            "detected_lang": lang_info["lang"],
            "translated_text": lang_info["translated_text"],
            "intent": intent,
            "entities": entities,
            "next_action": action
        }


if __name__ == "__main__":
    nlu = KrishiMitraNLU()
    test_input = "मुझे दिल्ली के मौसम के बारे में बताओ"
    result = nlu.process(test_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))
