import pytest

from plateau.analysis import fit_trend


def test_perfectly_flat_data_has_zero_slope():
    x = [0, 1, 2, 3, 4, 5]
    y = [225, 225, 225, 225, 225, 225]
    result = fit_trend(x, y)
    assert result.slope == pytest.approx(0.0, abs=1e-9)


def test_monotonically_increasing_data_has_positive_slope():
    x = [0, 1, 2, 3, 4, 5]
    y = [200, 205, 210, 215, 220, 225]
    result = fit_trend(x, y)
    assert result.slope > 0
    assert result.slope == pytest.approx(5.0)


def test_noisy_flat_data_confidence_interval_includes_zero():
    x = [0, 1, 2, 3, 4, 5]
    y = [225, 218, 231, 220, 229, 224]
    result = fit_trend(x, y)
    assert result.slope_ci_low <= 0 <= result.slope_ci_high


def test_clear_trend_confidence_interval_excludes_zero():
    x = [0, 1, 2, 3, 4, 5]
    y = [200, 206, 211, 217, 221, 227]
    result = fit_trend(x, y)
    assert result.slope_ci_low > 0


def test_requires_at_least_three_points():
    with pytest.raises(ValueError):
        fit_trend([0, 1], [225, 230])


def test_requires_matching_lengths():
    with pytest.raises(ValueError):
        fit_trend([0, 1, 2], [225, 230])


def test_requires_x_variance():
    with pytest.raises(ValueError):
        fit_trend([1, 1, 1], [225, 230, 220])
