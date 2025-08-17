# app/data_ingest.py
import json, glob, os
from pathlib import Path

PACK_DIR = Path(__file__).parent / "data" / "offline_packs"
OUT_DIR = Path(__file__).parent / "data" / "ingested"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def normalize_crop(c):
    # example mapping - adapt to your schema
    return {
        "id": c.get("id") or c.get("crop_id") or c.get("name"),
        "name": c.get("name"),
        "season": c.get("season"),
        "soil": c.get("soil_requirements"),
        "irrigation": c.get("irrigation"),
        "pests": c.get("pests", []),
        "notes": c.get("notes", "")
    }

def main():
    for p in PACK_DIR.glob("*.json"):
        data = json.loads(p.read_text(encoding='utf-8'))
        base = p.stem
        if base == "crop_pack":
            rows = [normalize_crop(c) for c in data.get("crops", [])]
            out = OUT_DIR / "crop_ingested.json"
            out.write_text(json.dumps(rows, indent=2, ensure_ascii=False))
            print("Wrote", out)
        else:
            # copy other packs as-is for now
            out = OUT_DIR / f"{base}_ingested.json"
            out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
            print("Wrote", out)

if __name__ == "__main__":
    main()
