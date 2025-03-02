import pygame
import chess
import chess.engine
import time
import random

STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

ELO_LIST = [1800 + (i * 100) for i in range(11)]
FIXED_ELO = 2500  # Bot cố định

BOARD_SIZE = 600
SQUARE_SIZE = BOARD_SIZE // 8
WHITE = (255, 255, 255)
GREEN_YELLOW = (173, 255, 47)  # Xanh chuối
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
pygame.display.set_caption("NgNghia Chess")

pieces = {}
piece_files = {
    "p": "p.svg", "r": "r.svg", "n": "n.svg", "b": "b.png", "q": "q.svg", "k": "k.svg",
    "P": "wP.svg", "R": "wR.svg", "N": "wN.svg", "B": "wB.svg", "Q": "wQ.svg", "K": "wK.svg"
}

for piece, filename in piece_files.items():
    pieces[piece] = pygame.image.load(f"../images/{filename}")
    pieces[piece] = pygame.transform.scale(pieces[piece], (SQUARE_SIZE, SQUARE_SIZE))

pygame.font.init()
font = pygame.font.SysFont("Arial", 24, bold=True)

fullscreen = False


def get_board_position():
    screen_width, screen_height = pygame.display.get_surface().get_size()
    board_x = (screen_width - BOARD_SIZE) // 2
    board_y = (screen_height - BOARD_SIZE) // 2
    return board_x, board_y


def draw_board():
    board_x, board_y = get_board_position()
    colors = [WHITE, GREEN_YELLOW]
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            rect = pygame.Rect(board_x + col * SQUARE_SIZE, board_y + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)


def draw_pieces(board):
    board_x, board_y = get_board_position()
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            x = board_x + (square % 8) * SQUARE_SIZE
            y = board_y + (7 - (square // 8)) * SQUARE_SIZE
            screen.blit(pieces[piece.symbol()], (x, y))


# def draw_elo(fixed_elo, opponent_elo, fixed_elo_white):
#     screen_width, _ = pygame.display.get_surface().get_size()
#     text_x = (screen_width - BOARD_SIZE) // 2 + 20
#     if fixed_elo_white:
#         elo_text_1 = font.render(f"Bot 1 (White): {fixed_elo} ELO", True, RED)
#         elo_text_2 = font.render(f"Bot 2 (Black): {opponent_elo} ELO", True, RED)
#     else:
#         elo_text_1 = font.render(f"Bot 1 (Black): {fixed_elo} ELO", True, RED)
#         elo_text_2 = font.render(f"Bot 2 (White): {opponent_elo} ELO", True, RED)
#
#     screen.blit(elo_text_1, (text_x, 10))
#     screen.blit(elo_text_2, (text_x, BOARD_SIZE - 30))


def play_game(fixed_elo, opponent_elo, fixed_elo_white):
    global fullscreen, screen
    board = chess.Board()

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        engine.configure({"UCI_LimitStrength": True, "UCI_Elo": fixed_elo})
        engine2 = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        engine2.configure({"UCI_LimitStrength": True, "UCI_Elo": opponent_elo})

        running = True
        while running and not board.is_game_over():
            draw_board()
            draw_pieces(board)
            # draw_elo(fixed_elo, opponent_elo, fixed_elo_white)
            pygame.display.flip()
            time.sleep(0.5)

            if (board.turn and fixed_elo_white) or (not board.turn and not fixed_elo_white):
                move = engine.play(board, chess.engine.Limit(time=5)).move
            else:
                move = engine2.play(board, chess.engine.Limit(time=5)).move

            board.push(move)

            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))

        print(f"Trận đấu giữa bot {fixed_elo} vs bot {opponent_elo} kết thúc! Kết quả: {board.result()}")
        engine2.quit()


fixed_elo_white = True

while True:
    # opponent_elo = random.choice([elo for elo in ELO_LIST if elo != FIXED_ELO])
    # print(
    #     f"--- Bắt đầu trận đấu giữa bot {FIXED_ELO} {'(White)' if fixed_elo_white else '(Black)'} và bot {opponent_elo} {'(Black)' if fixed_elo_white else '(White)'} ---")

    # play_game(FIXED_ELO, opponent_elo, fixed_elo_white)
    # fixed_elo_white = not fixed_elo_white
    # print("Chờ 2 phút trước trận tiếp theo...\n")
    # time.sleep(120)
    while True:
        opponent_elo = random.choices(
            [elo for elo in ELO_LIST if elo != FIXED_ELO],
            weights=[10] * 10,
            k=1
        )[0]

        print(
            f"--- Bắt đầu trận đấu giữa bot {FIXED_ELO} {'(White)' if fixed_elo_white else '(Black)'} và bot {opponent_elo} {'(Black)' if fixed_elo_white else '(White)'} ---")

        play_game(FIXED_ELO, opponent_elo, fixed_elo_white)

        fixed_elo_white = not fixed_elo_white
        print("Chờ 2 phút trước trận tiếp theo...\n")
        time.sleep(120)
