import numpy as np
from sklearn.model_selection import GroupShuffleSplit


def test_group_shuffle_split_no_farm_leakage():
    rng = np.random.default_rng(42)
    n_farms = 50
    trees_per_farm = rng.integers(1, 20, size=n_farms)

    farm_ids = np.repeat(np.arange(n_farms), trees_per_farm)
    n = len(farm_ids)
    x = rng.normal(size=(n, 4))
    y = rng.normal(size=n)

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(x, y, groups=farm_ids))

    train_farms = set(farm_ids[train_idx])
    test_farms = set(farm_ids[test_idx])

    assert train_farms.isdisjoint(test_farms), "Farms leaked across train/test split"
    assert len(test_idx) > 0 and len(train_idx) > 0
