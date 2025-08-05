# logging_setup.py
"""
Cat Prey Analyzer - Logging Setup Utility

Purpose:
    - Enables consistent, centralized logging across all processes.
    - Designed to work with external log rotation tools like `logrotate`.

Features:
    - Shared log file with file-level locking (via `fcntl`, Unix-only).
    - Unified format and log levels across all modules and processes.
    - Cleans up previous handlers to avoid duplicate log entries.
    - Compatible with external rotation (no internal log rotation).
    - Safe for use in multiprocess applications.

Usage:
    - Call `setup_logging()` at process startup (e.g., in cascade.py or camera_class.py).
    - Configure rotation with `/etc/logrotate.d/your_log_config` externally.

Author:
    github.com/netphantm
"""

import logging
import fcntl
import os
from datetime import datetime


class LockedFileHandler(logging.FileHandler):
    """FileHandler with cross-process locking via fcntl (UNIX-only)."""
    def emit(self, record):
        try:
            msg = self.format(record) + '\n'
            with open(self.baseFilename, 'a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(msg)
                f.flush()
                os.fsync(f.fileno())
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception:
            self.handleError(record)


def setup_logging(log_filename="log/CatPreyAnalyzer.log", log_level_str="INFO"):
    """
    Setup cross-process safe logging using LockedFileHandler.

    Args:
        log_filename (str): Full path to the log file.
        log_level_str (str): Logging level ("DEBUG", "INFO", etc).
    """
    logger = logging.getLogger()
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])

    log_level = getattr(logging, log_level_str.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {log_level_str}")

    logger.setLevel(log_level)

    handler = LockedFileHandler(log_filename)
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s][PID %(process)d]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

