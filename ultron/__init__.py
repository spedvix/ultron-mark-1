"""
Ultron service package.

Provides application factory, settings, and supporting utilities for the
academic assistant backend.
"""

from importlib import metadata


def get_version() -> str:
    """Return the installed package version, or dev marker when unavailable."""
    try:
        return metadata.version("ultron")
    except metadata.PackageNotFoundError:
        return "0.0.0-dev"


__all__ = ["get_version"]
