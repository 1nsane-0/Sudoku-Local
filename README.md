# Sudoku Local

A local Sudoku Solver app with a browser UI and a Python FastAPI backend.

The app can recognize a Sudoku board from an image, let you correct the detected grid, and solve it with a backtracking/CSP solver. Everything runs on the user's computer.

## Features

- Sudoku image upload
- editable recognized grid
- prepared example puzzles
- backtracking/CSP Sudoku solver
- local-first setup, no cloud backend required

## Quick Start

1. Install Python 3.10+.
2. Install dependencies once:

```bash
python install_requirements.py
```

3. Start the app:

```bash
python start_local.py
```

On Windows, you can also double-click:

```text
run.bat
```

The app opens at:

```text
http://127.0.0.1:8010/sudoku
```

## Tesseract OCR

Image recognition requires Tesseract OCR.

Windows:

1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Add the folder containing `tesseract.exe` to `PATH`.
3. Restart your terminal.

Without Tesseract, manual grid input and solving still work.

## Project Structure

```text
.
├── Site/                  # frontend files
├── local_app.py           # FastAPI app: static site and API
├── sudoku_site_api.py     # /api endpoints
├── image_to_sudoku.py     # image recognition
├── sudoku_solver.py       # solver
├── requirements.txt
├── install_requirements.py
├── start_local.py
└── run.bat
```

## API

```text
GET  /api/health
POST /api/solve
POST /api/recognize
POST /api/recognize-example/{filename}
```

## Notes

The app runs only on `127.0.0.1`, so uploaded images and Sudoku data stay on the user's machine.
