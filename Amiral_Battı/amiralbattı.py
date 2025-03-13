import pygame
import time
from random import randint, choice

# Oyun tahtası ayarları
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
CELL_SIZE = 50
GRID_SIZE = SCREEN_HEIGHT // CELL_SIZE

# Renkler
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Pygame başlatma
pygame.init()

# Dinamik çözünürlük algılama (Tam ekran çözünürlüğü al)
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Tam ekran modu
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Amiral Battı")
font = pygame.font.Font(None, 74)

# Görsel yükleme ve yeniden boyutlandırma
background_image = pygame.image.load("arkaplan2.png")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Gemiler için görseller
directions = ["sağ", "sol", "aşağı", "yukarı"]
ship_images = {
    f"ship1{direction}": pygame.image.load(f"ship1{direction}.png") for direction in directions
}
ship_images.update({
    f"ship2{direction}": pygame.image.load(f"ship2{direction}.png") for direction in directions
})
ship_images.update({
    f"ship3{direction}": pygame.image.load(f"ship3{direction}.png") for direction in directions
})

# Gemileri hücre boyutlarına ölçeklendir
for ship_type in ship_images:
    ship_images[ship_type] = pygame.transform.scale(ship_images[ship_type], (CELL_SIZE, CELL_SIZE))

fire_effect = pygame.image.load("Fire-Ball.png")
fire_effect = pygame.transform.scale(fire_effect, (CELL_SIZE, CELL_SIZE))

miss_effect = pygame.image.load("Red-Cross.png")
miss_effect = pygame.transform.scale(miss_effect, (CELL_SIZE, CELL_SIZE))


# Ses efektlerini yükleme
explosion_sound = pygame.mixer.Sound('explosion.wav')  # Vuruş sesi
water_sound = pygame.mixer.Sound('water.wav')  # Iskalanma sesi


# Tahta oluşturma
def create_board(size):
    return [["O"] * size for _ in range(size)]


# Gemi yerleştirme
def place_ship(board, ship_size, ship_type):
    while True:
        direction = choice(["sağ", "aşağı"])  # Yalnızca sağ ve aşağı yönüyle yerleştir
        row, col = randint(0, GRID_SIZE - 1), randint(0, GRID_SIZE - 1)

        if direction == "sağ" and col + ship_size <= GRID_SIZE:
            if all(board[row][col + i] == "O" for i in range(ship_size)):
                for i in range(ship_size):
                    board[row][col + i] = ship_type + direction
                break
        elif direction == "aşağı" and row + ship_size <= GRID_SIZE:
            if all(board[row + i][col] == "O" for i in range(ship_size)):
                for i in range(ship_size):
                    board[row + i][col] = ship_type + direction
                break


# Tahtayı çizme
def draw_board(board, offset_x, show_ships=False):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                offset_x + col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
            if board[row][col] == "X":
                screen.blit(fire_effect, rect.topleft)  # Ateş efekti
            elif board[row][col] == "-":
                screen.blit(miss_effect, rect.topleft)  # Iskalandı
            elif show_ships and board[row][col] != "O":
                ship_type = board[row][col]
                screen.blit(ship_images[ship_type], rect.topleft)
            pygame.draw.rect(screen, GRAY, rect, 1)


# Ayırıcı çizgi
def draw_separator():
    pygame.draw.line(
        screen, BLACK, (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 3
    )


# Hamle kontrolü
def make_move(board, row, col):
    if board[row][col] != "O" and board[row][col] not in ["X", "-"]:
        board[row][col] = "X"  # İsabet
        explosion_sound.play()  # Vuruş sesi çal
        return True
    elif board[row][col] == "O":
        board[row][col] = "-"  # Iskalandı
        water_sound.play()  # Iskalanma sesi çal
        return False


# Bilgisayarın rastgele hamlesi
def computer_move(board):
    while True:
        row = randint(0, GRID_SIZE - 1)
        col = randint(0, GRID_SIZE - 1)
        if board[row][col] in ["O", "ship1sağ", "ship2sağ", "ship3sağ"]:
            return row, col


# Kazanma durumu kontrolü
def check_victory(board):
    return all(cell in ["O", "X", "-"] for row in board for cell in row)


# Mesaj gösterme
def show_message(message, color):
    text = font.render(message, True, color)
    screen.blit(text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 50))
    pygame.display.flip()
    time.sleep(3)


# Ana oyun
def play_game():
    player_board = create_board(GRID_SIZE)
    computer_board = create_board(GRID_SIZE)

    # Gemileri yerleştir
    for ship_size, ship_type, count in [
        (2, "ship1", 3),
        (3, "ship2", 2),
        (4, "ship3", 1),
    ]:
        for _ in range(count):
            place_ship(player_board, ship_size, ship_type)
            place_ship(computer_board, ship_size, ship_type)

    running = True
    player_turn = True

    while running:
        screen.blit(background_image, (0, 0))

        draw_board(player_board, offset_x=0, show_ships=True)
        draw_separator()
        draw_board(computer_board, offset_x=SCREEN_WIDTH // 2, show_ships=False)

        pygame.display.flip()

        if player_turn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pos[0] < SCREEN_WIDTH // 2:
                        continue
                    col = (pos[0] - SCREEN_WIDTH // 2) // CELL_SIZE
                    row = pos[1] // CELL_SIZE

                    if computer_board[row][col] in ["X", "-"]:
                        continue

                    hit = make_move(computer_board, row, col)
                    if hit:
                        print("Vurdunuz!")
                    else:
                        print("Iskalandı!")

                    if check_victory(computer_board):
                        show_message("Kazandınız!", YELLOW)
                        running = False

                    player_turn = False
        else:
            row, col = computer_move(player_board)
            hit = make_move(player_board, row, col)
            if hit:
                print(f"Bilgisayar vurdu: ({row}, {col})")
            else:
                print(f"Bilgisayar ıskaladı: ({row}, {col})")

            if check_victory(player_board):
                show_message("Kaybettiniz!", RED)
                running = False

            player_turn = True

    pygame.quit()


play_game()
