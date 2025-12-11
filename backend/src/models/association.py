from sqlalchemy import Table, Column, ForeignKey
from ..database import Base  # 1 level higher

# Define the association table using the low-level Table construct
# For Many-to-Many relationships
farm_agroforestry_association = Table(
    "farm_agroforestry_association",  # Name of the physical join table
    Base.metadata,
    Column("farm_id", ForeignKey("farms.id"), primary_key=True),
    Column(
        "agroforestry_type_id",
        ForeignKey("agroforestry_types.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

species_agroforestry_association = Table(
    "species_agroforestry_association",
    Base.metadata,
    Column("species_id", ForeignKey("species.id"), primary_key=True),
    Column(
        "agroforestry_type_id",
        ForeignKey("agroforestry_types.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

species_soil_texture_association = Table(
    "species_soil_texture_association",
    Base.metadata,
    Column(
        "species_id", ForeignKey("species.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "soil_texture_id",
        ForeignKey("soil_textures.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
