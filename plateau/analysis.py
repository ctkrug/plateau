"""Statistical core: per-session strength estimates and trend regression."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from plateau.parsing import Entry

# Two-tailed 90% CI critical values for Student's t by degrees of freedom.
# Beyond 30 dof the normal approximation (1.645) is accurate to 3 decimal places.
_T90_TABLE = {
    1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015,
    6: 1.943, 7: 1.895, 8: 1.860, 9: 1.833, 10: 1.812,
    11: 1.796, 12: 1.782, 13: 1.771, 14: 1.761, 15: 1.753,
    16: 1.746, 17: 1.740, 18: 1.734, 19: 1.729, 20: 1.725,
    21: 1.721, 22: 1.717, 23: 1.714, 24: 1.711, 25: 1.708,
    26: 1.706, 27: 1.703, 28: 1.701, 29: 1.699, 30: 1.697,
}
_T90_NORMAL_APPROX = 1.645


def _t_critical_90(dof: int) -> float:
    if dof < 1:
        raise ValueError("degrees of freedom must be at least 1")
    return _T90_TABLE.get(dof, _T90_NORMAL_APPROX)


@dataclass(frozen=True)
class RegressionResult:
    slope: float
    intercept: float
    slope_ci_low: float
    slope_ci_high: float
    n: int


def fit_trend(x: Sequence[float], y: Sequence[float]) -> RegressionResult:
    """Fit y ~ x by ordinary least squares with a 90% confidence interval on the slope.

    Requires at least 3 points: 2 are needed to fit a line, a 3rd to estimate
    residual variance and therefore the slope's confidence interval.
    """
    n = len(x)
    if n != len(y):
        raise ValueError("x and y must be the same length")
    if n < 3:
        raise ValueError("need at least 3 points to fit a trend with a confidence interval")

    mean_x = sum(x) / n
    mean_y = sum(y) / n
    sxx = sum((xi - mean_x) ** 2 for xi in x)
    if sxx == 0:
        raise ValueError("x values must vary")

    sxy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x

    residual_ss = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    dof = n - 2
    mse = residual_ss / dof
    se_slope = math.sqrt(mse / sxx)
    margin = _t_critical_90(dof) * se_slope

    return RegressionResult(
        slope=slope,
        intercept=intercept,
        slope_ci_low=slope - margin,
        slope_ci_high=slope + margin,
        n=n,
    )


def estimate_one_rep_max(weight: float, reps: int) -> float:
    """Estimate a one-rep max from a single set via the Epley formula.

    1RM = weight * (1 + reps / 30). A single-rep set returns the weight
    unchanged.
    """
    if weight < 0:
        raise ValueError("weight must be non-negative")
    if reps < 1:
        raise ValueError("reps must be at least 1")
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)


class Trend(StrEnum):
    """A per-exercise classification of recent estimated-1RM movement."""

    STALLED = "stalled"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass(frozen=True)
class Classification:
    exercise: str
    trend: Trend
    weeks_stalled: int
    slope: float | None
    sessions_used: int


DEFAULT_WINDOW = 6
MIN_SESSIONS = 4


def classify_exercise(entries: Sequence[Entry], window: int = DEFAULT_WINDOW) -> Classification:
    """Classify one exercise's recent trend from its session history.

    Fits a rolling window of the trailing ``window`` sessions (or all of them,
    if fewer) and asks whether the slope's 90% confidence interval includes
    zero: if so the lift is statistically indistinguishable from flat over
    that window, i.e. plateaued. Fewer than MIN_SESSIONS sessions can't
    support a confidence interval at all, so those are reported separately
    rather than guessed at.
    """
    ordered = sorted(entries, key=lambda e: e.date)
    if len(ordered) < MIN_SESSIONS:
        exercise = ordered[0].exercise if ordered else ""
        return Classification(exercise, Trend.INSUFFICIENT_DATA, 0, None, len(ordered))

    exercise = ordered[0].exercise
    recent = ordered[-window:] if len(ordered) > window else ordered

    first_date = recent[0].date
    x = [(e.date - first_date).days for e in recent]
    y = [estimate_one_rep_max(e.weight, e.reps) for e in recent]
    fit = fit_trend(x, y)

    if fit.slope_ci_low <= 0 <= fit.slope_ci_high:
        span_days = (recent[-1].date - recent[0].date).days
        weeks_stalled = max(1, round(span_days / 7))
        return Classification(exercise, Trend.STALLED, weeks_stalled, fit.slope, len(recent))

    trend = Trend.TRENDING_UP if fit.slope > 0 else Trend.TRENDING_DOWN
    return Classification(exercise, trend, 0, fit.slope, len(recent))


def classify_log(entries: Sequence[Entry], window: int = DEFAULT_WINDOW) -> list[Classification]:
    """Classify every exercise present in a parsed log, independently."""
    by_exercise: dict[str, list[Entry]] = {}
    for entry in entries:
        by_exercise.setdefault(entry.exercise, []).append(entry)
    return [classify_exercise(sessions, window=window) for sessions in by_exercise.values()]
