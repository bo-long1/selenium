"""Common utility functions for configuration and helpers."""
import json
import re
from pathlib import Path
import threading
import time
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

# Example utility functions that can be used across the test framework
def generate_uuid() -> str:
    """Generate a unique identifier string."""
    return str(uuid.uuid4())

def generate_random_string(length: int = 8) -> str:
    """Generate a random alphanumeric string of specified length."""
    return uuid.uuid4().hex[:length]

def generate_expected_value_from_template(template: str, **kwargs) -> str:
    """Generate expected value by replacing placeholders in the template with provided keyword arguments."""
    for key, value in kwargs.items():
        placeholder = f"{{{key}}}"
        template = template.replace(placeholder, str(value))
    return template

def convert_hex_color_to_rgb(hex_color: str) -> tuple:
    """Convert hex color code to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def convert_rgb_color_to_hex(rgb_color: tuple) -> str:
    """Convert RGB tuple to hex color code."""
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

def normalize_string(s: str) -> str:
    """Normalize string by stripping whitespace and converting to lowercase."""
    return re.sub(r'\s+', ' ', s.strip().lower())

def time_string_to_seconds(time_str: str) -> int:
    """Convert time string (e.g. '1h 30m') to total seconds."""
    time_units = {'h': 3600, 'm': 60, 's': 1}
    total_seconds = 0
    for match in re.finditer(r'(\d+)([hms])', time_str):
        value, unit = match.groups()
        total_seconds += int(value) * time_units[unit]
    return total_seconds

def sort_descending(lst: list) -> list:
    """Return a new list sorted in descending order."""
    return sorted(lst, reverse=True)

def sort_ascending(lst: list) -> list:
    """Return a new list sorted in ascending order."""
    return sorted(lst)

def sort_case_insensitive_upper_first(lst: list) -> list:
    """Return a new list sorted case-insensitively with uppercase grouped before lowercase."""
    return sorted(
        lst,
        key=lambda s: (
            s.lower(),
            tuple(0 if c.isupper() else 1 for c in s)
        )
    )

def remove_duplicates(lst: list) -> list:
    """Return a new list with duplicates removed while preserving order."""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def attach_screenshot_to_report(driver, name: str = "screenshot"):
    """Capture screenshot and attach to test report."""
    try:
        screenshot = driver.get_screenshot_as_png()
        # Here you would integrate with your test reporting tool to attach the screenshot
        # For example, if using Allure:
        # import allure
        # allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")

def get_downloaded_file_path(download_dir: str, filename_pattern: str) -> str:
    """Get the path of a downloaded file matching the given pattern."""
    download_path = Path(download_dir)
    for file in download_path.iterdir():
        if re.match(filename_pattern, file.name):
            return str(file.resolve())
    return None

def wait_for_file_downloaded(download_dir: str, filename_pattern: str, timeout: int = 30) -> str:
    """Wait for a file matching the pattern to be downloaded within the timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        file_path = get_downloaded_file_path(download_dir, filename_pattern)
        if file_path:
            return file_path
        time.sleep(1)
    raise TimeoutError(f"File matching pattern '{filename_pattern}' not found in '{download_dir}' after {timeout} seconds")

def wait_for_file_deleted(download_dir: str, filename_pattern: str, timeout: int = 30) -> bool:
    """Wait for a file matching the pattern to be deleted within the timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        file_path = get_downloaded_file_path(download_dir, filename_pattern)
        if not file_path:
            return True
        time.sleep(1)
    raise TimeoutError(f"File matching pattern '{filename_pattern}' still exists in '{download_dir}' after {timeout} seconds")

def wait_for_file_exists(file_path: str, timeout: int = 30) -> bool:
    """Wait for a specific file to exist within the timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if Path(file_path).exists():
            return True
        time.sleep(1)
    raise TimeoutError(f"File '{file_path}' not found after {timeout} seconds")

def quote_string(s: str) -> str:
    """Return the input string wrapped in double quotes."""
    return f'"{s}"'

def unquote_string(s: str) -> str:
    """Return the input string with surrounding quotes removed."""
    return s.strip('"')
