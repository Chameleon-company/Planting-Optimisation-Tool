import os
import sys
from sqlalchemy import create_engine
from sqlalchemy_schemadisplay import create_schema_graph

# Adjust path to find modules when running from root directory
sys.path.insert(0, os.getcwd())

from src.config import settings
from src.database import Base
from src import models  # noqa: F401

db_url_async = settings.DATABASE_URL
# Using synchronous driver for compatibility with sqlalchemy_schemadisplay
DATABASE_URL = db_url_async.replace("postgresql+asyncpg://", "postgresql+psycopg://")

# Create engine
print(f"Connecting to database to generate ERD: {DATABASE_URL.split('@')[-1]}")
engine = create_engine(DATABASE_URL)

# To ignore the postGIS included unused tables
target_tables = list(Base.metadata.tables.keys())

# Create graph of ERD
graph = create_schema_graph(
    engine=engine,
    metadata=Base.metadata,
    show_datatypes=True,
    show_indexes=False,
    rankdir="TB",
    concentrate=True,
    restrict_tables=target_tables,
)

graph.set_node_defaults(
    shape="Mrecord", fontsize="10", bgcolor="lightyellow", fontname="Helvetica"
)

graph.set("ranksep", "0.7")
graph.set("nodesep", "0.4")
graph.set("splines", "ortho")
graph.set("layout", "dot")

# Draw the diagram
graph.write("ERD.svg", format="svg")

print("\nSuccessfully generated PostGIS ERD as ERD.svg")
