def draw_sudoku(assignment):
    # 1. Собираем поле 9x9 из словаря
    grid = [[0 for _ in range(9)] for _ in range(9)]

    for (row, col), value in assignment.items():
        grid[row][col] = value

    # 2. Красиво рисуем
    top = "+-------+-------+-------+"
    middle = "+-------+-------+-------+"
    bottom = "+-------+-------+-------+"

    print(top)

    for i in range(9):
        row_values = []
        for j in range(9):
            value = grid[i][j]
            row_values.append(str(value) if value != 0 else ".")

        print(
            f"| {' '.join(row_values[0:3])} | "
            f"{' '.join(row_values[3:6])} | "
            f"{' '.join(row_values[6:9])} |"
        )

        if i in [2, 5]:
            print(middle)

    print(bottom)
