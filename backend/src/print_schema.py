# ruff: noqa: F401
import sys
import os
from .database import Base
import src.models

# Add model directory to path (necessary for importing all models)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "models")))


def generate_schema_report():
    """Prints the database schema in a clean Markdown table format."""

    output = ["# POT Database Schema Definition (SQLAlchemy ORM)\n"]

    for table_name, table in Base.metadata.tables.items():
        output.append(f"## TABLE: `{table_name}`\n")

        # Create table header
        output.append(
            "| Column Name | SQL Type | Nullable | Primary Key | Foreign Key |"
        )
        output.append("| :--- | :--- | :--- | :--- | :--- |")

        for column in table.columns:
            # Extract FK info
            fk_target = ""
            if column.foreign_keys:
                fk_target = list(column.foreign_keys)[0].target_fullname

            # Format the row into Markdown
            row = [
                f"`{column.name}`",
                f"`{repr(column.type).split('(')[0]}`",  # Get simplified type (e.g., INTEGER, FLOAT)
                "No" if not column.nullable else "Yes",
                "Yes" if column.primary_key else "No",
                f"{fk_target.split('.')[-1]}" if fk_target else "",
            ]
            output.append("| " + " | ".join(row) + " |")

    # Print all lines to the terminal
    print("\n".join(output))


if __name__ == "__main__":
    generate_schema_report()
