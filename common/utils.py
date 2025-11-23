"""Common utility functions for configuration and helpers."""
import json
import re
from pathlib import Path
import threading
import uuid
_settings_cache = None
_settings_lock = threading.Lock()


def load_settings(path: str | Path = None) -> dict:
    """Load test settings from JSON config file."""
    global _settings_cache
    if _settings_cache is None:
        with _settings_lock:
            if _settings_cache is None:
                p = Path(path) if path else Path(__file__).parents[1] / 'config' / 'test_setting.json'
                if not p.exists():
                    return {}
                with p.open('r', encoding='utf-8') as f:
                    _settings_cache = json.load(f) or {}
    return _settings_cache
