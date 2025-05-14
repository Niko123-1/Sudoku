import pygame
import sys
import random
from copy import deepcopy

# Инициализация pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 540, 540
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
ERROR_COLOR = (255, 150, 150)
FIXED_COLOR = (50, 50, 50)  # Цвет для начальных цифр

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Судоку")

# Параметры сложности (сколько клеток оставить видимыми)
DIFFICULTY = 0.4  # От 0.1 (очень сложно) до 0.8 (легко)

# Игровое поле и исходное (неизменяемое) поле
board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
original_board = deepcopy(board)
selected = None  # Выделенная клетка (row, col)


def check_duplicates(s: list) -> bool:
    s = [x for x in s if x != 0]  # Игнорируем пустые клетки
    return len(s) != len(set(s))  # Сравниваем длину списка и множества


def is_valid_sudoku(board: list) -> bool:
    # Проверка строк
    for row in board:
        if check_duplicates(row):
            return False

    # Проверка столбцов
    for col in range(9):
        column = [board[row][col] for row in range(9)]
        if check_duplicates(column):
            return False

    # Проверка малых квадратов 3x3
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            square = []
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    square.append(board[row][col])
            if check_duplicates(square):
                return False

    return True


def get_error_cells(board):
    error_cells = set()

    for row in range(9):
        row_values = [board[row][col] for col in range(9)]
        if check_duplicates(row_values):
            for col in range(9):
                if board[row][col] != 0:
                    error_cells.add((row, col))

    for col in range(9):
        col_values = [board[row][col] for row in range(9)]
        if check_duplicates(col_values):
            for row in range(9):
                if board[row][col] != 0:
                    error_cells.add((row, col))

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            square = []
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    square.append(board[row][col])
            if check_duplicates(square):
                for row in range(box_row, box_row + 3):
                    for col in range(box_col, box_col + 3):
                        if board[row][col] != 0:
                            error_cells.add((row, col))

    return error_cells


def solve_sudoku(board):
    """ Решение судоку с помощью backtracking """
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid_placement(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def is_valid_placement(board, row, col, num):
    """ Проверяет, можно ли поставить число num в клетку (row, col) """
    # Проверка строки
    if num in board[row]:
        return False

    # Проверка столбца
    if num in [board[i][col] for i in range(9)]:
        return False

    # Проверка квадрата 3x3
    box_row, box_col = row // 3 * 3, col // 3 * 3
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if board[i][j] == num:
                return False

    return True


def generate_sudoku():
    """ Генерация валидного поля судоку """
    # Создаем пустое поле
    board = [[0 for _ in range(9)] for _ in range(9)]

    # Заполняем диагональные квадраты (они независимы)
    for box in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                board[box + i][box + j] = nums.pop()

    # Решаем полученное поле
    solve_sudoku(board)

    # Теперь удаляем часть чисел в зависимости от сложности
    cells_to_remove = int(81 * (1 - DIFFICULTY))
    cells_removed = 0

    while cells_removed < cells_to_remove:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if board[row][col] != 0:
            board[row][col] = 0
            cells_removed += 1

    return board


def draw_board():
    screen.fill(WHITE)

    # Рисуем сетку
    for i in range(GRID_SIZE + 1):
        line_width = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), line_width)
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), line_width)

    # Подсвечиваем выбранную клетку
    if selected:
        row, col = selected
        pygame.draw.rect(screen, LIGHT_BLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Подсветка ошибок
    error_cells = get_error_cells(board)
    for (row, col) in error_cells:
        pygame.draw.rect(screen, ERROR_COLOR,
                         (col * CELL_SIZE + 2, row * CELL_SIZE + 2,
                          CELL_SIZE - 4, CELL_SIZE - 4), 2)

    # Рисуем цифры
    font = pygame.font.SysFont('Arial', 40)
    small_font = pygame.font.SysFont('Arial', 20)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] != 0:
                # Определяем цвет цифры
                if original_board[row][col] != 0:  # Начальные цифры
                    color = FIXED_COLOR
                elif (row, col) == selected:  # Выделенная клетка
                    color = RED
                else:  # Обычные цифры
                    color = BLUE

                text = font.render(str(board[row][col]), True, color)
                text_rect = text.get_rect(center=(col * CELL_SIZE + CELL_SIZE // 2,
                                                  row * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, text_rect)


# Генерируем новое поле при старте
board = generate_sudoku()
original_board = deepcopy(board)

# Основной цикл игры
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обработка клика мыши для выбора клетки
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            col = pos[0] // CELL_SIZE
            row = pos[1] // CELL_SIZE
            # Выбираем только пустые или изменяемые клетки
            if original_board[row][col] == 0:
                selected = (row, col)

        # Обработка нажатия клавиш для ввода цифр
        elif event.type == pygame.KEYDOWN:
            if selected:
                row, col = selected
                # Изменяем только клетки, которые были пустыми в original_board
                if original_board[row][col] == 0:
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        board[row][col] = 1
                    elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        board[row][col] = 2
                    elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        board[row][col] = 3
                    elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        board[row][col] = 4
                    elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        board[row][col] = 5
                    elif event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        board[row][col] = 6
                    elif event.key == pygame.K_7 or event.key == pygame.K_KP7:
                        board[row][col] = 7
                    elif event.key == pygame.K_8 or event.key == pygame.K_KP8:
                        board[row][col] = 8
                    elif event.key == pygame.K_9 or event.key == pygame.K_KP9:
                        board[row][col] = 9
                    elif event.key == pygame.K_0 or event.key == pygame.K_BACKSPACE or event.key == pygame.K_KP0:
                        board[row][col] = 0
                    elif event.key == pygame.K_ESCAPE:
                        selected = None
                    elif event.key == pygame.K_r:  # Новая игра по нажатию R
                        board = generate_sudoku()
                        original_board = deepcopy(board)
                        selected = None

    # Отрисовка
    draw_board()

    # Проверка на победу
    if all(all(cell != 0 for cell in row) for row in board) and is_valid_sudoku(board):
        font = pygame.font.SysFont('Arial', 40)
        text = font.render("Победа!", True, RED)
        screen.blit(text, (WIDTH // 2 - 70, HEIGHT // 2 - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()