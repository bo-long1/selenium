import json
from pathlib import Path


def load_settings(path: str | Path = None) -> dict:
    p = Path(path) if path else Path(__file__).parents[1] / 'config' / 'test_setting.json'
    if not p.exists():
        return {}
    with p.open('r', encoding='utf-8') as f:
        return json.load(f) or {}
