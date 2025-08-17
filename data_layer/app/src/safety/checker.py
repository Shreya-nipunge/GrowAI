# src/safety/checker.py
import json, re
from typing import Dict, Any

RULES_PATH = "app/data/offline_packs/safety_rules.json"

def load_rules():
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)["rules"]

def check_text_against_rules(text: str, rules=None):
    if rules is None:
        rules = load_rules()
    flags = []
    text_l = text.lower()
    for r in rules:
        if r.get("banned_keywords"):
            for kw in r["banned_keywords"]:
                if kw.lower() in text_l:
                    flags.append({"rule": r["id"], "action": r["action"], "severity": r["severity"], "match": kw})
        if r.get("pattern"):
            m = re.search(r["pattern"], text, flags=re.I)
            if m:
                # simple numeric check - the first group
                try:
                    num = int(m.group(1))
                except:
                    num = None
                if num is not None:
                    if num < r.get("min", -999999) or num > r.get("max", 999999):
                        flags.append({"rule": r["id"], "action": r["action"], "severity": r["severity"], "match": m.group(0)})
        # extend with logical_conflict later (needs external context like weather)
    return flags

def decision_from_flags(flags):
    if not flags:
        return {"decision": "ok", "escalate": False, "flags": []}
    # escalate if any high severity
    for f in flags:
        if f["severity"] == "high" or f["action"] == "escalate":
            return {"decision": "escalate", "escalate": True, "flags": flags}
    return {"decision": "warn", "escalate": False, "flags": flags}

# quick CLI
if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:]) or "Apply 600 ml of paraquat to the field"
    flags = check_text_against_rules(text)
    print(flags)
    print(decision_from_flags(flags))
