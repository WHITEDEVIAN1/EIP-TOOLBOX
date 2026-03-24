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


@app.get("/")
async def root():
    return {"message": "ToolForge API is running 🚀", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
