from pathlib import Path


def test_no_owner_id_in_asset_modules():
    repository = Path(__file__).resolve().parents[3]
    matches = [
        str(path.relative_to(repository))
        for path in (repository / "app/assets").rglob("*.py")
        if "owner_id" in path.read_text(encoding="utf-8")
    ]
    assert matches == []
