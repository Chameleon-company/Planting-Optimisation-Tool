import os
import sys
from sqlalchemy import create_engine
from sqlalchemy_schemadisplay import create_schema_graph

# Adjust path to find modules when running from root
sys.path.insert(0, os.getcwd())

# 1. Import your settings, Base, and Models
from src.config import settings
from src.database import Base
from src import models  # noqa: F401

# --- Database URL and Engine Creation ---
db_url_async = settings.DATABASE_URL
# Using synchronous driver for compatibility with sqlalchemy_schemadisplay
DATABASE_URL = db_url_async.replace("asyncpg", "psycopg2")

# Create engine
print(f"Connecting to database to generate ERD: {DATABASE_URL.split('@')[-1]}")
engine = create_engine(DATABASE_URL)

# Explicitly reflect the schema from the DB into Base.metadata
Base.metadata.reflect(bind=engine)

# Create graph of ERD
graph = create_schema_graph(
    engine=engine,
    metadata=Base.metadata,
    show_datatypes=True,
    show_indexes=False,
    rankdir="TB",
    concentrate=True,
)

graph.set_node_defaults(
    shape="Mrecord", fontsize="10", bgcolor="lightyellow", fontname="Helvetica"
)

graph.set("ranksep", "0.7")
graph.set("nodesep", "0.4")
graph.set("splines", "ortho")
graph.set("layout", "dot")

# 3. Draw the diagram
graph.write("ERD.svg", format="svg")

print("\nSuccessfully generated PostGIS ERD as ERD.svg")
