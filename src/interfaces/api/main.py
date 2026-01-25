from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
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
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router)

# Serve React frontend in production
frontend_dist = os.path.join(os.path.dirname(__file__), "../../../frontend/dist")

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
        return FileResponse(os.path.join(frontend_dist, "index.html"))


@app.get("/")
def read_root():
    """API root - redirects to app or shows API info"""
    if os.path.exists(frontend_dist):
        return RedirectResponse(url="/app")
    return {
        "message": "AI Fitness Agent API is running",
        "docs": "/docs",
        "frontend": "Build frontend with: cd frontend && npm run build"
    }

