from exclusion_rules.exclusion_core_logic import _check_topographic_requirements


# ------------------------------------------------------------
# Riparian Requirement Tests
# ------------------------------------------------------------
def test_riparian_demand_met_passes():
    farm = {"riparian": True}
    # Pterocarpus indicus is marked as riparian
    species = {"id": 3, "name": "Pterocarpus indicus", "riparian": True}

    reasons = _check_topographic_requirements(species, farm)
    assert reasons == []


def test_riparian_demand_not_met_excludes():
    farm = {"riparian": True}
    # Tectona grandis is marked as not riparian
    species = {"id": 2, "name": "Tectona grandis", "riparian": False}

    reasons = _check_topographic_requirements(species, farm)
    assert "excluded: species is not suitable for riparian zones" in reasons


# ------------------------------------------------------------
# Coastal Requirement Tests
# ------------------------------------------------------------
def test_coastal_demand_met_passes():
    farm = {"coastal": True}
    # Casuarina equisetifolia is marked as coastal
    species = {"id": 1, "name": "Casuarina equisetifolia", "coastal": True}

    reasons = _check_topographic_requirements(species, farm)
    assert reasons == []


def test_coastal_demand_not_met_excludes():
    farm = {"coastal": True}
    # Santalum album is marked as not coastal
    species = {"id": 4, "name": "Santalum album", "coastal": False}

    reasons = _check_topographic_requirements(species, farm)
    assert "excluded: species is not suitable for coastal zones" in reasons


# ------------------------------------------------------------
# Neutral Pass (No Demand)
# ------------------------------------------------------------
def test_no_topographic_demand_passes_everything():
    # Farm doesn't care about riparian or coastal
    farm = {"riparian": False, "coastal": False}
    species = {"id": 99, "riparian": False, "coastal": False}

    reasons = _check_topographic_requirements(species, farm)
    assert reasons == []
