import asyncio
from sqlalchemy import text
from src.database import AsyncSessionLocal


async def check_stats():
    async with AsyncSessionLocal() as session:
        # High-Level Totals
        counts = {
            "Total Users": "SELECT count(*) FROM users",
            "Total Farms": "SELECT count(*) FROM farms",
            "Total Species": "SELECT count(*) FROM species",
        }

        print("\n" + "═" * 65)
        print("                DATABASE INGESTION REPORT")
        print("═" * 65)
        for label, query in counts.items():
            try:
                res = await session.execute(text(query))
                print(f" {label:32}: {res.scalar()}")
            except Exception:
                print(f" {label:32}: [Error - Table Missing]")

        # Boundary Completeness
        boundary_query = """
            SELECT 
                (SELECT count(*) FROM boundary) as with_boundary,
                (SELECT count(*) FROM farms f 
                 LEFT JOIN boundary b ON f.id = b.id 
                 WHERE b.id IS NULL) as missing_boundary
        """
        try:
            res = await session.execute(text(boundary_query))
            row = res.fetchone()
            if row:
                print(f" {'Farms with GIS Boundaries':32}: {row[0]}")
                print(f" {'Farms missing GIS Boundaries':32}: {row[1]}")
            else:
                print(f" {'Farms with GIS Boundaries':32}: [No Data]")
                print(f" {'Farms missing GIS Boundaries':32}: [No Data]")
        except Exception as e:
            print(f" Boundary Stats Error: {e}")

        # Soil Texture Breakdown (Farms)
        print("\n" + "─" * 65)
        print(f"{'Soil Texture Name':32} | {'Farms with this Texture'}")
        print("─" * 65)

        texture_query = """
            SELECT st.name, COUNT(f.id) 
            FROM soil_textures st
            LEFT JOIN farms f ON st.id = f.soil_texture_id
            GROUP BY st.name
            ORDER BY COUNT(f.id) DESC
        """
        try:
            results = await session.execute(text(texture_query))
            for name, count in results:
                print(f" {name:32} | {count}")
        except Exception:
            print(" Error fetching Soil Texture breakdown.")

        # Agroforestry Type Breakdown (Farms - Many-to-Many)
        print("\n" + "─" * 65)
        print(f"{'Agroforestry Type':32} | {'Farms with this Type'}")
        print("─" * 65)

        agro_query = """
            SELECT aft.type_name, COUNT(assoc.farm_id) 
            FROM agroforestry_types aft
            LEFT JOIN farm_agroforestry_association assoc ON aft.id = assoc.agroforestry_type_id
            GROUP BY aft.type_name
            ORDER BY COUNT(assoc.farm_id) DESC
        """
        try:
            results = await session.execute(text(agro_query))
            for type_name, count in results:
                print(f" {type_name:32} | {count}")
        except Exception as e:
            print(f" Agroforestry Type Error: {e}")

        # Association Table Ingestion (Links)
        print("\n" + "─" * 65)
        print(f"{'Association Link Type':32} | {'Total Links Ingested'}")
        print("─" * 65)

        associations = {
            "Species <-> Soil Texture": "SELECT count(*) FROM species_soil_texture_association",
            "Species <-> Agroforestry": "SELECT count(*) FROM species_agroforestry_association",
            "Farm <-> Agroforestry": "SELECT count(*) FROM farm_agroforestry_association",
        }

        for label, query in associations.items():
            try:
                res = await session.execute(text(query))
                print(f" {label:32} | {res.scalar()}")
            except Exception:
                print(f" {label:32} | [Error]")

        print("═" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(check_stats())
