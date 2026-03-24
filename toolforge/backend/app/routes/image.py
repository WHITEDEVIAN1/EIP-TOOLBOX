"""
Image Toolbox — FastAPI Routes
All image processing endpoints.
"""

import uuid
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from modules.image.processor import ImageProcessor
from modules.image.filters import FilterEngine
from modules.image.metadata import MetadataReader

router = APIRouter()
processor = ImageProcessor()
filter_engine = FilterEngine()
metadata_reader = MetadataReader()

# ─── Helpers ──────────────────────────────────────────────────────────────────

def save_upload(file: UploadFile) -> Path:
    """Save uploaded file to uploads dir, return its path."""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    ext = Path(file.filename).suffix or ".png"
    dest = upload_dir / f"{uuid.uuid4()}{ext}"
    with open(dest, "wb") as f:
        f.write(file.file.read())
    return dest


def make_output_path(suffix: str, ext: str) -> Path:
    """Generate a unique output file path."""
    out_dir = Path(settings.OUTPUT_DIR)
    out_dir.mkdir(exist_ok=True)
    return out_dir / f"{uuid.uuid4()}_{suffix}.{ext}"


def file_url(path: Path) -> str:
    """Convert output path to a download URL."""
    return f"/outputs/{path.name}"


# ─── Info ─────────────────────────────────────────────────────────────────────

@router.get("/info")
async def image_module_info():
    """Return list of supported operations."""
    return {
        "module": "Image Toolbox",
        "supported_formats": ["jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff", "ico", "heic"],
        "operations": [
            "convert", "resize", "crop", "rotate", "flip",
            "filter", "adjust", "watermark", "metadata",
            "background_remove", "upscale", "ocr", "compress", "batch"
        ]
    }


# ─── Convert ──────────────────────────────────────────────────────────────────

@router.post("/convert")
async def convert_image(
    file: UploadFile = File(...),
    format: str = Form(..., description="Target format: png, jpg, webp, bmp, tiff, ico"),
    quality: int = Form(90, ge=1, le=100),
):
    """Convert image to a different format."""
    src = save_upload(file)
    fmt = format.lower().strip(".")
    out = make_output_path("converted", fmt)
    try:
        processor.convert(src, out, fmt, quality)
        return {"url": file_url(out), "format": fmt, "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Resize ───────────────────────────────────────────────────────────────────

@router.post("/resize")
async def resize_image(
    file: UploadFile = File(...),
    width: Optional[int] = Form(None, ge=1),
    height: Optional[int] = Form(None, ge=1),
    keep_aspect: bool = Form(True),
    resample: str = Form("lanczos", description="lanczos | bicubic | nearest | bilinear"),
):
    """Resize image to target dimensions."""
    if width is None and height is None:
        raise HTTPException(400, "Provide at least width or height.")
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("resized", ext)
    try:
        processor.resize(src, out, width, height, keep_aspect, resample)
        return {"url": file_url(out), "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Crop ─────────────────────────────────────────────────────────────────────

@router.post("/crop")
async def crop_image(
    file: UploadFile = File(...),
    left: int = Form(..., ge=0),
    top: int = Form(..., ge=0),
    right: int = Form(..., ge=1),
    bottom: int = Form(..., ge=1),
):
    """Crop image to bounding box (left, top, right, bottom)."""
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("cropped", ext)
    try:
        processor.crop(src, out, left, top, right, bottom)
        return {"url": file_url(out), "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Rotate / Flip ────────────────────────────────────────────────────────────

@router.post("/rotate")
async def rotate_image(
    file: UploadFile = File(...),
    angle: float = Form(..., description="Rotation angle in degrees (90, 180, 270, or any)"),
    expand: bool = Form(True),
):
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("rotated", ext)
    try:
        processor.rotate(src, out, angle, expand)
        return {"url": file_url(out), "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


@router.post("/flip")
async def flip_image(
    file: UploadFile = File(...),
    direction: str = Form(..., description="horizontal | vertical | both"),
):
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("flipped", ext)
    try:
        processor.flip(src, out, direction)
        return {"url": file_url(out), "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Filters ──────────────────────────────────────────────────────────────────

@router.get("/filters")
async def list_filters():
    """Return all available filter names."""
    return {"filters": filter_engine.available_filters()}


@router.post("/filter")
async def apply_filter(
    file: UploadFile = File(...),
    filter_name: str = Form(...),
    intensity: float = Form(1.0, ge=0.0, le=5.0),
):
    """Apply a named filter with optional intensity."""
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path(f"filter_{filter_name}", ext)
    try:
        filter_engine.apply(src, out, filter_name, intensity)
        return {"url": file_url(out), "filter": filter_name, "filename": out.name}
    except ValueError as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Adjustments ──────────────────────────────────────────────────────────────

@router.post("/adjust")
async def adjust_image(
    file: UploadFile = File(...),
    brightness: float = Form(1.0, ge=0.0, le=3.0),
    contrast: float = Form(1.0, ge=0.0, le=3.0),
    saturation: float = Form(1.0, ge=0.0, le=3.0),
    sharpness: float = Form(1.0, ge=0.0, le=3.0),
):
    """Adjust brightness, contrast, saturation, sharpness simultaneously."""
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("adjusted", ext)
    try:
        processor.adjust(src, out, brightness, contrast, saturation, sharpness)
        return {"url": file_url(out), "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Compress ─────────────────────────────────────────────────────────────────

@router.post("/compress")
async def compress_image(
    file: UploadFile = File(...),
    quality: int = Form(75, ge=1, le=95),
    optimize: bool = Form(True),
):
    """Compress image (converts PNG/BMP/TIFF to WebP for lossy compression)."""
    src = save_upload(file)
    ext = Path(file.filename).suffix.lower().strip(".") or "jpg"
    if ext in ("png", "bmp", "tiff", "tif", "gif"):
        ext = "webp"
    out = make_output_path("compressed", ext)
    try:
        info = processor.compress(src, out, quality, optimize)
        return {"url": file_url(out), "filename": out.name, **info}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Watermark ────────────────────────────────────────────────────────────────

@router.post("/watermark/text")
async def watermark_text(
    file: UploadFile = File(...),
    text: str = Form(...),
    position: str = Form("bottom-right", description="top-left|top-right|bottom-left|bottom-right|center"),
    opacity: float = Form(0.5, ge=0.1, le=1.0),
    font_size: int = Form(36, ge=8, le=200),
    color: str = Form("white", description="Color name or hex like #FFFFFF"),
):
    """Add a text watermark to an image."""
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("watermarked", ext)
    try:
        processor.watermark_text(src, out, text, position, opacity, font_size, color)
        return {"url": file_url(out), "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Metadata ─────────────────────────────────────────────────────────────────

@router.post("/metadata")
async def get_metadata(file: UploadFile = File(...)):
    """Extract all metadata (EXIF, dimensions, color mode, size) from an image."""
    src = save_upload(file)
    try:
        data = metadata_reader.extract(src)
        return data
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


@router.post("/metadata/strip")
async def strip_metadata(file: UploadFile = File(...)):
    """Remove all metadata (EXIF) from an image — for privacy."""
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("stripped", ext)
    try:
        processor.strip_metadata(src, out)
        return {"url": file_url(out), "filename": out.name, "message": "All metadata removed."}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Background Removal (AI) ──────────────────────────────────────────────────

@router.post("/bg-remove")
async def remove_background(file: UploadFile = File(...)):
    """
    Remove background from image using rembg (U2Net — local AI, no API key).
    Output is always PNG (transparency support).
    """
    src = save_upload(file)
    out = make_output_path("nobg", "png")
    try:
        processor.remove_background(src, out)
        return {"url": file_url(out), "filename": out.name}
    except ImportError:
        raise HTTPException(503, "rembg not installed. Run: pip install rembg")
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Upscale (AI) ─────────────────────────────────────────────────────────────

@router.post("/upscale")
async def upscale_image(
    file: UploadFile = File(...),
    scale: int = Form(2, ge=2, le=4, description="Upscale factor: 2 or 4"),
):
    """
    AI-powered image upscaling using Lanczos (fast) or Real-ESRGAN if available.
    """
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path(f"upscaled_{scale}x", ext)
    try:
        processor.upscale(src, out, scale)
        return {"url": file_url(out), "filename": out.name, "scale": scale}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── OCR ──────────────────────────────────────────────────────────────────────

@router.post("/ocr")
async def ocr_image(
    file: UploadFile = File(...),
    language: str = Form("eng", description="Tesseract language code: eng, hin, fra, deu..."),
):
    """Extract text from image using Tesseract OCR."""
    src = save_upload(file)
    try:
        text = processor.ocr(src, language)
        return {"text": text, "language": language, "char_count": len(text)}
    except ImportError:
        raise HTTPException(503, "pytesseract not installed or Tesseract binary missing.")
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


# ─── Grayscale / Invert ───────────────────────────────────────────────────────

@router.post("/grayscale")
async def to_grayscale(file: UploadFile = File(...)):
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("grayscale", ext)
    try:
        processor.to_grayscale(src, out)
        return {"url": file_url(out), "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)


@router.post("/invert")
async def invert_colors(file: UploadFile = File(...)):
    src = save_upload(file)
    ext = Path(file.filename).suffix.strip(".") or "png"
    out = make_output_path("inverted", ext)
    try:
        processor.invert(src, out)
        return {"url": file_url(out), "filename": out.name}
    except Exception as e:
        raise HTTPException(400, str(e))
    finally:
        src.unlink(missing_ok=True)
