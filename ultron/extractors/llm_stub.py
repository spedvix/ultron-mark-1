from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dateutil import parser as date_parser
from dateutil.tz import gettz

from ..settings import settings
from .rules import RuleHits


@dataclass
class NormalizedArtifact:
    title: str
    course_code: Optional[str]
    kind: str
    due_iso: Optional[str]
    location: Optional[str]
    link: Optional[str]
    confidence: float


def normalize_artifact(title: str, url: str, text: str, rule_hits: RuleHits) -> NormalizedArtifact:
    """Deterministic normalizer that mimics an LLM output."""
    kind = rule_hits.kind_guess or "announcement"
    course_code = rule_hits.course_codes[0] if rule_hits.course_codes else None
    due_iso = _determine_due_iso(rule_hits)
    location = rule_hits.locations[0] if rule_hits.locations else None

    confidence = 0.3
    if due_iso and kind and course_code:
        confidence = 0.9
    elif due_iso and kind:
        confidence = 0.6

    link = url if url else None
    return NormalizedArtifact(
        title=title.strip() or text[:80],
        course_code=course_code,
        kind=kind,
        due_iso=due_iso,
        location=location,
        link=link,
        confidence=confidence,
    )


def _determine_due_iso(rule_hits: RuleHits) -> Optional[str]:
    if not rule_hits.dates:
        return None
    date_text = rule_hits.dates[0]
    time_text = rule_hits.times[0] if rule_hits.times else None
    try:
        if time_text:
            combined = f"{date_text} {time_text}"
        else:
            combined = date_text
        tz = gettz(settings.timezone)
        dt = date_parser.parse(combined, dayfirst=False, yearfirst=False)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        return dt.astimezone(tz).isoformat()
    except (ValueError, OverflowError):
        return None

