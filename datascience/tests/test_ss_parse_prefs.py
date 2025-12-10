from suitability_scoring.scoring.scoring import parse_prefs


def test_parse_prefs_none_returns_empty_list():
    """
    Checks a None preference returns and empty list.
    """
    assert parse_prefs(None) == []


def test_parse_prefs_list_passthrough():
    """
    Checks a list of preferences is passed through.
    """
    src = ["loam", "sandy loam"]
    out = parse_prefs(src)
    assert out is src  # function returns the same list object
    assert out == ["loam", "sandy loam"]


def test_parse_prefs_simple_string_split_and_strip():
    """
    Checks a single string is split into a list correctly.
    """
    assert parse_prefs("loam, sandy loam,clay") == ["loam", "sandy loam", "clay"]
    assert parse_prefs("  loam ,  sandy loam , clay  ") == [
        "loam",
        "sandy loam",
        "clay",
    ]


def test_parse_prefs_empty_string_results_in_single_empty_item():
    """
    Checks and empty string is returned as single empty item.
    """
    assert parse_prefs("") == [""]


def test_parse_prefs_trailing_comma_preserves_empty_item():
    """
    Checks trailing commas returns and empty item.
    """
    assert parse_prefs("clay,") == ["clay", ""]


def test_parse_prefs_only_spaces_become_empty_item_after_strip():
    """
    Checks only spaces become and empty item.
    """
    assert parse_prefs("   ") == [""]


def test_parse_prefs_non_string_non_list_non_none_returns_none():
    """
    Checks numbers are returned as None.
    """
    assert parse_prefs(123) is None
    assert parse_prefs(3.14) is None
