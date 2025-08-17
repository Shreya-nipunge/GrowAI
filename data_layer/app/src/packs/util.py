import json

def load_json_with_context(path: str):
    """Load JSON file with better error messages (line/col)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"{path}: JSON syntax error at line {e.lineno}, col {e.colno}: {e.msg}")

