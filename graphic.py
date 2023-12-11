import pygame

# Define cell properties
CELL_SIZE = 50
CELL_PADDING = 5

# Custom colors for input and clue cells
INPUT_CELL_COLOR = (255, 255, 255)  # White
CLUE_CELL_COLOR = (0, 0, 0)  # Black
TEXT_COLOR = (255, 255, 255)  # White
BACK_COLOR = (128, 128, 128)  # GRAY

matrix = [
    ["X", "X", "11\\", "5\\", "X", "15\\", "15\\", "X"],
    ["X", "3\\3", "", "", "4\\17", "", "", "X"],
    ["\\22", "", "", "", "", "", "", "X"],
    ["\\3", "", "", "11\\4", "", "", "10\\", "X"],
    ["X", "\\8", "", "", "7\\3", "", "", "8\\"],
    ["X", "X", "4\\4", "", "", "3\\4", "", ""],
    ["X", "\\21", "", "", "", "", "", ""],
    ["X", "\\3", "", "", "\\4", "", "", "X"],
]

# Function to create a Kakuro cell
def create_kakuro_cell(row, col, screen, value=None):
    cell_x = col * (CELL_SIZE + CELL_PADDING)
    cell_y = row * (CELL_SIZE + CELL_PADDING)

    cell_size = CELL_SIZE
    font = pygame.font.Font(None, 24)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    if isinstance(value, int):
        pygame.draw.rect(screen, WHITE, (cell_x, cell_y, cell_size, cell_size))
        text = font.render(str(value), True, BLACK)
        text_rect = text.get_rect(
            center=(cell_x + cell_size // 2, cell_y + cell_size // 2)
        )
        screen.blit(text, text_rect)
    elif isinstance(value, str) and "\\" in value:
        pygame.draw.rect(screen, BLACK, (cell_x, cell_y, cell_size, cell_size))
        parts = value.split("\\")
        text1 = font.render(parts[0], True, WHITE)
        text2 = font.render(parts[1], True, WHITE)
        text1_rect = text1.get_rect(
            center=(cell_x + cell_size // 4, cell_y + cell_size // 2 + cell_size // 4)
        )
        text2_rect = text2.get_rect(
            center=(
                cell_x + 3 * cell_size // 4,
                cell_y + cell_size // 2 - cell_size // 4,
            )
        )
        pygame.draw.line(
            screen, WHITE, (cell_x, cell_y), (cell_x + cell_size, cell_y + cell_size), 2
        )
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)
    elif value == "X":
        pygame.draw.rect(screen, BLACK, (cell_x, cell_y, cell_size, cell_size))
    else:
        pygame.draw.rect(screen, WHITE, (cell_x, cell_y, cell_size, cell_size))
        text = font.render(str(value), True, BLACK)
        text_rect = text.get_rect(
            center=(cell_x + cell_size // 2, cell_y + cell_size // 2)
        )
        screen.blit(text, text_rect)


# Create the Kakuro grid
def graphic(k):
    # Initialize Pygame
    pygame.init()
    # Define board size
    BOARD_SIZE = len(k.board)

    # Define board size
    BOARD_SIZE = len(k.board)

    # Create the main window
    window = pygame.display.set_mode(
        (
            (CELL_SIZE + CELL_PADDING) * BOARD_SIZE,
            (CELL_SIZE + CELL_PADDING) * BOARD_SIZE,
        )
    )
    pygame.display.set_caption("Kakuro Board")
    window.fill((128, 128, 128))

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        for row in range(len(k.board)):
            for col in range(len(k.board[0])):
                value = k.board[row][col]

                create_kakuro_cell(row, col, window, value=value)
                pygame.display.flip()

    pygame.quit()
