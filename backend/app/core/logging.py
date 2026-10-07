"""
Structured logging configuration for the AI Fitness Coach backend.
"""

import sys
import logging
import json
from datetime import datetime, timezone
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """JSON-formatted log output for structured logging."""

    SENSITIVE_KEYS = {"password", "token", "access_token", "refresh_token",
                      "service_role_key", "secret", "authorization"}

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields (request_id, analysis_id, user_id, etc.)
        for key in ("request_id", "analysis_id", "user_id", "stage",
                     "duration", "status", "error"):
            val = getattr(record, key, None)
            if val is not None:
                log_entry[key] = val

        # Exception info
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, default=str)


class HumanFormatter(logging.Formatter):
    """Human-readable log format for development."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.now().strftime("%H:%M:%S")
        extras = ""
        for key in ("request_id", "analysis_id", "stage"):
            val = getattr(record, key, None)
            if val:
                extras += f" [{key}={val}]"
        return f"{ts} | {record.levelname:8s} | {record.name}:{record.funcName}:{record.lineno} |{extras} {record.getMessage()}"


def setup_logging(level: str = "INFO", log_format: str = "json") -> None:
    """Configure application logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    if log_format == "json":
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(HumanFormatter())

    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    for noisy in ("httpcore", "httpx", "uvicorn.access", "watchfiles"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(f"fitness_coach.{name}")
