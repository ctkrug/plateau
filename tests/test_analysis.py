import pytest

from plateau.analysis import estimate_one_rep_max


def test_single_rep_returns_weight_unchanged():
    assert estimate_one_rep_max(225, 1) == 225


def test_matches_known_epley_reference_value():
    # 225 lbs x 5 reps -> 225 * (1 + 5/30) = 262.5
    assert estimate_one_rep_max(225, 5) == pytest.approx(262.5)


def test_rejects_negative_weight():
    with pytest.raises(ValueError):
        estimate_one_rep_max(-10, 5)


def test_rejects_zero_reps():
    with pytest.raises(ValueError):
        estimate_one_rep_max(100, 0)
