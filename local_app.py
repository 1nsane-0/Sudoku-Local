from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from sudoku_site_api import register_sudoku_api


app = FastAPI(title="Sudoku Local")

register_sudoku_api(app)
app.mount("/", StaticFiles(directory="Site", html=True), name="site")
