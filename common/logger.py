"""
Centralized logging utilities: debug-mode detection and shared logger configuration.
"""
from __future__ import annotations

import logging
import atexit
from pathlib import Path
from datetime import datetime
from common.utils import load_settings
import threading
from logging.handlers import QueueHandler, QueueListener
import queue

LOG_DIR = Path("log_report")
_logger_init_lock = threading.Lock()
_log_queue: queue.Queue | None = None
_queue_listener: QueueListener | None = None
_file_handler: logging.Handler | None = None
_console_handler: logging.Handler | None = None


def is_debug_mode() -> bool:
    """Check if debug mode is enabled in settings."""
    try:
        settings = load_settings()
        raw = settings.get("browser_options", {}).get("debug_mode", False)
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, str):
            return raw.strip().lower() in ("1", "true", "yes", "on")
        if isinstance(raw, int):
            return raw != 0
        return bool(raw)
    except Exception:
        logging.getLogger(__name__).warning("Could not read debug mode from settings; defaulting to False")
        return False


def create_logger(name='bdd_logger', log_file=None):
    """Create and configure logger with file and console handlers."""
    logger = logging.getLogger(name)
    
    with _logger_init_lock:
        if logger.handlers:
            return logger

        debug = is_debug_mode()
        level = logging.DEBUG if debug else logging.INFO

        base_fmt = '%(asctime)s - %(levelname)s - [%(threadName)s:%(process)d] - %(message)s' if debug \
            else '%(asctime)s - %(message)s'
        formatter = logging.Formatter(base_fmt, datefmt='%d-%m')

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = LOG_DIR / f"{timestamp}.log"
        else:
            log_file = Path(log_file)

        global _log_queue, _queue_listener, _file_handler, _console_handler
        
        # Initialize the queue only once
        if _log_queue is None:
            _log_queue = queue.Queue(-1)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        _file_handler = file_handler

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        _console_handler = console_handler

        queue_handler = QueueHandler(_log_queue)
        queue_handler.setLevel(level)

        logger.addHandler(queue_handler)
        logger.setLevel(level)
        logger.propagate = False

        # Initialize the listener once only and register cleanup
        if _queue_listener is None:
            _queue_listener = QueueListener(
                _log_queue, file_handler, console_handler, respect_handler_level=True
            )
            _queue_listener.start()
            atexit.register(_shutdown_listener)

    return logger


def _shutdown_listener():
    """Stop QueueListener safely on program exit."""
    global _queue_listener
    if _queue_listener:
        _queue_listener.stop()
        _queue_listener = None


def reconfigure_logger_from_settings(name='bdd_logger'):
    """Apply current settings (debug_mode) to logger and handlers."""
    with _logger_init_lock:  # thread-safe
        level = logging.DEBUG if is_debug_mode() else logging.INFO
        lg = logging.getLogger(name)
        lg.setLevel(level)
        for h in lg.handlers:
            h.setLevel(level)
        if _file_handler:
            _file_handler.setLevel(level)
        if _console_handler:
            _console_handler.setLevel(level)


# Create shared logger instance
logger = create_logger()
