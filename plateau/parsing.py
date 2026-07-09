"""Parse pasted training logs into structured entries.

Expected shape, one session per line, comma- or tab-separated::

    date, exercise, weight, reps
    2026-01-05, squat, 225, 5

A leading header row (non-date first field on line 1) is tolerated and skipped.
Malformed rows are collected as errors rather than raising, so a paste with a
few typos still yields a usable partial result.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y")


@dataclass(frozen=True)
class Entry:
    date: date
    exercise: str
    weight: float
    reps: int


@dataclass(frozen=True)
class ParseResult:
    entries: list[Entry]
    errors: list[str]


def _parse_date(raw: str) -> date | None:
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def parse_log(text: str) -> ParseResult:
    entries: list[Entry] = []
    errors: list[str] = []

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        fields = [f.strip() for f in (line.split("\t") if "\t" in line else line.split(","))]
        if len(fields) != 4:
            errors.append(
                f"line {line_no}: expected 4 fields (date, exercise, weight, reps), got {len(fields)}"
            )
            continue

        raw_date, exercise, raw_weight, raw_reps = fields
        parsed_date = _parse_date(raw_date)
        if parsed_date is None:
            if line_no == 1:
                # Likely a header row (e.g. "date,exercise,weight,reps") — skip quietly.
                continue
            errors.append(f"line {line_no}: invalid date '{raw_date}'")
            continue

        if not exercise:
            errors.append(f"line {line_no}: missing exercise name")
            continue

        try:
            weight = float(raw_weight)
        except ValueError:
            errors.append(f"line {line_no}: invalid weight '{raw_weight}'")
            continue

        try:
            reps = int(float(raw_reps))
        except ValueError:
            errors.append(f"line {line_no}: invalid reps '{raw_reps}'")
            continue

        entries.append(Entry(date=parsed_date, exercise=exercise.lower(), weight=weight, reps=reps))

    return ParseResult(entries=entries, errors=errors)
