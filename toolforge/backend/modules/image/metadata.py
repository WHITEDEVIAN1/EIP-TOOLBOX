"""
Metadata Reader — Extract EXIF, file info, dimensions from images.
"""

from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import os


class MetadataReader:

    def extract(self, src: Path) -> dict:
        img = Image.open(src)
        img.load()

        info = {
            "filename": src.name,
            "format": img.format or src.suffix.strip(".").upper(),
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "megapixels": round((img.width * img.height) / 1_000_000, 2),
            "file_size_bytes": os.path.getsize(src),
            "file_size_kb": round(os.path.getsize(src) / 1024, 2),
            "exif": {},
        }

        # Extract EXIF data
        try:
            raw_exif = img._getexif()
            if raw_exif:
                for tag_id, value in raw_exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    # Skip binary/bytes values
                    if isinstance(value, bytes):
                        value = value.decode("utf-8", errors="replace")
                    try:
                        info["exif"][str(tag)] = str(value)
                    except Exception:
                        pass
        except Exception:
            info["exif"] = {}

        # Animation info (GIF)
        if hasattr(img, "n_frames"):
            info["frames"] = img.n_frames

        return info
