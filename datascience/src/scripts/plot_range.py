from pathlib import Path
import matplotlib.pyplot as plt

"""
Generates a figure illustrating the range scoring logic:
    - Plateau (a to d): Score is 1
"""
here = Path(__file__).resolve().parents[2]
out_dir = here / "suitability_scoring" / "docs" / "images"

# Define arbitrary parameters for the schematic
a = 20  # Min value
d = 90  # Max value

# Coordinates for the line plot
# Includes padding points outside [a, d] to show the zero baseline
x = [a - 15, a, a, d, d, d + 15]
y = [0, 0, 1, 1, 0, 0]

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the trapezoid line outline
ax.plot(x, y, color="#b6b8b6", linewidth=3, zorder=10)

# Fill under the curve for better visualization
ax.fill_between(x, y, color="#2ca02c", alpha=0.1)

# Shade Plateau (Green Rectangle)
# The region under the curve from 'a' to 'd'
ax.fill_between([a, d], [1, 1], color="green", alpha=0.1, label="Optimal")


# Annotate points a, b, c, d on the X-axis
ax.text(a, -0.08, "a\n(min)", ha="center", va="top", fontsize=12)
ax.text(d, -0.08, "d\n(max)", ha="center", va="top", fontsize=12)

# Annotate Regions
ax.text(
    (a + d) / 2,
    0.5,
    "Optimal",
    ha="center",
    va="center",
    fontsize=12,
    color="green",
)

# Axis formatting
ax.set_ylim(-0.2, 1.3)
ax.set_xlim(a - 10, d + 10)
ax.set_yticks([0, 1.0])
ax.set_yticklabels(["0.0\n(Unsuitable)", "1.0\n(Optimal)"])
ax.set_ylabel("Suitability score", fontsize=12)
ax.set_xlabel("Feature value (e.g., Rainfall, Temp)", fontsize=12)

# Clean up the box (remove top and right spines)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_position(("outward", 10))
ax.spines["bottom"].set_position(("outward", 10))

# Title
ax.set_title("Range Suitability Scoring", fontsize=14, pad=20)

# Save
plt.tight_layout()
out_path = out_dir / "range_scoring.png"
plt.savefig(out_path)
