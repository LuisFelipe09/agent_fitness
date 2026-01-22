from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from src.interfaces.api.routers import router as api_router

from src.infrastructure.database import engine, Base
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Fitness Agent")

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with /api prefix for clarity
app.include_router(api_router)

# Serve frontend static files in production
frontend_dist = os.path.join(os.path.dirname(__file__), "../../../frontend/dist")
old_frontend = os.path.join(os.path.dirname(__file__), "../frontend")

# Mount old frontend for backwards compatibility
if os.path.exists(old_frontend):
    app.mount("/static", StaticFiles(directory=old_frontend, html=True), name="static")

# Serve new React frontend if built
if os.path.exists(frontend_dist):
    # Mount assets directory
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    @app.get("/app")
    async def serve_app():
        """Serve the React app"""
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    
    @app.get("/app/{full_path:path}")
    async def serve_app_routes(full_path: str):
        """Serve React app for all /app routes (SPA routing)"""
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # For SPA routes, return index.html
        return FileResponse(os.path.join(frontend_dist, "index.html"))


@app.get("/")
def read_root():
    return {
        "message": "AI Fitness Agent API is running",
        "endpoints": {
            "api_docs": "/docs",
            "old_frontend": "/static/index.html",
            "new_frontend": "/app" if os.path.exists(frontend_dist) else "Not built yet"
        }
    }
