from __future__ import annotations
from draw_sudoku import draw_sudoku

import argparse
from pathlib import Path

import cv2
import numpy as np


GridDict = dict[tuple[int, int], int]


def order_points(points: np.ndarray) -> np.ndarray:
    points = points.reshape(4, 2).astype("float32")
    ordered = np.zeros((4, 2), dtype="float32")

    point_sums = points.sum(axis=1)
    ordered[0] = points[np.argmin(point_sums)]
    ordered[2] = points[np.argmax(point_sums)]

    point_diffs = np.diff(points, axis=1)
    ordered[1] = points[np.argmin(point_diffs)]
    ordered[3] = points[np.argmax(point_diffs)]
    return ordered


def four_point_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    top_left, top_right, bottom_right, bottom_left = order_points(points)

    width_top = np.linalg.norm(top_right - top_left)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)
    height_right = np.linalg.norm(top_right - bottom_right)
    height_left = np.linalg.norm(top_left - bottom_left)

    side = int(max(width_top, width_bottom, height_right, height_left))
    destination = np.array(
        [[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]],
        dtype="float32",
    )

    matrix = cv2.getPerspectiveTransform(
        np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32"),
        destination,
    )
    return cv2.warpPerspective(image, matrix, (side, side))


def find_sudoku_board(gray: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    threshold = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2,
    )

    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    image_area = gray.shape[0] * gray.shape[1]
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4 and cv2.contourArea(approx) > image_area * 0.15:
            return four_point_transform(gray, approx)

    raise ValueError("Не удалось найти внешнюю рамку судоку на изображении.")


def crop_digit(binary_cell: np.ndarray) -> np.ndarray | None:
    contours, _ = cv2.findContours(binary_cell, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    digit_contours = []
    height, width = binary_cell.shape
    cell_area = height * width
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        touches_border = x <= 2 or y <= 2 or x + w >= width - 2 or y + h >= height - 2
        looks_like_grid_line = w > width * 0.75 or h > height * 0.75

        if touches_border and looks_like_grid_line:
            continue

        if area > cell_area * 0.002 and h > height * 0.12 and w > width * 0.025:
            digit_contours.append(contour)

    if not digit_contours:
        return None

    points = np.vstack(digit_contours)
    x, y, w, h = cv2.boundingRect(points)
    padding = max(3, int(max(w, h) * 0.18))
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(width, x + w + padding)
    y2 = min(height, y + h + padding)
    return binary_cell[y1:y2, x1:x2]


def prepare_digit_for_ocr(digit: np.ndarray) -> np.ndarray:
    digit = cv2.resize(digit, (64, 64), interpolation=cv2.INTER_AREA)
    canvas = np.full((96, 96), 255, dtype=np.uint8)
    # Tesseract лучше читает темные цифры на светлом фоне.
    digit_on_white = cv2.bitwise_not(digit)
    canvas[16:80, 16:80] = digit_on_white
    return canvas


def read_digit(digit_image: np.ndarray, *, debug: bool = False) -> int:
    try:
        import pytesseract
    except ImportError as exc:
        raise RuntimeError("Установите pytesseract: pip install pytesseract") from exc

    raw_answers = []
    for psm in (6, 10, 13):
        config = f"--psm {psm} --oem 3 -c tessedit_char_whitelist=123456789"
        text = pytesseract.image_to_string(digit_image, config=config).strip()
        raw_answers.append(text)
        digits = [char for char in text if char in "123456789"]
        if digits:
            return int(digits[0])

    if debug:
        print(f"OCR не распознал клетку, сырые ответы: {raw_answers!r}")

    return 0


def image_to_sudoku_dict(image_path: str | Path, *, debug: bool = False) -> GridDict:
    image_path = Path(image_path)
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Не удалось открыть изображение: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    board = find_sudoku_board(gray)
    board = cv2.resize(board, (900, 900), interpolation=cv2.INTER_AREA)
    threshold = cv2.adaptiveThreshold(
        board,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        7,
    )

    result: GridDict = {}
    cell_size = 900 // 9
    margin = 8

    for row in range(9):
        for col in range(9):
            y1 = row * cell_size + margin
            y2 = (row + 1) * cell_size - margin
            x1 = col * cell_size + margin
            x2 = (col + 1) * cell_size - margin

            cell = threshold[y1:y2, x1:x2]
            digit = crop_digit(cell)
            if digit is None:
                result[(row, col)] = 0
                continue

            prepared_digit = prepare_digit_for_ocr(digit)
            result[(row, col)] = read_digit(prepared_digit, debug=debug)

    return result


def dict_to_grid(values: GridDict) -> list[list[int]]:
    return [[values[(row, col)] for col in range(9)] for row in range(9)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Распознать не решенное судоку на изображении и вернуть словарь координат.",
    )
    parser.add_argument(
        "image",
        help="Путь к изображению судоку.",
    )
    parser.add_argument("--grid", action="store_true", help="Дополнительно вывести поле списком 9x9.")
    parser.add_argument("--debug", action="store_true", help="Печатать детали неудачного OCR.")
    args = parser.parse_args()

    sudoku = image_to_sudoku_dict(args.image, debug=args.debug)
    print("Распознанное судоку:")
    draw_sudoku(sudoku)
    if args.grid:
        print()
        print("Список 9x9:")
        print(dict_to_grid(sudoku))


if __name__ == "__main__":
    main()
