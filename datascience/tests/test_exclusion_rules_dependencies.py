from exclusion_rules.exclusion_core_logic import run_exclusion_rules


def test_species_with_no_dependencies_stays_candidate():
    """Test that a species with no dependencies remains a candidate when no rules exclude it."""
    farm = {"id": 1, "ph": 6.5}
    all_species = [{"id": 201, "name": "Acacia"}, {"id": 202, "name": "Eucalyptus"}]

    # Empty lookups = no rules, no dependencies
    out = run_exclusion_rules(farm, all_species, rules_lookup={}, dep_lookup={})

    assert set(out["candidate_ids"]) == {201, 202}
    assert out["excluded_species"] == []


def test_single_dependency_excludes_when_no_partner_present():
    """Test that if a species requires a partner that is not present, it should be excluded with the correct reason."""
    farm = {"id": 1}
    all_species = [{"id": 301, "name": "Santalum album"}]

    # Sandalwood (301) requires host 400 or 401
    dep_lookup = {301: [400, 401]}

    out = run_exclusion_rules(farm, all_species, rules_lookup={}, dep_lookup=dep_lookup)

    assert 301 not in out["candidate_ids"]
    excluded_301 = next(e for e in out["excluded_species"] if e["id"] == 301)
    assert any("excluded: no suitable host/partner plant available" in r for r in excluded_301["reasons"])


def test_single_dependency_passes_when_partner_present():
    """Test that if a species requires a partner that is present, it should remain a candidate."""
    farm = {"id": 1}
    all_species = [
        {"id": 401, "name": "Santalum album"},
        {"id": 402, "name": "Acacia"},  # Partner present
    ]

    dep_lookup = {401: [402, 403]}  # Needs 402 OR 403

    out = run_exclusion_rules(farm, all_species, rules_lookup={}, dep_lookup=dep_lookup)

    assert 401 in out["candidate_ids"]
    assert 402 in out["candidate_ids"]


def test_dependency_chain_excludes_upstream_when_chain_breaks():
    """
    Test if C is missing, B is excluded. Because B is excluded, A must be excluded.
    The iterative 'while True' loop handles this regardless of dict order.
    """
    farm = {"id": 1}
    all_species = [
        {"id": 501, "name": "Species A"},
        {"id": 502, "name": "Species B"},
        # Species C is missing
    ]

    dep_lookup = {
        501: [502],  # A needs B
        502: [999],  # B needs C (999)
    }

    out = run_exclusion_rules(farm, all_species, {}, dep_lookup)

    assert out["candidate_ids"] == []
    excluded_ids = {e["id"] for e in out["excluded_species"]}
    assert excluded_ids == {501, 502}


def test_circular_dependency_does_not_crash_and_is_stable():
    """
    A requires B, and B requires A.
    Current safe behaviour:
      - both remain candidates (because each has a partner present)
      - function should NOT crash or loop forever
    """
    farm = {"id": 1}
    all_species = [{"id": 601, "name": "A"}, {"id": 602, "name": "B"}]
    dep_lookup = {601: [602], 602: [601]}

    out = run_exclusion_rules(farm, all_species, {}, dep_lookup)

    assert set(out["candidate_ids"]) == {601, 602}


def test_physical_rule_triggers_biological_exclusion():
    """Test that a physical rule (e.g., soil pH) can trigger the exclusion of a species that is also excluded due to dependency issues."""
    farm = {"id": 1, "ph": 4.0}
    all_species = [{"id": 1, "name": "Sandalwood"}, {"id": 2, "name": "Acacia"}]
    # Rule: Acacia (2) excluded if pH < 5.0
    rules_lookup = {2: [{"feature": "ph", "operator": "<", "value": 5.0, "reason": "pH must be greater than 5.0"}]}
    dep_lookup = {1: [2]}  # Sandalwood needs Acacia

    out = run_exclusion_rules(farm, all_species, rules_lookup, dep_lookup)

    assert out["candidate_ids"] == []
    # Both should be excluded: one for pH, one for missing host
    assert {e["id"] for e in out["excluded_species"]} == {1, 2}


def test_circular_dependency_collapses_on_physical_failure():
    """If A and B depend on each other, and A fails a physical rule, then B should also be excluded due to the loss of its partner."""
    farm = {"id": 1, "ph": 4.0}
    all_species = [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]

    # A fails physically
    rules_lookup = {1: [{"feature": "ph", "operator": "<", "value": 5.0, "reason": "pH must be greater than 5.0"}]}
    dep_lookup = {1: [2], 2: [1]}

    out = run_exclusion_rules(farm, all_species, rules_lookup, dep_lookup)
    assert out["candidate_ids"] == []
