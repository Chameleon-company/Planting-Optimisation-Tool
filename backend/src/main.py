from typing import Union
from fastapi import FastAPI
from src.routers import farm, soil_texture
from pydantic import BaseModel
from src.database import get_db_session

app = FastAPI(
    title="Planting Optimisation Tool API",
    version="1.0.0",
)

app.include_router(farm.router)
app.include_router(soil_texture.router)

# Just a test for now, using tutorial from FastAPI docs
@app.get("/")
def read_root():
    return {"Hello": "World"}

# # Farm related endpoints
# @app.post("/farms/single")
# def submit():
#     return


# @app.post("/farms/bulk")
# def submit_bulk():
#     return


# @app.get("/farms/{farm_id}")
# def retrieve_id():
#     return


# @app.put("/farms/{farm_id}")
# def update_farm():
#     return


# @app.get("/farms/by-supervisor/{supervisor_id}")
# def retrieve_farms():
#     return


# # Species related endpoints
# @app.get("species/approved")
# def approved_list():
#     return


# # ETC
