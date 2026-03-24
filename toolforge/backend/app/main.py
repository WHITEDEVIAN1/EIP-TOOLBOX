"""ToolForge — FastAPI Backend Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.routes import image_router

# Create storage dirs eagerly so StaticFiles never raises RuntimeError
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    yield


app = FastAPI(
    title="ToolForge API",
    description="Universal File Toolbox — Image · Audio · Document",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server and Vercel domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount output files as static so frontend can download results
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

# Routers
app.include_router(image_router, prefix="/api/image", tags=["Image Toolbox"])

@app.get("/health")
async def health():
    return {"status": "ok"}

# ─── Serve React Frontend ─────────────────────────────────────
# Mount the React dist/assets folder
import os
from fastapi.responses import FileResponse
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "dist")

if os.path.exists(os.path.join(frontend_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="frontend_assets")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Catch-all route to serve the React SPA index.html"""
    # Check if a specific file is requested in dist (like favicon.ico)
    requested_file = os.path.join(frontend_dist, full_path)
    if os.path.isfile(requested_file):
        return FileResponse(requested_file)
    
    # Fallback to index.html for React Router / SPA
    index_file = os.path.join(frontend_dist, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    return {"message": "ToolForge API is running 🚀. Please build the frontend to see the UI.", "version": "1.0.0"}
