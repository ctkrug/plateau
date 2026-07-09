from datetime import date

from plateau.parsing import Entry, parse_log


def test_parses_comma_separated_log():
    result = parse_log("2026-01-05, squat, 225, 5\n2026-01-12, squat, 230, 5")

    assert result.errors == []
    assert result.entries == [
        Entry(date=date(2026, 1, 5), exercise="squat", weight=225.0, reps=5),
        Entry(date=date(2026, 1, 12), exercise="squat", weight=230.0, reps=5),
    ]


def test_parses_tab_separated_log():
    result = parse_log("2026-01-05\tsquat\t225\t5")

    assert result.errors == []
    assert result.entries == [Entry(date=date(2026, 1, 5), exercise="squat", weight=225.0, reps=5)]


def test_skips_leading_header_row():
    result = parse_log("date,exercise,weight,reps\n2026-01-05,squat,225,5")

    assert result.errors == []
    assert len(result.entries) == 1


def test_blank_lines_are_ignored():
    result = parse_log("\n2026-01-05,squat,225,5\n\n")

    assert len(result.entries) == 1


def test_malformed_row_is_reported_not_raised():
    result = parse_log("2026-01-05,squat,225,5\nnot-a-date,squat,225,5")

    assert len(result.entries) == 1
    assert len(result.errors) == 1
    assert "line 2" in result.errors[0]


def test_wrong_field_count_is_reported():
    result = parse_log("2026-01-05,squat,225")

    assert result.entries == []
    assert "line 1" in result.errors[0]
