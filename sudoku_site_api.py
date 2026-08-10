from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from sudoku_solver import backtrack


Grid = list[list[int]]

EXAMPLES_DIR = Path(__file__).resolve().parent / "Site" / "assets" / "sudoku" / "examples"
ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


class SudokuGridRequest(BaseModel):
    grid: Grid


def register_sudoku_api(app: FastAPI) -> None:
    @app.get("/api/health")
    async def api_health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/solve")
    async def solve_sudoku(payload: SudokuGridRequest) -> dict[str, Grid]:
        grid = normalize_grid(payload.grid)
        ensure_no_conflicts(grid)

        assignment = grid_to_assignment(grid)
        variables = [(row, col) for row in range(9) for col in range(9)]
        domain = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        solved = backtrack(assignment.copy(), variables, domain)
        if solved is None:
            raise HTTPException(status_code=422, detail="Sudoku has no solution.")

        return {"grid": assignment_to_grid(solved)}

    @app.post("/api/recognize")
    async def recognize_sudoku(file: UploadFile = File(...)) -> dict[str, Grid]:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in ALLOWED_IMAGE_SUFFIXES:
            raise HTTPException(status_code=400, detail="Upload PNG, JPG, JPEG, or WEBP image.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(await file.read())

        try:
            from image_to_sudoku import dict_to_grid, image_to_sudoku_dict

            recognized = image_to_sudoku_dict(temp_path)
            return {"grid": dict_to_grid(recognized)}
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        finally:
            temp_path.unlink(missing_ok=True)

    @app.post("/api/recognize-example/{filename}")
    async def recognize_example(filename: str) -> dict[str, Grid]:
        example_path = (EXAMPLES_DIR / Path(filename).name).resolve()
        if EXAMPLES_DIR.resolve() not in example_path.parents:
            raise HTTPException(status_code=400, detail="Invalid example path.")
        if not example_path.exists() or example_path.suffix.lower() not in ALLOWED_IMAGE_SUFFIXES:
            raise HTTPException(status_code=404, detail="Example image not found.")

        try:
            from image_to_sudoku import dict_to_grid, image_to_sudoku_dict

            recognized = image_to_sudoku_dict(example_path)
            return {"grid": dict_to_grid(recognized)}
        except Exception as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc


def normalize_grid(value: Any) -> Grid:
    if not isinstance(value, list) or len(value) != 9:
        raise HTTPException(status_code=400, detail="Grid must contain 9 rows.")

    normalized: Grid = []
    for row in value:
        if not isinstance(row, list) or len(row) != 9:
            raise HTTPException(status_code=400, detail="Each grid row must contain 9 values.")

        normalized_row = []
        for cell in row:
            if not isinstance(cell, int) or cell < 0 or cell > 9:
                raise HTTPException(status_code=400, detail="Grid values must be integers from 0 to 9.")
            normalized_row.append(cell)
        normalized.append(normalized_row)

    return normalized


def grid_to_assignment(grid: Grid) -> dict[tuple[int, int], int]:
    return {(row, col): grid[row][col] for row in range(9) for col in range(9)}


def assignment_to_grid(values: dict[tuple[int, int], int]) -> Grid:
    return [[values[(row, col)] for col in range(9)] for row in range(9)]


def ensure_no_conflicts(grid: Grid) -> None:
    for index in range(9):
        check_unit(grid[index], "row", index)
        check_unit([grid[row][index] for row in range(9)], "column", index)

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            values = [
                grid[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            ]
            check_unit(values, "box", box_row + box_col // 3)


def check_unit(values: list[int], unit_name: str, unit_index: int) -> None:
    filled = [value for value in values if value != 0]
    if len(filled) != len(set(filled)):
        raise HTTPException(status_code=422, detail=f"Sudoku has duplicate values in {unit_name} {unit_index + 1}.")
