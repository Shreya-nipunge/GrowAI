# src/safety/confidence.py
def compute_confidence(nlu_confidence: float, retrieval_score: float, risk_penalty: float):
    """
    nlu_confidence: 0-1
    retrieval_score: 0-1 (how good the retrieval was)
    risk_penalty: 0-1 (0 = no risk, 1 = maximum risk)
    """
    base = (nlu_confidence * 0.6) + (retrieval_score * 0.4)
    adjusted = base * (1 - 0.5 * risk_penalty)  # punish confidence when risk exists
    return round(adjusted, 3)
