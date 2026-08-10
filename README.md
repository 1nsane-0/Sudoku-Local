# Sudoku Local

Локальная версия Sudoku Solver: сайт и Python API запускаются на компьютере пользователя.

## Возможности

- распознавание Sudoku с изображения
- ручное исправление распознанной сетки
- решение Sudoku backtracking/CSP-алгоритмом
- готовые example images
- полностью локальный запуск без облачного бэкенда

## Быстрый Старт

1. Установи Python 3.10+.
2. Установи зависимости один раз:

```bash
python install_requirements.py
```

3. Запусти приложение:

```bash
python start_local.py
```

На Windows можно дважды кликнуть:

```text
run.bat
```

После запуска откроется:

```text
http://127.0.0.1:8010/sudoku
```

## Tesseract OCR

Для распознавания цифр нужен Tesseract OCR.

Windows:

1. Установи Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Добавь папку с `tesseract.exe` в `PATH`.
3. Перезапусти терминал.

Без Tesseract ручной ввод и кнопка Solve всё равно работают.

## Структура

```text
.
├── Site/                  # frontend
├── local_app.py           # FastAPI app: static site + API
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
