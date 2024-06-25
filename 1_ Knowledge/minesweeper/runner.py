from minesweeper import Minesweeper, MinesweeperAI
import pygame
import sys
import time


def command_prompt():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Cs50 Minesweeper game and AI")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="shows color for what ai thinks is safe/mine. RED=Mine, Green=Safe.")
    parser.epilog = """Argparse and Debugger by @IAMAJAYPRO.
    @IAMAJAYPRO also added color differences(the game looks better)"""
    dims_gp = parser.add_mutually_exclusive_group()
    dims_gp.add_argument("--dim", '--dimensions', nargs=2, type=int,
                         metavar=('HEIGHT', 'WIDTH'), help="Specify height and width.")
    dims_gp.add_argument('--square', "--size", default=8, type=int, metavar='SIZE',
                         help="Specify the size for both height and width.")
    parser.add_argument("--mines", type=int, default=8,
                        metavar="N_mines", help="number of mines, default 8")
    exp_gp = parser.add_mutually_exclusive_group()
    exp_gp.add_argument('-e', "--expand", action='store_true', default=True,
                        help='Expand the 0 neighbours chain')
    exp_gp.add_argument('-E', action='store_false', dest='expand',
                        help='Do not expand the 0 neighbours chain')
    args = parser.parse_args()
    return args


args = command_prompt()
DEBUG = args.debug
DOES_EXPAND = args.expand

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)  # unused


HEIGHT = args.dim[0] if args.dim else args.square
WIDTH = args.dim[1] if args.dim else args.square
MINES = args.mines

BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
REVD_COLOR0 = (230,)*3  # revealed
REVD_COLOR1 = (240,)*3

if MINES > HEIGHT*WIDTH:
    quit(f"    Error: No. of mines should be more than no. of available spaces({
         HEIGHT*WIDTH}).")
# Colors

# Create game
pygame.init()
size = width, height = 600, 400
screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))

# Create game and AI agent
game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
lost = False


def make_move(move: tuple[int, int], game: Minesweeper, ai: MinesweeperAI):
    """make move and open all near squares"""
    i, j = move
    nearby = game.nearby_mines(move)
    revealed.add(move)
    ai.add_knowledge(move, nearby)
    if DOES_EXPAND and nearby == 0:
        for h in range(-1+i, 2+i):
            if not (0 <= h < game.height):
                continue
            for k in range(-1+j, 2+j):
                if not (0 <= k < game.width):
                    continue
                cell = h, k
                if cell not in revealed:
                    make_move(cell, game, ai)


                # Show instructions initially
instructions = True

while True:

    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLACK)

    # Show game instructions
    if instructions:

        # Title
        title = largeFont.render("Play Minesweeper", True, WHITE)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)

        # Rules
        rules = [
            "Click a cell to reveal it.",
            "Right-click a cell to mark it as a mine.",
            "Mark all mines successfully to win!"
        ]
        for i, rule in enumerate(rules):
            line = smallFont.render(rule, True, WHITE)
            lineRect = line.get_rect()
            lineRect.center = ((width / 2), 150 + 30 * i)
            screen.blit(line, lineRect)

        # Play game button
        buttonRect = pygame.Rect((width / 4), (3 / 4) * height, width / 2, 50)
        buttonText = mediumFont.render("Play Game", True, BLACK)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = buttonRect.center
        pygame.draw.rect(screen, WHITE, buttonRect)
        screen.blit(buttonText, buttonTextRect)

        # Check if play button clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if buttonRect.collidepoint(mouse):
                instructions = False
                time.sleep(0.3)

        pygame.display.flip()
        continue

    # Draw board
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):
            cell = (i, j)
            cell_in_revealed = cell in revealed

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            bg = (REVD_COLOR0 if (i+j) %
                  2 else REVD_COLOR1) if cell_in_revealed else GRAY
            corner_color = (REVD_COLOR0 if (i+j) %
                            2 else REVD_COLOR1) if cell_in_revealed else WHITE
            pygame.draw.rect(screen, bg, rect)
            if not cell_in_revealed:
                if DEBUG and cell in ai.safes:
                    pygame.draw.rect(screen, GREEN, rect, 3)
                elif DEBUG and cell in ai.mines:
                    pygame.draw.rect(screen, RED, rect, 3)
                else:
                    pygame.draw.rect(screen, corner_color, rect, 3)
            # Add a mine, flag, or number if needed
            if game.is_mine((i, j)) and lost:
                screen.blit(mine, rect)
            elif cell in flags:
                screen.blit(flag, rect)
            elif cell_in_revealed:
                near_mines = game.nearby_mines(cell)
                neighbors = smallFont.render(
                    str(near_mines if near_mines != 0 else ""),
                    True, BLACK
                )
                neighborsTextRect = neighbors.get_rect()
                neighborsTextRect.center = rect.center
                screen.blit(neighbors, neighborsTextRect)

            row.append(rect)
        cells.append(row)

    # AI Move button
    aiButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height - 50,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("AI Move", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    pygame.draw.rect(screen, WHITE, aiButton)
    screen.blit(buttonText, buttonRect)

    # Reset button
    resetButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 20,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("Reset", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    pygame.draw.rect(screen, WHITE, resetButton)
    screen.blit(buttonText, buttonRect)
    # bit.ly/encrypted_credits
    # Display text
    text = "Lost" if lost else "Won" if game.mines == flags else ""
    text = mediumFont.render(text, True, WHITE)
    textRect = text.get_rect()
    textRect.center = ((5 / 6) * width, (2 / 3) * height)
    screen.blit(text, textRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    # Check for a right-click to toggle flagging
    if right == 1 and not lost:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    if (i, j) in flags:
                        flags.remove((i, j))
                    else:
                        flags.add((i, j))
                    time.sleep(0.2)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        # If AI button clicked, make an AI move
        if aiButton.collidepoint(mouse) and not lost:
            move = ai.make_safe_move()
            if move is None:
                move = ai.make_random_move()
                if move is None:
                    flags = ai.mines.copy()
                    print("No moves left to make.")
                else:
                    print(
                        f"No known safe moves, AI making random move {move}.")
            else:
                print(f"AI making safe move {move}.")
            time.sleep(0.2)

        # Reset game state
        elif resetButton.collidepoint(mouse):
            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
            revealed = set()
            flags = set()
            lost = False
            continue

        # User-made move
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    # Make move and update AI knowledge
    if move:
        if game.is_mine(move):
            lost = True
        else:
            make_move(move, game, ai)

    pygame.display.flip()
