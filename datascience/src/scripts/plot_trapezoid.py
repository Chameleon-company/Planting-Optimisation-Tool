from pathlib import Path
import matplotlib.pyplot as plt

"""
Generates a figure illustrating the trapezoid scoring logic:
    - Left Shoulder (a to b): Score ramps 0->1
    - Plateau (b to c): Score is 1
    - Right Shoulder (c to d): Score ramps 1->0
"""
here = Path(__file__).resolve().parents[2]
out_dir = here / "suitability_scoring" / "docs" / "images"

# Define arbitrary parameters for the schematic
a = 20  # Min value (start of left shoulder)
b = 40  # Start of plateau
c = 70  # End of plateau
d = 90  # Max value (end of right shoulder)

# Coordinates for the line plot
# Includes padding points outside [a, d] to show the zero baseline
x = [a - 15, a, b, c, d, d + 15]
y = [0, 0, 1, 1, 0, 0]

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the trapezoid line outline
ax.plot(x, y, color="#b6b8b6", linewidth=3, zorder=10)

# Fill under the curve for better visualization
ax.fill_between(x, y, color="#2ca02c", alpha=0.1)

# Shade Left Shoulder (Orange Triangle)
# The region under the curve from 'a' to 'b'
ax.fill_between([a, b], [0, 1], color="orange", alpha=0.4, label="Stress (Shoulder)")

# Shade Right Shoulder (Orange Triangle)
# The region under the curve from 'c' to 'd'
ax.fill_between([c, d], [1, 0], color="orange", alpha=0.4)

# Shade Plateau (Green Rectangle)
# The region under the curve from 'b' to 'c'
ax.fill_between([b, c], [1, 1], color="green", alpha=0.1, label="Optimal (Plateau)")

# Add vertical dashed lines for key points a, b, c, d
# We only draw lines for b and c up to 1.0, and a and d are at 0
ax.plot([b, b], [0, 1], color="grey", linestyle="--", linewidth=1)
ax.plot([c, c], [0, 1], color="grey", linestyle="--", linewidth=1)

# Annotate points a, b, c, d on the X-axis
ax.text(a, -0.08, "a\n(min)", ha="center", va="top", fontsize=12)
ax.text(b, -0.08, "b", ha="center", va="top", fontsize=12)
ax.text(c, -0.08, "c", ha="center", va="top", fontsize=12)
ax.text(d, -0.08, "d\n(max)", ha="center", va="top", fontsize=12)

# Annotate Regions
ax.text(
    (a + b) / 1.8,
    0.3,
    "Left\nShoulder",
    ha="center",
    va="center",
    fontsize=12,
    rotation=45,
    color="#cc5500",
)
ax.text(
    (b + c) / 2,
    0.5,
    "Plateau\n(Optimal)",
    ha="center",
    va="center",
    fontsize=12,
    color="green",
)
ax.text(
    (c + d) / 2.1,
    0.3,
    "Right\nShoulder",
    ha="center",
    va="center",
    fontsize=12,
    rotation=-45,
    color="#cc5500",
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
ax.set_title("Trapezoid Suitability Scoring", fontsize=14, pad=20)

# Save
plt.tight_layout()
out_path = out_dir / "trapezoid_scoring.png"
plt.savefig(out_path)
