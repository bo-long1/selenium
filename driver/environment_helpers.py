"""
Core helper functions for WebDriver management, logging, and failure diagnostics.
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

from driver import driver_factory
from common.logger import is_debug_mode, logger
from pages.heroku import HerokuPage

try:
    import allure  # type: ignore
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================
ALLURE_DIR = Path("allure_results")
LOG_DIR = Path("log_report")


# ============================================================================
# DIRECTORY SETUP
# ============================================================================
def setup_directories():
    """Create directories for reports."""
    for directory in [ALLURE_DIR, LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    logger.debug(f"Directories ready: {ALLURE_DIR}, {LOG_DIR}")


def clean_allure_results():
    """Remove old Allure results if they exist."""
    if ALLURE_DIR.exists():
        logger.debug("Cleaning old Allure results...")
        try:
            shutil.rmtree(ALLURE_DIR)
            logger.debug("Cleaned")
        except Exception as e:
            logger.warning(f"Could not clean Allure results: {e}")


# ============================================================================
# DRIVER MANAGEMENT
# ============================================================================
def create_driver(context: Any, scenario_name: str):
    """Create WebDriver and initialize page objects."""
    context.driver = driver_factory.create_driver_from_settings()
    HerokuPage.set_driver(context.driver)



def close_driver(context: Any, scenario_name: str):
    """Safely close WebDriver and cleanup."""
    driver = getattr(context, "driver", None)
    if not driver:
        logger.debug(f"No driver to close for scenario: {scenario_name}")
        return

    try:
        driver.delete_all_cookies()
        driver.quit()
    except Exception as e:
        logger.debug(f"Could not delete cookies and quit driver: {e}")
    finally:
        context.driver = None

# ============================================================================
# FAILURE DIAGNOSTICS
# ============================================================================
def generate_filename(basename: str) -> str:
    """Generate clean filename from name + timestamp (no special chars)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in basename).strip()
    safe_name = safe_name or "step"
    return f"{safe_name}_{timestamp}"


def capture_screenshot(driver, step_name: str) -> Optional[Path]:
    """Capture screenshot to file and optionally attach to Allure."""
    try:
        screenshot_bytes = driver.get_screenshot_as_png()
        filename = generate_filename(step_name)
        screenshot_path = LOG_DIR / f"{filename}.png"
        screenshot_path.write_bytes(screenshot_bytes)

        logger.info(f"Screenshot saved: {screenshot_path}")

        if ALLURE_AVAILABLE:
            allure.attach(
                screenshot_bytes,
                name=f"Screenshot - {step_name}",
                attachment_type=allure.attachment_type.PNG,
            )

        return screenshot_path

    except Exception as e:
        logger.warning(f"Could not capture screenshot: {e}")
        return None


def capture_console_logs(driver, step_name: str) -> Optional[Path]:
    """Capture browser console logs as JSON and optionally attach to Allure."""
    try:
        logs = None

        # Try browser logs, fallback to performance logs
        for log_type in ("browser", "performance"):
            try:
                logs = driver.get_log(log_type)
                if logs:
                    break
            except Exception:
                continue

        if not logs:
            return None

        filename = generate_filename(step_name)
        log_file = LOG_DIR / f"{filename}_console.json"
        log_file.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")

        logger.info(f"Console logs saved: {log_file}")

        if ALLURE_AVAILABLE:
            allure.attach(
                json.dumps(logs, ensure_ascii=False, indent=2),
                name=f"Console logs - {step_name}",
                attachment_type=allure.attachment_type.TEXT,
            )

        return log_file

    except Exception as e:
        logger.warning(f"Could not capture console logs: {e}")
        return None


def handle_step_failure(context: Any, step: Any):
    """Handle step failure: capture screenshot + console logs."""
    driver = getattr(context, "driver", None)
    if not driver:
        return

    logger.error(f"Step FAILED: {step.name}")

    if is_debug_mode():
        logger.debug(f"Location: {step.location}")
        logger.debug(f"Status: {step.status}")
        duration = getattr(step, "duration", None)
        logger.debug(f"Duration: {duration:.2f}s" if duration else "Duration: N/A")
        if hasattr(step, "error_message"):
            logger.debug(f"Error message: {step.error_message}")
        if hasattr(step, "exception"):
            logger.debug(f"Exception: {type(step.exception).__name__}: {step.exception}")

    capture_screenshot(driver, step.name)
    capture_console_logs(driver, step.name)


# ============================================================================
# STATUS HELPERS
# ============================================================================
def _status_to_str(status_obj: Any) -> str:
    """Convert Behave status object to a lowercase string safely."""
    try:
        name = getattr(status_obj, "name", None)
        return str(name or status_obj).strip().lower()
    except Exception:
        return ""


def is_step_failed(step) -> bool:
    """Return True if step indicates failure."""
    return _status_to_str(getattr(step, "status", None)) in ("failed", "error")


# ============================================================================
# STEP LOGGERS
# ============================================================================
def log_step_start(step: Any):
    """Log Given/When/Then step start (DEBUG in debug_mode only)."""
    if getattr(step, "_logged", False):
        return
    step._logged = True
    logger.info(f"{step.keyword.strip()} {step.name}".strip())
    if is_debug_mode():
        logger.debug(f"{step.keyword.strip()} {step.name}".strip())
        logger.debug(f"Location: {step.location}")


def log_step_end(step: Any):
    """Log step completion (DEBUG)."""
    status_str = _status_to_str(getattr(step, "status", None))
    duration = getattr(step, "duration", None)
    logger.debug(
        f"Step {status_str.upper()}: {step.name} ({duration:.3f}s)" if duration else f"Step {status_str.upper()}: {step.name}"
    )


def log_scenario_details(scenario: Any):
    """Log scenario details in debug mode."""
    if not is_debug_mode():
        return
    logger.debug("=" * 80)
    logger.debug(f"Scenario: {scenario.name}")
    logger.debug(f"Location: {scenario.location}")
    logger.debug(f"Tags: {', '.join(scenario.tags) if scenario.tags else 'None'}")
    logger.debug("=" * 80)
