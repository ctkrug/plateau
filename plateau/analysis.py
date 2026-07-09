"""Statistical core: per-session strength estimates.

The rolling-regression plateau classifier (the project's wow moment) builds on
top of this module and lands in a later pass — see docs/BACKLOG.md epic 1.
"""

from __future__ import annotations


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
