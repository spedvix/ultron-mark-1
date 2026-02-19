from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

RE_DATE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b",
    re.IGNORECASE,
)
RE_TIME = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b")
RE_COURSE = re.compile(r"\b[A-Za-z]{2,4}\s?-?\s?\d{3}\b")
KEYWORDS_ASSIGN = re.compile(r"\b(assign(?:ment)?|homework|hw)\b", re.IGNORECASE)
KEYWORDS_EXAM = re.compile(r"\b(midterm|final|quiz|exam|make-?up)\b", re.IGNORECASE)
KEYWORDS_CANCELLED = re.compile(r"\b(cancelled|canceled|closure)\b", re.IGNORECASE)
RE_LOCATION = re.compile(r"\b(Room|Hall|Building|Lab)\s+[A-Za-z0-9-]+\b", re.IGNORECASE)


@dataclass
class RuleHits:
    dates: List[str]
    times: List[str]
    course_codes: List[str]
    kind_guess: Optional[str]
    locations: List[str]


class RuleExtractor:
    """Simple regex-driven extraction of structured cues."""

    def extract(self, title: str, text: str) -> RuleHits:
        content = f"{title}\n{text}"
        dates = RE_DATE.findall(content)
        times = RE_TIME.findall(content)
        course_codes = [self._normalize_course_code(code) for code in RE_COURSE.findall(content)]
        locations = [match.group(0) for match in RE_LOCATION.finditer(content)]
        kind_guess = self._guess_kind(content)
        return RuleHits(
            dates=list(dict.fromkeys(dates)),
            times=list(dict.fromkeys(times)),
            course_codes=list(dict.fromkeys(course_codes)),
            kind_guess=kind_guess,
            locations=list(dict.fromkeys(locations)),
        )

    @staticmethod
    def _guess_kind(text: str) -> Optional[str]:
        if KEYWORDS_ASSIGN.search(text):
            return "assignment"
        if KEYWORDS_EXAM.search(text):
            return "exam"
        if KEYWORDS_CANCELLED.search(text):
            return "announcement"
        return None

    @staticmethod
    def _normalize_course_code(code: str) -> str:
        return code.replace(" ", "").replace("-", "").upper()


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()
