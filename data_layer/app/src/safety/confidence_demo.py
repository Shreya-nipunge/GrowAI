# src/safety/confidence_demo.py
from src.safety.confidence import compute_confidence
import sys

def simple_risk_from_text(text: str):
    t = text.lower()
    # Very small heuristic demo: paraquat or large dosage -> high risk
    if "paraquat" in t or "monocrotophos" in t:
        return 1.0
    if "ml" in t:
        # crude: large numbers -> higher penalty
        import re
        m = re.search(r'([0-9]+)\s*(ml|g|kg|ltr|litre)', t)
        if m:
            n = int(m.group(1))
            return 1.0 if n > 500 else 0.5 if n>100 else 0.2
    return 0.0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/safety/confidence_demo.py \"candidate text\"")
        sys.exit(1)
    text = " ".join(sys.argv[1:])
    risk = simple_risk_from_text(text)
    # example NLU & retrieval confidences for demo:
    nlu_conf = 0.8
    retrieval_score = 0.7
    score = compute_confidence(nlu_conf, retrieval_score, risk)
    print("text:", text)
    print("risk_penalty:", risk)
    print("computed_confidence:", score)
