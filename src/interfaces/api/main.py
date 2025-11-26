from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.interfaces.api.routers import router
from src.infrastructure.database import engine, Base
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fitness Agent API")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Fitness Agent API is running. Go to /static/index.html for the Mini App."}
