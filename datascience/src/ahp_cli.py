from fractions import Fraction

import numpy as np

from ahp.ahp_core import AhpCore
from app.ahp_local_service import AhpLocalDataManager


class AhpCli:
    def __init__(self):
        """Initialise the AHP CLI application state.

        Sets up AHP core computation, local data access, and in-memory
        containers used during interactive profiling.
        """
        self.core = AhpCore()
        self.data = AhpLocalDataManager()
        self.features = []
        self.species_list = []

    def get_user_input(self, factor_a, factor_b):
        """Prompt for and validate a pairwise-comparison preference value.

        Accepts integer, decimal, or fraction input and enforces the AHP
        comparison range.

        Args:
            factor_a (str): Name of the first factor in the comparison prompt.
            factor_b (str): Name of the second factor in the comparison prompt.

        Returns:
            float: A validated preference value in the inclusive range
                ``[1/9, 9]``.

        Raises:
            ValueError: Raised while parsing non-fraction input with
                ``float(...)``; handled internally and retried.
            ZeroDivisionError: Raised for invalid fraction input like ``1/0``;
                handled internally and retried.

        Notes:
            Parsing errors are handled internally, and the prompt is repeated
            until a valid value is entered.
        """
        print(f"\n[?] Compare: {factor_a} vs {factor_b}")
        print("    Scale: 9 (A is extreme) ... 1 (Equal) ... 1/9 (B is extreme)")

        min_val = 1 / 9
        max_val = 9

        while True:
            val_str = input("    Enter preference: ").strip()
            try:
                if "/" in val_str:
                    val = float(Fraction(val_str))
                else:
                    val = float(val_str)

                # Range validation
                if not (min_val <= val <= max_val):
                    print("    Value must be between 1/9 and 9.")
                    continue

                return val

            except (ValueError, ZeroDivisionError):
                print("    Invalid input. Try '5', '0.2', or '1/5'.")

    def run_profile(self, species_dict):
        """Run the AHP profiling workflow for one species.

        Args:
            species_dict: Species metadata containing
                ``id``, ``name``, and ``common_name``.

        Returns:
            None: This method prints output and optionally persists results.

        Raises:
            KeyError: If required keys are missing from ``species_dict``.
        """
        species_name = f"{species_dict['name']} [{species_dict['common_name']}]"
        print("\n" + "=" * 80)
        print(f" Profiling: {species_name}")
        print("=" * 80)

        n = len(self.features)
        matrix = np.eye(n)  # Initialise Identity Matrix

        # Pairwise Comparisons (Upper Triangular)
        count = 0
        total = n * (n - 1) // 2

        for r in range(n):
            for c in range(r + 1, n):
                count += 1
                print(f"\nComparison {count}/{total}")
                val = self.get_user_input(self.features[r][1], self.features[c][1])

                # Fill reciprocal values
                matrix[r, c] = val
                matrix[c, r] = 1.0 / val

        # Calculate using Core
        print("\nComputing weights...")
        result = self.core.calculate_weights(matrix)

        # Display Results
        print("\n" + "-" * 45)
        print(f" Consistency Ratio: {result['consistency_ratio']:.1%} ", end="")
        if result["is_consistent"]:
            print("(OK)")
        else:
            print("(WARNING: >10%)")
        print("-" * 45)

        for i, w in enumerate(result["weights"]):
            print(f" {self.features[i][1]:<15}: {w:.4f}")

        # Save using local service
        if result["is_consistent"]:
            path = self.data.save_results(species_dict["id"], self.features, result["weights"])
            print(f"\n[Success] Saved to {path}")
        else:
            print("\n[Skipped Save] Judgments were inconsistent. Please try again.")

    def start(self):
        """Start the interactive CLI menu loop.

        Loads configuration data and species records, then repeatedly prompts
        the user to run profiling for a selected species.

        Returns:
            None: This method runs until the user exits the menu.

        Raises:
            ValueError: Raised when converting non-numeric menu input with
                ``int(choice)``; handled internally.
        """
        try:
            self.features, self.species_list = self.data.load_config()
        except Exception as e:
            print(f"Error: {e}")
            return

        while True:
            print("\n" + "=" * 60)
            print(" AHP Species Weighting Tool")
            print("=" * 60)
            for i, s in enumerate(self.species_list):
                species_name = f"{s['name']} [{s['common_name']}]"
                print(f" {i + 1}. {species_name}")
            print(" Q. Quit")

            choice = input("\nSelect Species: ").strip().lower()
            if choice == "q":
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.species_list):
                    self.run_profile(self.species_list[idx])
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")


if __name__ == "__main__":
    app = AhpCli()
    app.start()
