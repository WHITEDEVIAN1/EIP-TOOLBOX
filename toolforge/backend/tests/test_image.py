"""
Image Module Tests — pytest
Tests all image processing operations end-to-end.
"""

import pytest
import io
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


def _make_test_image(width=100, height=100, mode="RGB", color=(120, 80, 200)) -> bytes:
    """Create a minimal in-memory PNG image for upload."""
    img = Image.new(mode, (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _post_image(endpoint: str, extra_data: dict = None) -> dict:
    data = extra_data or {}
    response = client.post(
        f"/api/image{endpoint}",
        files={"file": ("test.png", _make_test_image(), "image/png")},
        data=data,
    )
    return response


# ── Health ────────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_image_info():
    r = client.get("/api/image/info")
    assert r.status_code == 200
    assert "operations" in r.json()


# ── Convert ───────────────────────────────────────────────────────────────────

def test_convert_to_jpeg():
    r = _post_image("/convert", {"format": "jpg", "quality": "85"})
    assert r.status_code == 200
    assert r.json()["format"] == "jpg"


def test_convert_to_webp():
    r = _post_image("/convert", {"format": "webp", "quality": "90"})
    assert r.status_code == 200


# ── Resize ────────────────────────────────────────────────────────────────────

def test_resize_by_width():
    r = _post_image("/resize", {"width": "50"})
    assert r.status_code == 200


def test_resize_by_both():
    r = _post_image("/resize", {"width": "60", "height": "60", "keep_aspect": "false"})
    assert r.status_code == 200


def test_resize_no_dims():
    r = _post_image("/resize")
    assert r.status_code == 400


# ── Crop ──────────────────────────────────────────────────────────────────────

def test_crop():
    r = _post_image("/crop", {"left": "0", "top": "0", "right": "50", "bottom": "50"})
    assert r.status_code == 200


# ── Rotate ────────────────────────────────────────────────────────────────────

def test_rotate_90():
    r = _post_image("/rotate", {"angle": "90"})
    assert r.status_code == 200


# ── Flip ──────────────────────────────────────────────────────────────────────

def test_flip_horizontal():
    r = _post_image("/flip", {"direction": "horizontal"})
    assert r.status_code == 200


def test_flip_invalid():
    r = _post_image("/flip", {"direction": "diagonal"})
    assert r.status_code == 400


# ── Adjust ────────────────────────────────────────────────────────────────────

def test_adjust():
    r = _post_image("/adjust", {
        "brightness": "1.2", "contrast": "1.1",
        "saturation": "0.8", "sharpness": "1.5"
    })
    assert r.status_code == 200


# ── Filters ───────────────────────────────────────────────────────────────────

def test_list_filters():
    r = client.get("/api/image/filters")
    assert r.status_code == 200
    filters = r.json()["filters"]
    assert len(filters) >= 10
    names = [f["name"] for f in filters]
    assert "blur" in names
    assert "sepia" in names


def test_apply_blur():
    r = _post_image("/filter", {"filter_name": "blur", "intensity": "1.5"})
    assert r.status_code == 200


def test_apply_sepia():
    r = _post_image("/filter", {"filter_name": "sepia"})
    assert r.status_code == 200


def test_apply_sketch():
    r = _post_image("/filter", {"filter_name": "sketch"})
    assert r.status_code == 200


def test_apply_cartoon():
    r = _post_image("/filter", {"filter_name": "cartoon"})
    assert r.status_code == 200


def test_apply_invalid_filter():
    r = _post_image("/filter", {"filter_name": "nonexistent_filter"})
    assert r.status_code == 400


# ── Compress ──────────────────────────────────────────────────────────────────

def test_compress():
    img_bytes = _make_test_image(500, 500)
    r = client.post(
        "/api/image/compress",
        files={"file": ("big.jpg", img_bytes, "image/jpeg")},
        data={"quality": "60"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "saving_percent" in body


# ── Grayscale / Invert ────────────────────────────────────────────────────────

def test_grayscale():
    r = _post_image("/grayscale")
    assert r.status_code == 200


def test_invert():
    r = _post_image("/invert")
    assert r.status_code == 200


# ── Watermark ─────────────────────────────────────────────────────────────────

def test_watermark_text():
    r = _post_image("/watermark/text", {
        "text": "ToolForge",
        "position": "bottom-right",
        "opacity": "0.6",
        "font_size": "24",
        "color": "white",
    })
    assert r.status_code == 200


# ── Metadata ──────────────────────────────────────────────────────────────────

def test_metadata():
    r = _post_image("/metadata")
    assert r.status_code == 200
    data = r.json()
    assert data["width"] == 100
    assert data["height"] == 100
    assert "exif" in data


def test_strip_metadata():
    r = _post_image("/metadata/strip")
    assert r.status_code == 200
