from __future__ import annotations

import logging
import re
from typing import Optional

EMAIL_RE = re.compile(r"(?P<user>[A-Za-z0-9._%+-]+)@(?P<domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,})")


class _PiiFilter(logging.Filter):
    """Filter that masks emails when enabled."""

    def __init__(self, mask_pii: bool):
        super().__init__()
        self.mask_pii = mask_pii

    def filter(self, record: logging.LogRecord) -> bool:
        if self.mask_pii and isinstance(record.msg, str):
            record.msg = mask_email(record.msg)
        return True


def mask_email(text: str) -> str:
    """Mask email addresses with a fixed redaction token."""

    def _replace(match: re.Match[str]) -> str:
        return "***@***"

    return EMAIL_RE.sub(_replace, text)


def configure_logging(level: str = "INFO", mask_pii: bool = True) -> None:
    """Configure root logging with structured formatter and optional masking."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger().addFilter(_PiiFilter(mask_pii))


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Shortcut for module loggers."""
    return logging.getLogger(name if name else "ultron")

