import numpy as np


class AhpCore:
    def __init__(self):
        """Initialise the AHP core with a Random Consistency Index (RI) table."""
        # Random Consistency Index (RI) table based on matrix size
        self.ri_dict = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}

    def calculate_weights(self, matrix_data):
        """Calculate AHP weights and consistency metrics from a pairwise matrix.

        Args:
            matrix_data: Square pairwise comparison matrix.

        Returns:
            Dictionary containing:
                - ``weights``: Normalised principal eigenvector values.
                - ``consistency_ratio``: Saaty consistency ratio (CR).
                - ``consistency_index``: Consistency index (CI).
                - ``is_consistent``: ``True`` when CR is below ``0.1``.

        References:
            [1] T. L. Saaty, "How to make a decision: The analytic hierarchy
            process," European Journal of Operational Research, 1990.
            DOI: https://doi.org/10.1016/0377-2217(90)90057-I

            [2] T. L. Saaty, "Deriving the AHP 1-9 Scale from First Principles,"
            ISAHP proceedings, 2001.
            DOI: https://doi.org/10.13033/isahp.y2001.030

            [3] Hatice Esen, "Analytical Hierarchy Process Problem Solution,"
            IntechOpen, 2023.
            DOI: https://doi.org/10.5772/intechopen.1001072
        """
        matrix = np.array(matrix_data)
        n = matrix.shape[0]

        # Calculate Eigenvalues and Eigenvectors
        eigvals, eigvecs = np.linalg.eig(matrix)

        # The principal eigenvalue is the largest real one
        max_idx = np.argmax(np.real(eigvals))
        principal_eigenvalue = np.real(eigvals[max_idx])

        # The priority vector is the corresponding eigenvector
        priority_vector = np.real(eigvecs[:, max_idx])

        # Normalise so sum is 1
        weights = priority_vector / np.sum(priority_vector)

        # Calculate Consistency Index (CI) and Consistency Ratio (CR)
        if n > 2:
            ci = (principal_eigenvalue - n) / (n - 1)
            ri = self.ri_dict.get(n, 1.49)
            cr = ci / ri if ri != 0 else 0.0
        else:
            ci, cr = 0.0, 0.0

        return {
            "weights": weights.tolist(),
            "consistency_ratio": float(cr),
            "consistency_index": float(ci),
            "is_consistent": bool(cr < 0.1),  # Threshold from [2]
        }
