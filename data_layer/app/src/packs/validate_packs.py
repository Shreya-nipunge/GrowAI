# src/packs/validate_packs.py
"""
Validate all offline JSON packs against their schemas.

Usage:
    python src/packs/validate_packs.py
"""

import os, glob, sys, json
from jsonschema import Draft7Validator, ValidationError, SchemaError
from .utils import load_json_with_context

# Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PACKS_DIR = os.path.join(BASE_DIR, "app", "data", "offline_packs")
SCHEMA_DIR = os.path.join(os.path.dirname(__file__))

def find_schema(pack_file: str):
    """
    Finds a matching schema for a given pack file.
    Example: crop_pack.json -> crop_pack.schema.json
    """
    base = os.path.splitext(os.path.basename(pack_file))[0]
    candidate = os.path.join(SCHEMA_DIR, f"{base}.schema.json")
    if os.path.exists(candidate):
        return candidate
    return None

def validate_pack(pack_file: str):
    """
    Validates one JSON pack against its schema.
    Returns: (ok: bool, errors: list[str])
    """
    errors = []
    try:
        data = load_json_with_context(pack_file)
    except ValueError as e:
        return False, [str(e)]

    schema_path = find_schema(pack_file)
    if not schema_path:
        return False, [f"No schema found for {pack_file}"]

    try:
        schema = load_json_with_context(schema_path)
    except ValueError as e:
        return False, [f"Schema {schema_path} is invalid JSON: {e}"]

    try:
        validator = Draft7Validator(schema)
        for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
            loc = ".".join(map(str, err.absolute_path)) or "(root)"
            errors.append(f"{pack_file} :: {loc} :: {err.message}")
    except SchemaError as e:
        return False, [f"Schema {schema_path} is not a valid JSON schema: {e}"]

    return (len(errors) == 0), errors

def main():
    pack_files = glob.glob(os.path.join(PACKS_DIR, "*.json"))
    if not pack_files:
        print("⚠️  No pack files found in", PACKS_DIR)
        sys.exit(1)

    failed = []
    for pack in pack_files:
        ok, errors = validate_pack(pack)
        if ok:
            print(f"✔ {os.path.basename(pack)} passed")
        else:
            print(f"✖ {os.path.basename(pack)} failed:")
            for e in errors:
                print("   -", e)
            failed.extend(errors)

    if failed:
        print(f"\n❌ Validation failed for {len(failed)} issues.")
        sys.exit(1)

    print("\n✅ All packs validated successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
