from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import seaborn as sns
import numpy as np

# Use mpltern's ternary projection and the official USDA polygon dataset
from mpltern.datasets import soil_texture_classes

sns.set_theme(style="whitegrid")

here = Path(__file__).resolve().parents[2]
out_dir = here / "suitability_scoring" / "docs" / "images"


def calculate_centroid(vertices):
    """
    Compute the centroid (geometric center) of a simple 2D polygon using the
    signed-area (shoelace) formula.

    Uses the signed area A and the standard centroid formula:
        A = 0.5 * sum_i (x_i * y_{i+1} - x_{i+1} * y_i)
        C = (1/(6A)) * sum_i ( (v_i + v_{i+1}) * cross_i )

    The sign of A depends on vertex ordering (CCW positive, CW negative) and is
    correctly handled by the formula.

    :param vertices: Polygon vertices in 2D Cartesian coordinates, (N, 2) array-like
    :raises: ValueError if fewer than 3 unique vertices, wrong shape, or degenerate (zero area).
    :returns: The (x, y) centroid of the polygon, (2,) ndarray.
    """
    v = np.asarray(vertices, dtype=np.float64)

    # Basic validation
    if v.ndim != 2 or v.shape[1] != 2:
        raise ValueError("vertices must be a (N, 2) array-like of 2D points.")
    if v.shape[0] < 3:
        raise ValueError("At least 3 vertices are required to form a polygon.")

    # If closed, drop the duplicated last vertex
    if np.allclose(v[0], v[-1]):
        v = v[:-1]
        if v.shape[0] < 3:
            raise ValueError(
                "After removing duplicate last vertex, not enough points remain."
            )

    # Roll to pair (v_i, v_{i+1})
    vi = v
    vj = np.roll(v, -1, axis=0)

    # Cross (scalar z-component for 2D vectors)
    cross = vi[:, 0] * vj[:, 1] - vj[:, 0] * vi[:, 1]

    area = 0.5 * np.sum(cross)
    if np.isclose(area, 0.0):
        raise ValueError(
            "Degenerate polygon: area is zero or numerically close to zero."
        )

    centroid = np.sum((vi + vj) * cross[:, None], axis=0) / (6.0 * area)
    return centroid


# Change "silt loam"to "silty loam" for consistency with project naming
soil_texture_classes["silty loam"] = soil_texture_classes.pop("silt loam")

fig = plt.figure(figsize=(9, 8))
ax = plt.subplot(projection="ternary", ternary_sum=100.0)

# Draw USDA polygons with labels
palette = sns.color_palette("Set3", n_colors=len(soil_texture_classes))
for (label, verts), color in zip(soil_texture_classes.items(), palette):
    # verts is an Nx3 array-like of [Clay, Sand, Silt] percentages
    tn0, tn1, tn2 = np.array(verts).T  # clay, sand, silt

    # Create a polygon, returned as a list of polygons
    patch = ax.fill(tn0, tn1, tn2, ec="k", fc=color, alpha=0.6, zorder=2.1)

    # Calculate the centroid of the polygon. Using the cartesian co-ordinates of its vertices
    centroid = calculate_centroid(patch[0].get_xy())
    ax.text(
        centroid[0],
        centroid[1],
        label,
        ha="center",
        va="center",
        fontsize=9,
        transform=ax.transData,
    )

# Configure ternary axes (ticks & labels)
ax.taxis.set_major_locator(MultipleLocator(10.0))
ax.laxis.set_major_locator(MultipleLocator(10.0))
ax.raxis.set_major_locator(MultipleLocator(10.0))
ax.taxis.set_minor_locator(AutoMinorLocator(2))
ax.laxis.set_minor_locator(AutoMinorLocator(2))
ax.raxis.set_minor_locator(AutoMinorLocator(2))
ax.grid(which="both")

ax.set_tlabel("Clay (%)")
ax.set_llabel("Sand (%)")
ax.set_rlabel("Silt (%)")

ax.set_title("USDA Soil Texture Triangle", fontsize=12)
plt.tight_layout()
out_path = out_dir / "USDA_soil_texture_triangle.png"
plt.savefig(out_path)
