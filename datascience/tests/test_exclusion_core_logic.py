from exclusion_rules.exclusion_core_logic import run_exclusion_rules


def test_species_specific_numeric_exclusion():
    """
    Tests all numeric comparison operators.
    Ensures that an exclusion only triggers when the 'fail condition' is met.
    """
    # All species in the system
    all_species = [{"id": 101, "name": "Species A"}, {"id": 102, "name": "Species B"}]

    farm_numeric = {"id": 1, "rainfall_mm": 500, "elevation_m": 1000}

    numeric_rules = {
        101: [
            {"feature": "rainfall_mm", "operator": ">", "value": 400, "reason": "too high"},  # 500 > 400 (True) -> Exclude
            {"feature": "rainfall_mm", "operator": "<", "value": 600, "reason": "too low"},  # 500 < 600 (True) -> Exclude
            {"feature": "elevation_m", "operator": ">=", "value": 1000, "reason": "limit reached"},  # 1000 >= 1000 -> Exclude
            {"feature": "elevation_m", "operator": "<=", "value": 1000, "reason": "limit reached"},  # 1000 <= 1000 -> Exclude
        ]
    }

    out_numeric = run_exclusion_rules(farm_numeric, all_species, numeric_rules, dep_lookup={})
    assert 101 not in out_numeric["candidate_ids"]

    reasons = next(e["reasons"] for e in out_numeric["excluded_species"] if e["id"] == 101)
    assert len(reasons) == 4
    assert any("excluded: too high" in r for r in reasons)

    # Test "Pass" conditions (Rules exist but farm values are safe)
    farm_safe = {"id": 1, "rainfall_mm": 500}
    safe_rules = {102: [{"feature": "rainfall_mm", "operator": ">", "value": 600, "reason": "excluded if > 600"}]}

    # 500 > 600 is False -> Should NOT exclude
    out_safe = run_exclusion_rules(farm_safe, all_species, safe_rules, dep_lookup={})
    assert 102 in out_safe["candidate_ids"]


def test_species_specific_categorical_exclusion():
    """
    Tests that the '==' and '!=' operators correctly handle
    lists of values (e.g., multiple allowed or prohibited soil types).
    """

    # All species in the system
    all_species = [{"id": 101, "name": "Species A"}, {"id": 102, "name": "Species B"}]

    # Test Categorical Single String (instead of list)
    # The engine should handle a single string threshold like "clay"
    farm_soil = {"id": 1, "soil_texture": "clay"}

    categorical_rules = {102: [{"feature": "soil_texture", "operator": "==", "value": "clay", "reason": "clay is prohibited"}]}

    out_cat = run_exclusion_rules(farm_soil, all_species, categorical_rules, dep_lookup={})
    assert 102 not in out_cat["candidate_ids"]

    excluded_item = next(e for e in out_cat["excluded_species"] if e["id"] == 102)
    assert "excluded: clay is prohibited" in excluded_item["reasons"][0]

    # Test "==" logic: Farm soil matches one item in the species list
    farm_loam = {"id": 1, "soil_texture": "loam"}
    rules_in = {102: [{"feature": "soil_texture", "operator": "==", "value": ["sand", "loam", "silt"], "reason": "soil not supported"}]}
    # loam is in [sand, loam, silt] -> Should EXCLUDE
    out_exclude = run_exclusion_rules(farm_loam, all_species, rules_in, dep_lookup={})
    assert 102 not in out_exclude["candidate_ids"]
    assert "excluded: soil not supported" in out_exclude["excluded_species"][0]["reasons"][0]

    # Test "==" logic: Farm soil matches any in the list
    farm_clay = {"id": 1, "soil_texture": "clay"}
    # clay is NOT in [sand, loam, silt] -> Should PASS
    out_pass = run_exclusion_rules(farm_clay, all_species, rules_in, dep_lookup={})
    assert 102 in out_pass["candidate_ids"]

    # Test "!=" logic: Farm soil does not match an item in the list.
    rules_not_equal = {102: [{"feature": "soil_texture", "operator": "!=", "value": ["clay"], "reason": "must be clay"}]}
    # Farm is clay, Rule says != [clay] -> Should PASS
    out_pass_cat = run_exclusion_rules(farm_clay, all_species, rules_not_equal, dep_lookup={})
    assert 102 in out_pass_cat["candidate_ids"]

    # Test Case Insensitivity within Lists
    farm_caps = {"id": 1, "soil_texture": "SAND"}
    # Rule has lowercase 'sand' -> Should PASS
    out_case = run_exclusion_rules(farm_caps, all_species, rules_in, dep_lookup={})
    assert 101 in out_case["candidate_ids"]


def test_malformed_rules_and_empty_data():
    """
    Ensures that malformed rules or missing data never trigger an accidental exclusion.
    """
    # All species in the system
    all_species = [{"id": 101, "name": "Species A"}]

    # Test: Missing Threshold Value
    rules_missing_val = {101: [{"feature": "ph", "operator": "<", "value": None, "reason": "bad rule"}]}
    farm_ph = {"id": 1, "ph": 6.0}
    out = run_exclusion_rules(farm_ph, all_species, rules_missing_val, dep_lookup={})
    assert 101 in out["candidate_ids"], "Should pass if rule value is None"

    # Test: Missing Feature
    rules_missing_feat = {101: [{"feature": None, "operator": "<", "value": 6.0, "reason": "bad rule"}]}
    out = run_exclusion_rules(farm_ph, all_species, rules_missing_feat, dep_lookup={})
    assert 101 in out["candidate_ids"], "Should pass if rule feature is None"

    # Test: Missing Operator
    rules_missing_op = {101: [{"feature": "ph", "operator": None, "value": 6.0, "reason": "bad rule"}]}
    out = run_exclusion_rules(farm_ph, all_species, rules_missing_op, dep_lookup={})
    assert 101 in out["candidate_ids"], "Should pass if rule operator is None"

    # Test: Completely Empty Rules Table
    out = run_exclusion_rules(farm_ph, all_species, rules_lookup={}, dep_lookup={})
    assert 101 in out["candidate_ids"], "Should pass if no rules exist in database"

    # Test: Empty Farm Value (Farm data is missing the attribute)
    farm_empty = {"id": 1}  # Missing 'ph' key entirely
    rules_valid = {101: [{"feature": "ph", "operator": "<", "value": 6.0, "reason": "valid rule"}]}
    out = run_exclusion_rules(farm_empty, all_species, rules_valid, dep_lookup={})
    assert 101 not in out["candidate_ids"], "Should not pass if farm measurement is missing"

    # Test: Threshold Value not float
    rules_invalid_threshold = {101: [{"feature": "ph", "operator": "<", "value": "not_a_number", "reason": "valid rule"}]}
    out = run_exclusion_rules(farm_ph, all_species, rules_invalid_threshold, dep_lookup={})
    assert 101 in out["candidate_ids"], "Should pass if threshold value for numeric feature is not a valid number"


def test_wrong_data_type():
    """
    Tests the behaviour when farm values are of the wrong data type.
    """
    # All species in the system
    all_species = [{"id": 101, "name": "Species A"}]

    # Test: Farm Value not float
    farm_non_float = {"id": 1, "ph": "not_a_number"}  # 'ph' is a string
    rules_valid = {101: [{"feature": "ph", "operator": "<", "value": 6.0, "reason": "valid rule"}]}
    out = run_exclusion_rules(farm_non_float, all_species, rules_valid, dep_lookup={})
    assert 101 not in out["candidate_ids"], "Should not pass if farm measurement is not a valid number"


# Testing for ecological and agroforestry


def test_ecological_function_filtering():
    """
    Test that species must satisfy farm ecological requirements (boolean flags).
    """
    all_species = [
        {"id": 1, "name": "Species A", "nitrogen_fixing": True},
        {"id": 2, "name": "Species B", "nitrogen_fixing": False},
    ]

    # Farm REQUIRES nitrogen fixing
    farm = {"id": 1, "nitrogen_fixing": True}

    out = run_exclusion_rules(farm, all_species, rules_lookup={}, dep_lookup={})

    assert 1 in out["candidate_ids"]  # passes
    assert 2 not in out["candidate_ids"]  # excluded


def test_agroforestry_type_filtering():
    """
    Test that species must match at least one farm agroforestry type.
    """
    all_species = [
        {"id": 1, "name": "Species A", "agroforestry_types": ["block", "boundary"]},
        {"id": 2, "name": "Species B", "agroforestry_types": ["intercropping"]},
    ]

    farm = {"id": 1, "agroforestry_types": ["block"]}

    out = run_exclusion_rules(farm, all_species, rules_lookup={}, dep_lookup={})

    assert 1 in out["candidate_ids"]
    assert 2 not in out["candidate_ids"]


def test_combined_ecological_and_agroforestry_filters():
    """
    Test both ecological and agroforestry filters together.
    """
    all_species = [
        {"id": 1, "name": "Species A", "nitrogen_fixing": True, "agroforestry_types": ["block"]},
        {"id": 2, "name": "Species B", "nitrogen_fixing": False, "agroforestry_types": ["boundary"]},
    ]

    farm = {
        "id": 1,
        "nitrogen_fixing": True,
        "agroforestry_types": ["block"],
    }

    out = run_exclusion_rules(farm, all_species, rules_lookup={}, dep_lookup={})

    assert 1 in out["candidate_ids"]
    assert 2 not in out["candidate_ids"]


def test_agroforestry_type_list_handling():
    """
    Ensure agroforestry matching works for list inputs.
    """
    all_species = [
        {"id": 1, "name": "Species A", "agroforestry_types": ["block", "boundary"]},
        {"id": 2, "name": "Species B", "agroforestry_types": ["intercropping"]},
    ]

    farm = {"id": 1, "agroforestry_types": ["boundary"]}

    out = run_exclusion_rules(farm, all_species, rules_lookup={}, dep_lookup={})

    assert 1 in out["candidate_ids"]
    assert 2 not in out["candidate_ids"]
