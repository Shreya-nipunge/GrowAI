# nlu_pipeline.py
# Agentic NLU pipeline for KrishiMitra AI

import json
import re
from typing import Dict, Any

from transformers import pipeline
from googletrans import Translator


class KrishiMitraNLU:
    def __init__(self):
        print("Loading NLU models...")

        # Language detection / translation
        self.translator = Translator()

        # Intent + entity extraction
        self.intent_classifier = pipeline(
            "text-classification",
            model="facebook/bart-large-mnli"  # Multi-domain zero-shot intent detection
        )

        self.entity_extractor = pipeline(
            "ner",
            model="Davlan/xlm-roberta-large-ner-hrl"  # Multilingual NER for Indian langs
        )

        # Tool mapping (agentic decision layer)
        self.tool_map = {
            "get_crop_price": "eNAM_API",
            "weather_forecast": "Weather_API",
            "disease_detection": "Vision_Model",
            "general_query": "Knowledge_Base",
        }

    def detect_and_translate(self, text: str) -> Dict[str, str]:
        """Detect language and translate to English if needed."""
        detection = self.translator.detect(text)
        lang = detection.lang
        translated_text = text

        if lang != "en":
            translated_text = self.translator.translate(text, src=lang, dest="en").text

        return {"lang": lang, "translated_text": translated_text}

    def classify_intent(self, text: str) -> str:
        """Classify user intent using zero-shot classification."""
        candidate_labels = list(self.tool_map.keys())
        result = self.intent_classifier(text, candidate_labels)
        intent = result[0]['label']
        return intent

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text."""
        entities = self.entity_extractor(text)
        cleaned_entities = [
            {"entity": e["entity_group"], "text": e["word"]}
            for e in entities
        ]
        return cleaned_entities

    def decide_action(self, intent: str) -> str:
        """Map intent to the corresponding tool or API."""
        return self.tool_map.get(intent, "LLM_Fallback")

    def process(self, user_message: str) -> Dict[str, Any]:
        """Full NLU pipeline execution."""
        # Step 1: Detect language & translate
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
