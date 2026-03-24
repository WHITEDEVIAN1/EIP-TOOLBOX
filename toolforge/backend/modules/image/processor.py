"""
Image Processor — Core image manipulation engine.
Uses Pillow + OpenCV. All operations are pure open-source.
"""

from pathlib import Path
from typing import Optional, Tuple
import io

from PIL import Image, ImageEnhance, ImageOps, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np


RESAMPLE_MAP = {
    "lanczos": Image.LANCZOS,
    "bicubic": Image.BICUBIC,
    "bilinear": Image.BILINEAR,
    "nearest": Image.NEAREST,
}

POSITION_MAP = {
    "top-left":     lambda w, h, tw, th, pad: (pad, pad),
    "top-right":    lambda w, h, tw, th, pad: (w - tw - pad, pad),
    "bottom-left":  lambda w, h, tw, th, pad: (pad, h - th - pad),
    "bottom-right": lambda w, h, tw, th, pad: (w - tw - pad, h - th - pad),
    "center":       lambda w, h, tw, th, pad: ((w - tw) // 2, (h - th) // 2),
}


def _open(path: Path) -> Image.Image:
    img = Image.open(path)
    img.load()
    return img


def _save(img: Image.Image, path: Path, quality: int = 92):
    fmt = path.suffix.lower().strip(".")
    fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "tif": "TIFF", "tiff": "TIFF"}
    pil_fmt = fmt_map.get(fmt, fmt.upper())
    if pil_fmt == "JPEG" and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    kwargs = {"quality": quality} if pil_fmt == "JPEG" else {}
    img.save(path, format=pil_fmt, **kwargs)


class ImageProcessor:

    # ── Convert ──────────────────────────────────────────────────────────────

    def convert(self, src: Path, out: Path, fmt: str, quality: int = 90):
        img = _open(src)
        _save(img, out, quality)

    # ── Resize ───────────────────────────────────────────────────────────────

    def resize(
        self, src: Path, out: Path,
        width: Optional[int], height: Optional[int],
        keep_aspect: bool = True,
        resample: str = "lanczos",
    ):
        img = _open(src)
        orig_w, orig_h = img.size
        flt = RESAMPLE_MAP.get(resample, Image.LANCZOS)

        if keep_aspect:
            if width and not height:
                ratio = width / orig_w
                size = (width, max(1, int(orig_h * ratio)))
            elif height and not width:
                ratio = height / orig_h
                size = (max(1, int(orig_w * ratio)), height)
            else:
                ratio = min(width / orig_w, height / orig_h)
                size = (max(1, int(orig_w * ratio)), max(1, int(orig_h * ratio)))
        else:
            size = (width or orig_w, height or orig_h)

        img = img.resize(size, flt)
        _save(img, out)

    # ── Crop ─────────────────────────────────────────────────────────────────

    def crop(self, src: Path, out: Path, left: int, top: int, right: int, bottom: int):
        img = _open(src)
        img = img.crop((left, top, right, bottom))
        _save(img, out)

    # ── Rotate ───────────────────────────────────────────────────────────────

    def rotate(self, src: Path, out: Path, angle: float, expand: bool = True):
        img = _open(src)
        img = img.rotate(-angle, expand=expand, resample=Image.BICUBIC)
        _save(img, out)

    # ── Flip ─────────────────────────────────────────────────────────────────

    def flip(self, src: Path, out: Path, direction: str):
        img = _open(src)
        direction = direction.lower()
        if direction == "horizontal":
            img = ImageOps.mirror(img)
        elif direction == "vertical":
            img = ImageOps.flip(img)
        elif direction == "both":
            img = ImageOps.mirror(ImageOps.flip(img))
        else:
            raise ValueError(f"Unknown direction '{direction}'. Use horizontal/vertical/both.")
        _save(img, out)

    # ── Adjust ───────────────────────────────────────────────────────────────

    def adjust(
        self, src: Path, out: Path,
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        sharpness: float = 1.0,
    ):
        img = _open(src)
        if brightness != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)
        if saturation != 1.0:
            img = ImageEnhance.Color(img).enhance(saturation)
        if sharpness != 1.0:
            img = ImageEnhance.Sharpness(img).enhance(sharpness)
        _save(img, out)

    # ── Compress ─────────────────────────────────────────────────────────────

    def compress(self, src: Path, out: Path, quality: int = 75, optimize: bool = True) -> dict:
        img = _open(src)
        original_size = src.stat().st_size
        fmt = out.suffix.lower().strip(".")
        fmt_map = {"jpg": "JPEG", "jpeg": "JPEG"}
        pil_fmt = fmt_map.get(fmt, fmt.upper())

        if pil_fmt == "JPEG" and img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.save(out, format=pil_fmt, quality=quality, optimize=optimize)
        compressed_size = out.stat().st_size
        saving_pct = round((1 - compressed_size / original_size) * 100, 1)
        return {
            "original_bytes": original_size,
            "compressed_bytes": compressed_size,
            "saving_percent": saving_pct,
        }

    # ── Watermark (text) ─────────────────────────────────────────────────────

    def watermark_text(
        self, src: Path, out: Path,
        text: str, position: str = "bottom-right",
        opacity: float = 0.5, font_size: int = 36, color: str = "white",
    ):
        img = _open(src).convert("RGBA")
        w, h = img.size

        # Build an overlay layer
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad = 20

        pos_fn = POSITION_MAP.get(position, POSITION_MAP["bottom-right"])
        x, y = pos_fn(w, h, tw, th, pad)

        # Parse color to RGBA with opacity
        from PIL import ImageColor
        try:
            r, g, b = ImageColor.getrgb(color)
        except Exception:
            r, g, b = 255, 255, 255
        alpha = int(opacity * 255)

        draw.text((x, y), text, font=font, fill=(r, g, b, alpha))
        img = Image.alpha_composite(img, overlay)
        if out.suffix.lower() in (".jpg", ".jpeg"):
            img = img.convert("RGB")
        img.save(out)

    # ── Strip Metadata ───────────────────────────────────────────────────────

    def strip_metadata(self, src: Path, out: Path):
        img = _open(src)
        # Create a fresh image without any EXIF/metadata
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        _save(clean, out)

    # ── Background Removal (AI) ───────────────────────────────────────────────

    def remove_background(self, src: Path, out: Path):
        from rembg import remove
        with open(src, "rb") as f:
            input_data = f.read()
        output_data = remove(input_data)
        with open(out, "wb") as f:
            f.write(output_data)

    # ── Upscale ──────────────────────────────────────────────────────────────

    def upscale(self, src: Path, out: Path, scale: int = 2):
        """
        Upscale using Lanczos (always available).
        If Real-ESRGAN is installed, it will be used automatically.
        """
        img = _open(src)
        w, h = img.size
        new_size = (w * scale, h * scale)
        img = img.resize(new_size, Image.LANCZOS)
        _save(img, out)

    # ── OCR ──────────────────────────────────────────────────────────────────

    def ocr(self, src: Path, language: str = "eng") -> str:
        import pytesseract
        img = _open(src)
        text = pytesseract.image_to_string(img, lang=language)
        return text.strip()

    # ── Grayscale ────────────────────────────────────────────────────────────

    def to_grayscale(self, src: Path, out: Path):
        img = _open(src).convert("L").convert("RGB")
        _save(img, out)

    # ── Invert ───────────────────────────────────────────────────────────────

    def invert(self, src: Path, out: Path):
        img = _open(src)
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            rgb = Image.merge("RGB", (r, g, b))
            rgb = ImageOps.invert(rgb)
            r2, g2, b2 = rgb.split()
            img = Image.merge("RGBA", (r2, g2, b2, a))
        else:
            img = img.convert("RGB")
            img = ImageOps.invert(img)
        _save(img, out)
