import pandas as pd
import numpy as np
import pytest
from suitability_scoring.scoring.scoring import subset_species_by_ids


@pytest.fixture
def species_df_int():
    """
    Create species dataframe with int ids.
    """
    return pd.DataFrame(
        {
            "species_id": [101, 102, 103, 104, np.nan],
            "name": ["A", "B", "C", "D", "Missing"],
            "elevation_m": [100, 1200, 80, 150, 0],
        }
    )


@pytest.fixture
def species_df_str():
    """
    Create species dataframe with string ids.
    """
    return pd.DataFrame(
        {
            "species_code": ["SP-001", "SP-002", "SP-003", "SP-004", None],
            "name": ["A", "B", "C", "D", "Missing"],
            "elevation_m": [100, 1200, 80, 150, 0],
        }
    )


def test_empty_valid_ids_returns_empty_dataframe(species_df_int):
    """
    Checks that an empty list of ids returns and empty dataframe.
    """
    out = subset_species_by_ids(species_df_int, "species_id", valid_ids=[])
    # Should keep the schema but have no rows
    assert out.empty
    assert list(out.columns) == list(species_df_int.columns)
    assert out.dtypes.equals(species_df_int.dtypes)


def test_filter_membership_basic_int_ids(species_df_int):
    """
    Checks that a valid list of numeric ids returns the correct filtered dataframe.
    """
    valid = [101, 103]
    out = subset_species_by_ids(species_df_int, "species_id", valid_ids=valid)
    assert sorted(out["species_id"].dropna().tolist()) == [101, 103]
    # Check row count
    assert len(out) == 2
    # Names aligned
    assert set(out["name"]) == {"A", "C"}


def test_filter_membership_basic_str_ids(species_df_str):
    """
    Checks that a valid list of string ids returns the correct filtered dataframe.
    """
    valid = ["SP-001", "SP-003"]
    out = subset_species_by_ids(species_df_str, "species_code", valid_ids=valid)
    assert set(out["species_code"]) == {"SP-001", "SP-003"}
    assert set(out["name"]) == {"A", "C"}


def test_duplicates_in_valid_ids_do_not_duplicate_rows(species_df_int):
    """
    Checks that a list of ids containing duplicates does not duplicate the rows returned.
    """
    valid = [101, 101, 104, 104]
    out = subset_species_by_ids(species_df_int, "species_id", valid_ids=valid)
    # Only unique matches present once
    assert sorted(out["species_id"].dropna().tolist()) == [101, 104]
    assert len(out) == 2


def test_nonexistent_id_column_raises_keyerror(species_df_int):
    """
    Checks that a non-existent column name raises a KeyError.
    """
    with pytest.raises(KeyError):
        subset_species_by_ids(species_df_int, "unknown_id_col", valid_ids=[101])


def test_mixed_types_in_valid_ids_do_not_match_other_types(species_df_int):
    """
    Check string ides don't match int ids.
    """
    # '101' (str) should not match 101 (int) in the DataFrame
    out = subset_species_by_ids(species_df_int, "species_id", valid_ids=["101", "104"])
    # Expect no matches due to type mismatch
    assert out.empty


def test_preserves_dataframe_schema_and_order(species_df_int):
    """
    Check that the dataframe schema is retained.
    """
    valid = [104]
    out = subset_species_by_ids(species_df_int, "species_id", valid_ids=valid)
    # Same columns, same order
    assert list(out.columns) == list(species_df_int.columns)
    # dtypes unchanged
    assert out.dtypes.equals(species_df_int.dtypes)
