from __future__ import annotations

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8010/sudoku"


def missing_packages() -> list[str]:
    packages = []
    for module_name, package_name in [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("multipart", "python-multipart"),
        ("cv2", "opencv-python-headless"),
        ("numpy", "numpy"),
        ("pytesseract", "pytesseract"),
    ]:
        try:
            __import__(module_name)
        except ImportError:
            packages.append(package_name)
    return packages


def main() -> None:
    missing = missing_packages()
    if missing:
        print("Missing packages:")
        print("  " + " ".join(missing))
        print()
        print("Install once:")
        print("  python -m pip install -r requirements.txt")
        input("Press Enter to close...")
        raise SystemExit(1)

    print(f"Opening {URL}")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "local_app:app", "--host", "127.0.0.1", "--port", "8010"],
        cwd=ROOT,
    )
    time.sleep(1)
    webbrowser.open(URL)
    process.wait()


if __name__ == "__main__":
    main()
