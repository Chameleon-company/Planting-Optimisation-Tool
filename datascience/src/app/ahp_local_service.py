import csv
import os

import yaml


class AhpLocalDataManager:
    """Manage local AHP config and parameter persistence."""

    FIELDNAMES = (
        "species_id",
        "feature",
        "score_method",
        "weight",
        "trap_left_tol",
        "trap_right_tol",
    )

    def __init__(self, yaml_path="config/recommend.yaml", species_path="data/species.csv", csv_path="data/species_params.csv"):
        """Initialise file paths used by the local data manager.

        Args:
            yaml_path (str): Path to the recommendation configuration YAML file.
            species_path (str): Path to the species lookup CSV file.
            csv_path (str): Path to the species parameter output CSV file.
        """
        self.yaml_path = yaml_path
        self.species_path = species_path
        self.csv_path = csv_path

    def load_config(self):
        """Load configured features and species metadata from disk.

        Returns:
            A tuple containing:
                - Feature short names from the YAML config.
                - Species records with ``id``, ``name``, and ``common_name``.

        Raises:
            FileNotFoundError: If the YAML configuration file does not exist.
        """
        if not os.path.exists(self.yaml_path):
            raise FileNotFoundError(f"Configuration file '{self.yaml_path}' not found.")

        with open(self.yaml_path, "r") as f:
            data = yaml.safe_load(f)

        features = [(feature_name, feature_cfg["short"]) for feature_name, feature_cfg in data["features"].items()]

        species = []

        with open(self.species_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(row)
                species.append(
                    {
                        "id": int(row["id"]),
                        "name": row["name"],
                        "common_name": row["common_name"],
                    }
                )

        return features, species

    def save_results(self, species_id, feature_names, weights):
        """Save or update AHP feature weights for a species.

        Existing rows are matched by ``(species_id, feature)`` and have only
        their ``weight`` updated. New rows are appended with empty metadata
        fields for scoring method and trapezoid tolerances.

        Args:
            species_id (int): Species identifier to update.
            feature_names (list[str]): Ordered feature names for each weight.
            weights (list[float]): Raw weight values aligned with
                ``feature_names``.

        Returns:
            str: Path to the CSV file that was written.

        Raises:
            AssertionError: If ``feature_names`` and ``weights`` lengths differ.
        """

        assert len(feature_names) == len(weights)

        # Normalise inputs
        weights = [round(float(w), 4) for w in weights]

        rows = []
        index = {}

        # Read existing CSV
        if os.path.exists(self.csv_path):
            with open(self.csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    key = (int(row["species_id"]), row["feature"])
                    index[key] = i
                    rows.append(
                        {
                            "species_id": int(row["species_id"]),
                            "feature": row["feature"],
                            "score_method": row.get("score_method", ""),
                            "weight": row.get("weight", ""),
                            "trap_left_tol": row.get("trap_left_tol", ""),
                            "trap_right_tol": row.get("trap_right_tol", ""),
                        }
                    )

        # Apply updates
        for feature, weight in zip(feature_names, weights):
            key = (species_id, feature[0])

            if key in index:
                # Update weight only
                rows[index[key]]["weight"] = weight
            else:
                # Insert new row with empty metadata
                rows.append(
                    {
                        "species_id": species_id,
                        "feature": feature[0],
                        "score_method": "",
                        "weight": weight,
                        "trap_left_tol": "",
                        "trap_right_tol": "",
                    }
                )

        # Write back to CSV
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)

        return self.csv_path
