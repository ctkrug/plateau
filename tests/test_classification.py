from datetime import date, timedelta

from plateau.analysis import Trend, classify_exercise, classify_log
from plateau.parsing import Entry


def _sessions(exercise, weights, reps=5, start=date(2026, 1, 5), step_days=7):
    return [
        Entry(date=start + timedelta(days=i * step_days), exercise=exercise, weight=w, reps=reps)
        for i, w in enumerate(weights)
    ]


def test_flat_weights_classified_stalled_with_weeks_count():
    entries = _sessions("squat", [225, 224, 226, 225, 224, 225])
    result = classify_exercise(entries)
    assert result.trend == Trend.STALLED
    assert result.weeks_stalled == 5


def test_stalled_classification_exposes_slope_confidence_interval():
    entries = _sessions("squat", [225, 224, 226, 225, 224, 225])
    result = classify_exercise(entries)
    assert result.slope_ci_low <= 0 <= result.slope_ci_high


def test_clear_increase_classified_trending_up():
    entries = _sessions("bench", [155, 160, 165, 170, 175, 180])
    result = classify_exercise(entries)
    assert result.trend == Trend.TRENDING_UP
    assert result.slope_ci_low > 0


def test_clear_decrease_classified_trending_down():
    entries = _sessions("deadlift", [315, 305, 300, 290, 285, 275])
    result = classify_exercise(entries)
    assert result.trend == Trend.TRENDING_DOWN


def test_fewer_than_four_sessions_is_insufficient_data():
    entries = _sessions("squat", [225, 226, 224])
    result = classify_exercise(entries)
    assert result.trend == Trend.INSUFFICIENT_DATA
    assert result.slope is None
    assert result.slope_ci_low is None
    assert result.slope_ci_high is None


def test_exactly_four_sessions_attempts_a_classification():
    entries = _sessions("squat", [225, 224, 226, 225])
    result = classify_exercise(entries)
    assert result.trend != Trend.INSUFFICIENT_DATA


def test_empty_sessions_is_insufficient_data():
    result = classify_exercise([])
    assert result.trend == Trend.INSUFFICIENT_DATA
    assert result.exercise == ""


def test_window_only_considers_trailing_sessions():
    # An early plateau followed by six clearly increasing sessions should
    # read as trending up, since only the trailing window is fit.
    plateau_then_rise = _sessions("squat", [225, 224, 225]) + _sessions(
        "squat", [230, 240, 250, 260, 270, 280], start=date(2026, 2, 23)
    )
    result = classify_exercise(plateau_then_rise, window=6)
    assert result.trend == Trend.TRENDING_UP
    assert result.sessions_used == 6


def test_classify_log_handles_multiple_exercises_independently():
    entries = (
        _sessions("squat", [225, 224, 226, 225, 224, 225])
        + _sessions("bench", [155, 160, 165, 170, 175, 180])
        + _sessions("deadlift", [315, 305, 300, 290, 285, 275])
    )
    results = {r.exercise: r.trend for r in classify_log(entries)}
    assert results == {
        "squat": Trend.STALLED,
        "bench": Trend.TRENDING_UP,
        "deadlift": Trend.TRENDING_DOWN,
    }


def test_classify_log_flags_sparse_exercise_as_insufficient():
    entries = _sessions("squat", [225, 224, 226, 225, 224, 225]) + _sessions(
        "overhead press", [95, 96, 94]
    )
    results = {r.exercise: r.trend for r in classify_log(entries)}
    assert results["overhead press"] == Trend.INSUFFICIENT_DATA


def test_classify_log_empty_input_returns_empty_list():
    assert classify_log([]) == []


def test_gap_containing_log_classifies_without_crashing():
    # Two sessions a week apart, then an 8-week gap, then two more sessions.
    entries = [
        Entry(date=date(2026, 1, 5), exercise="squat", weight=225, reps=5),
        Entry(date=date(2026, 1, 12), exercise="squat", weight=226, reps=5),
        Entry(date=date(2026, 3, 9), exercise="squat", weight=224, reps=5),
        Entry(date=date(2026, 3, 16), exercise="squat", weight=225, reps=5),
    ]
    result = classify_exercise(entries)
    assert result.trend != Trend.INSUFFICIENT_DATA
    assert result.sessions_used == 4


def test_identical_weights_are_stalled_at_the_exact_zero_boundary():
    # Zero variance in y collapses the slope's confidence interval to exactly
    # [0, 0], so the "does the interval include zero" check must use an
    # inclusive comparison at both ends, not a strict one.
    entries = _sessions("squat", [225, 225, 225, 225, 225, 225])
    result = classify_exercise(entries)
    assert result.slope_ci_low == 0
    assert result.slope_ci_high == 0
    assert result.trend == Trend.STALLED


def test_weeks_stalled_reflects_calendar_span_not_session_count():
    # Same number of sessions (4), but spread over very different calendar spans.
    tight = _sessions("squat", [225, 224, 226, 225], step_days=7)
    sparse = _sessions("squat", [225, 224, 226, 225], step_days=21)

    tight_result = classify_exercise(tight)
    sparse_result = classify_exercise(sparse)

    assert tight_result.trend == Trend.STALLED
    assert sparse_result.trend == Trend.STALLED
    assert sparse_result.weeks_stalled > tight_result.weeks_stalled
