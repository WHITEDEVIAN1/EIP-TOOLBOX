"""
Filter Engine — 30+ named image filters using Pillow + OpenCV.
Inspired by ImageToolbox's 300+ filter list, implemented in open-source Python.
"""

from pathlib import Path
from typing import List
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import cv2
import numpy as np


def _pil_to_cv(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def _cv_to_pil(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))


# ── Filter Registry ────────────────────────────────────────────────────────────

class FilterEngine:

    FILTERS = {
        # ─ Basic ─────────────────────────────────────────────────────────────
        "blur":             "Gaussian blur",
        "sharpen":          "Classic sharpen kernel",
        "edge_detect":      "Sobel edge detection",
        "emboss":           "3D emboss effect",
        "contour":          "Outline contour",
        "smooth":           "Smooth (box blur)",
        "detail":           "Enhance fine details",
        # ─ Color ─────────────────────────────────────────────────────────────
        "grayscale":        "Convert to grayscale",
        "sepia":            "Warm sepia tone",
        "invert":           "Invert all colors",
        "solarize":         "Solarize effect",
        "posterize":        "Reduce color depth",
        "warm":             "Warm color temperature",
        "cool":             "Cool color temperature",
        "vintage":          "Filmic vintage look",
        "cyberpunk":        "Neon cyberpunk palette",
        # ─ Artistic ──────────────────────────────────────────────────────────
        "sketch":           "Pencil sketch",
        "cartoon":          "Cartoon-like effect",
        "oil_paint":        "Oil painting style",
        "pixelate":         "Pixelate (mosaic)",
        "vignette":         "Dark vignette border",
        "noise":            "Add film grain noise",
        "halftone":         "Halftone dot pattern",
        # ─ Blur variants ─────────────────────────────────────────────────────
        "motion_blur":      "Horizontal motion blur",
        "radial_blur":      "Zoom radial blur",
        "box_blur":         "Box / mean blur",
        # ─ Image enhancement ─────────────────────────────────────────────────
        "auto_contrast":    "Stretch contrast to full range",
        "equalize":         "Histogram equalization",
        "clahe":            "Adaptive histogram equalization (CLAHE)",
        "denoise":          "Non-local means denoising (OpenCV)",
        "hdr":              "HDR tone-mapping effect",
    }

    def available_filters(self) -> List[dict]:
        return [{"name": k, "description": v} for k, v in self.FILTERS.items()]

    def apply(self, src: Path, out: Path, filter_name: str, intensity: float = 1.0):
        filter_name = filter_name.lower().replace("-", "_")
        if filter_name not in self.FILTERS:
            raise ValueError(
                f"Unknown filter '{filter_name}'. Available: {', '.join(self.FILTERS.keys())}"
            )
        img = Image.open(src)
        img.load()
        result = getattr(self, f"_f_{filter_name}")(img, intensity)
        _save_pil(result, out)

    # ─── Internal filter implementations ─────────────────────────────────────

    def _f_blur(self, img: Image.Image, intensity: float) -> Image.Image:
        radius = max(1, int(intensity * 3))
        return img.filter(ImageFilter.GaussianBlur(radius=radius))

    def _f_sharpen(self, img: Image.Image, intensity: float) -> Image.Image:
        result = img
        for _ in range(max(1, int(intensity))):
            result = result.filter(ImageFilter.SHARPEN)
        return result

    def _f_edge_detect(self, img: Image.Image, intensity: float) -> Image.Image:
        cv = _pil_to_cv(img)
        gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
        edges = cv2.Sobel(gray, cv2.CV_64F, 1, 1, ksize=3)
        edges = np.uint8(np.abs(edges))
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        return _cv_to_pil(edges_bgr)

    def _f_emboss(self, img: Image.Image, intensity: float) -> Image.Image:
        return img.filter(ImageFilter.EMBOSS)

    def _f_contour(self, img: Image.Image, intensity: float) -> Image.Image:
        return img.filter(ImageFilter.CONTOUR)

    def _f_smooth(self, img: Image.Image, intensity: float) -> Image.Image:
        return img.filter(ImageFilter.SMOOTH_MORE)

    def _f_detail(self, img: Image.Image, intensity: float) -> Image.Image:
        return img.filter(ImageFilter.DETAIL)

    def _f_grayscale(self, img: Image.Image, intensity: float) -> Image.Image:
        gray = img.convert("L").convert("RGB")
        if intensity < 1.0:
            return Image.blend(img.convert("RGB"), gray, intensity)
        return gray

    def _f_sepia(self, img: Image.Image, intensity: float) -> Image.Image:
        arr = np.array(img.convert("RGB"), dtype=np.float32)
        r = arr[:, :, 0] * 0.393 + arr[:, :, 1] * 0.769 + arr[:, :, 2] * 0.189
        g = arr[:, :, 0] * 0.349 + arr[:, :, 1] * 0.686 + arr[:, :, 2] * 0.168
        b = arr[:, :, 0] * 0.272 + arr[:, :, 1] * 0.534 + arr[:, :, 2] * 0.131
        sepia = np.stack([r, g, b], axis=2).clip(0, 255).astype(np.uint8)
        result = Image.fromarray(sepia)
        if intensity < 1.0:
            return Image.blend(img.convert("RGB"), result, intensity)
        return result

    def _f_invert(self, img: Image.Image, intensity: float) -> Image.Image:
        rgb = img.convert("RGB")
        return ImageOps.invert(rgb)

    def _f_solarize(self, img: Image.Image, intensity: float) -> Image.Image:
        threshold = max(1, int(255 * (1 - intensity * 0.5)))
        return ImageOps.solarize(img.convert("RGB"), threshold=threshold)

    def _f_posterize(self, img: Image.Image, intensity: float) -> Image.Image:
        bits = max(1, int(4 - intensity))
        return ImageOps.posterize(img.convert("RGB"), bits)

    def _f_warm(self, img: Image.Image, intensity: float) -> Image.Image:
        arr = np.array(img.convert("RGB"), dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + 30 * intensity, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] - 20 * intensity, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _f_cool(self, img: Image.Image, intensity: float) -> Image.Image:
        arr = np.array(img.convert("RGB"), dtype=np.float32)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + 30 * intensity, 0, 255)
        arr[:, :, 0] = np.clip(arr[:, :, 0] - 20 * intensity, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))

    def _f_vintage(self, img: Image.Image, intensity: float) -> Image.Image:
        img = self._f_sepia(img, 0.6 * intensity)
        return ImageEnhance.Contrast(img).enhance(0.85)

    def _f_cyberpunk(self, img: Image.Image, intensity: float) -> Image.Image:
        arr = np.array(img.convert("RGB"), dtype=np.float32)
        arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.6, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.8 + 40 * intensity, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.4, 0, 255)
        result = Image.fromarray(arr.astype(np.uint8))
        return ImageEnhance.Color(result).enhance(1.5 * intensity)

    def _f_sketch(self, img: Image.Image, intensity: float) -> Image.Image:
        cv = _pil_to_cv(img)
        gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        sketch = cv2.divide(gray, 255 - blur, scale=256)
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        return _cv_to_pil(sketch_bgr)

    def _f_cartoon(self, img: Image.Image, intensity: float) -> Image.Image:
        cv = _pil_to_cv(img)
        gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
        )
        color = cv2.bilateralFilter(cv, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        return _cv_to_pil(cartoon)

    def _f_oil_paint(self, img: Image.Image, intensity: float) -> Image.Image:
        # Approximate with multiple bilateral filters
        cv = _pil_to_cv(img)
        for _ in range(max(1, int(intensity * 2))):
            cv = cv2.bilateralFilter(cv, 9, 75, 75)
        return _cv_to_pil(cv)

    def _f_pixelate(self, img: Image.Image, intensity: float) -> Image.Image:
        w, h = img.size
        factor = max(2, int(20 * intensity))
        small = img.resize((max(1, w // factor), max(1, h // factor)), Image.NEAREST)
        return small.resize((w, h), Image.NEAREST)

    def _f_vignette(self, img: Image.Image, intensity: float) -> Image.Image:
        img = img.convert("RGBA")
        w, h = img.size
        arr = np.array(img, dtype=np.float32)
        X = np.linspace(-1, 1, w)
        Y = np.linspace(-1, 1, h)
        XX, YY = np.meshgrid(X, Y)
        mask = 1 - np.sqrt(XX**2 + YY**2) * 0.7 * intensity
        mask = np.clip(mask, 0, 1)
        arr[:, :, :3] *= mask[:, :, np.newaxis]
        return Image.fromarray(arr.astype(np.uint8), "RGBA")

    def _f_noise(self, img: Image.Image, intensity: float) -> Image.Image:
        arr = np.array(img.convert("RGB"), dtype=np.int16)
        noise = np.random.randint(-int(40 * intensity), int(40 * intensity), arr.shape, dtype=np.int16)
        arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    def _f_halftone(self, img: Image.Image, intensity: float) -> Image.Image:
        gray = img.convert("L")
        w, h = gray.size
        dot_size = max(4, int(12 * intensity))
        result = Image.new("RGB", (w, h), "white")
        from PIL import ImageDraw
        draw = ImageDraw.Draw(result)
        for y in range(0, h, dot_size):
            for x in range(0, w, dot_size):
                pix = gray.getpixel((min(x, w-1), min(y, h-1)))
                radius = (1 - pix / 255) * (dot_size / 2)
                cx, cy = x + dot_size // 2, y + dot_size // 2
                draw.ellipse(
                    [cx - radius, cy - radius, cx + radius, cy + radius],
                    fill="black"
                )
        return result

    def _f_motion_blur(self, img: Image.Image, intensity: float) -> Image.Image:
        size = max(3, int(15 * intensity))
        cv = _pil_to_cv(img)
        kernel = np.zeros((size, size))
        kernel[size // 2, :] = np.ones(size) / size
        blurred = cv2.filter2D(cv, -1, kernel)
        return _cv_to_pil(blurred)

    def _f_radial_blur(self, img: Image.Image, intensity: float) -> Image.Image:
        steps = max(1, int(10 * intensity))
        result = img.convert("RGBA")
        w, h = img.size
        cx, cy = w / 2, h / 2
        for i in range(1, steps + 1):
            scale = 1 + i * 0.02 * intensity
            resized = img.resize((int(w * scale), int(h * scale)), Image.BILINEAR)
            r = resized.crop((
                (resized.width - w) // 2,
                (resized.height - h) // 2,
                (resized.width + w) // 2,
                (resized.height + h) // 2,
            )).convert("RGBA")
            r.putalpha(int(255 / steps))
            result = Image.alpha_composite(result, r)
        return result.convert("RGB")

    def _f_box_blur(self, img: Image.Image, intensity: float) -> Image.Image:
        radius = max(1, int(intensity * 5))
        return img.filter(ImageFilter.BoxBlur(radius))

    def _f_auto_contrast(self, img: Image.Image, intensity: float) -> Image.Image:
        return ImageOps.autocontrast(img.convert("RGB"), cutoff=int(intensity))

    def _f_equalize(self, img: Image.Image, intensity: float) -> Image.Image:
        return ImageOps.equalize(img.convert("RGB"))

    def _f_clahe(self, img: Image.Image, intensity: float) -> Image.Image:
        cv = _pil_to_cv(img)
        lab = cv2.cvtColor(cv, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0 + intensity, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return _cv_to_pil(result)

    def _f_denoise(self, img: Image.Image, intensity: float) -> Image.Image:
        cv = _pil_to_cv(img)
        h_val = int(10 * intensity)
        denoised = cv2.fastNlMeansDenoisingColored(cv, None, h_val, h_val, 7, 21)
        return _cv_to_pil(denoised)

    def _f_hdr(self, img: Image.Image, intensity: float) -> Image.Image:
        cv = _pil_to_cv(img)
        hdr = cv2.detailEnhance(cv, sigma_s=12, sigma_r=0.15 * intensity)
        return _cv_to_pil(hdr)


def _save_pil(img: Image.Image, path: Path):
    fmt = path.suffix.lower().strip(".")
    fmt_map = {"jpg": "JPEG", "jpeg": "JPEG"}
    pil_fmt = fmt_map.get(fmt, fmt.upper())
    if pil_fmt == "JPEG" and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    img.save(path, format=pil_fmt)
