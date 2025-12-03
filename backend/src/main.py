from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


# Just a test for now, using tutorial from FastAPI docs
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


# Example schema endpoints:
# WIP


# Farm related endpoints
@app.post("/farms/single")
def submit():
    return


@app.post("/farms/bulk")
def submit_bulk():
    return


@app.get("/farms/{farm_id}")
def retrieve_id():
    return


@app.put("/farms/{farm_id}")
def update_farm():
    return


@app.get("/farms/by-supervisor/{supervisor_id}")
def retrieve_farms():
    return


# Species related endpoints
@app.get("species/approved")
def approved_list():
    return


# ETC
