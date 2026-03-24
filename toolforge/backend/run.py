"""
ToolForge backend setup configuration.
Allows running the backend as a Python package.
"""

import subprocess
import sys
from pathlib import Path


def run():
    """Entry point: start uvicorn server."""
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
