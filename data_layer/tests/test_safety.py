# tests/test_safety.py
from src.safety.checker import check_text_against_rules, decision_from_flags
from src.safety.confidence import compute_confidence

def test_paraquat_escalate():
    text = "Apply paraquat 600 ml per acre"
    flags = check_text_against_rules(text)
    assert any(f['rule'] == 'pesticide_ban_check' for f in flags)
    dec = decision_from_flags(flags)
    assert dec['escalate'] is True

def test_confidence_penalty():
    low_conf = compute_confidence(0.8, 0.7, 1.0)
    assert 0 <= low_conf < 0.8  # penalized because risk=1.0
