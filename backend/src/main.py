from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import time
from src.routers import (
    farm,
    soil_texture,
    recommendation,
    species,
    auth,
    environmental_profile,
    sapling_estimation,
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
app.include_router(sapling_estimation.router)
# Not created yet
# app.include_router(user.router)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log it to the terminal
    print(f"Path: {request.url.path} | Time: {process_time:.4f}s")

    return response


@app.get("/")
def read_root():
    return {"Planting Optimisation": "Tool"}
