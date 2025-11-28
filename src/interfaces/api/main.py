from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.interfaces.api.routers import router as api_router

from src.infrastructure.database import engine, Base
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Fitness Agent")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

# Include routers
app.include_router(api_router)


@app.get("/")
def read_root():
    return {"message": "Fitness Agent API is running. Go to /static/index.html for the Mini App."}
