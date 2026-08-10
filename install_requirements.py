from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
    cwd=ROOT,
    check=True,
)
