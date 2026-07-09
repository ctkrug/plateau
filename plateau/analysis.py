"""Statistical core: per-session strength estimates and trend regression."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

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
