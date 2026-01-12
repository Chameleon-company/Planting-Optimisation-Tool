from fastapi import FastAPI
from src.routers import farm, soil_texture, recommendation, species, auth
from src.routers import report

app = FastAPI(
    title="Planting Optimisation Tool API",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(farm.router)
app.include_router(soil_texture.router)
app.include_router(recommendation.router)
app.include_router(species.router)
app.include_router(report.router)

# Not created yet
# app.include_router(user.router)


# Just a test for now, using tutorial from FastAPI docs
@app.get("/")
def read_root():
    return {"Planting Optimisation": "Tool"}
