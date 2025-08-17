from src.packs import validate_packs
import glob, os

def test_all_packs():
    """Ensure all offline packs validate against their schemas."""
    packs = glob.glob(os.path.join(validate_packs.PACKS_DIR, "*.json"))
    assert packs, "No offline packs found!"
    for p in packs:
        ok, errors = validate_packs.validate_pack(p)
        assert ok, f"{p} failed validation: {errors}"
