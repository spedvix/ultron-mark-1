from __future__ import annotations

import hashlib


def hash_text(*parts: str) -> str:
    """Return SHA256 hash of provided text parts."""
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
    return digest.hexdigest()

