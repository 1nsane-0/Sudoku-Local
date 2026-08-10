############### вынести потом в отдельный файл
import time

steps = 0
start_time = 0

spinner = ["|", "/", "-", "\\"]


def show_progress():
    elapsed = time.perf_counter() - start_time
    symbol = spinner[(steps // 10000) % len(spinner)]

    print(
        f"\rРешение ищется {symbol}  "
        f"Шагов: {steps:,}  "
        f"Время: {elapsed:.1f} сек.",
        end="",
        flush=True
    )

def solve_with_progress(backtrack_func, assignment, variables, domain):
    global steps, start_time

    steps = 0
    start_time = time.perf_counter()

    result = backtrack_func(assignment, variables, domain)

    elapsed = time.perf_counter() - start_time

    print(
        f"\rРешение завершено. "
        f"Шагов: {steps:,}, время: {elapsed:.2f} сек.          "
    )

    return result


def count_step():
    global steps, start_time

    if start_time == 0:
        start_time = time.perf_counter()

    steps += 1

    # Обновляем строку не на каждом вызове,
    # иначе вывод сильно замедлит программу
    if steps % 10000 == 0:
        show_progress()
##################
