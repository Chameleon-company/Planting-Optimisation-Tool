from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routers import (
    farm,
    soil_texture,
    recommendation,
    species,
    auth,
    environmental_profile,
)
from core.gee_client import init_gee


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs when the application starts
    try:
        init_gee()
        print("GEE initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize GEE: {e}")

    yield
    print("Shutting down application...")


app = FastAPI(
    title="Planting Optimisation Tool API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(farm.router)
app.include_router(soil_texture.router)
app.include_router(recommendation.router)
app.include_router(species.router)
app.include_router(environmental_profile.router)
# Not created yet
# app.include_router(user.router)


@app.get("/")
def read_root():
    return {"Planting Optimisation": "Tool"}
