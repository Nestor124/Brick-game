import pygame
import random
import sys

# Ініціалізація
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Дожени мене, кирпич!")
clock = pygame.time.Clock()

# Завантаження зображень
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player1_img = pygame.transform.scale(pygame.image.load("player1.png"), (125, 125))
player2_img = pygame.transform.scale(pygame.image.load("player2.png"), (125, 125))

brick_img = pygame.image.load("brick.png")
brick_img = pygame.transform.scale(brick_img, (30, 30))

# Завантаження звуків
throw_sound = pygame.mixer.Sound("nabrasyivanie-lasso-vokrug-tseli.wav")
hit_sound = pygame.mixer.Sound("bol-ot-udara.wav")

font = pygame.font.SysFont("Arial", 32)
big_font = pygame.font.SysFont("Arial", 48)

# Гравці
player1 = pygame.Rect(100, HEIGHT - 200, 80, 80)
player2 = pygame.Rect(650, HEIGHT - 200, 80, 80)
speed = 5

# Кирпич
brick = pygame.Rect(0, 0, 30, 30)
brick_active = False
brick_speed = 10

# Кнопки
dodge_button = pygame.Rect(WIDTH//2 - 75, HEIGHT - 60, 150, 50)

# Гра
rounds = 7
score = 0
current_round = 1
player_turn = 1

# Стан ухилення
dodged = False
can_dodge = False
dodge_timer = 0
DODGE_DURATION = 60

# Здоров'я
player1_health = 100
player2_health = 100
HEALTH_BAR_WIDTH = 100

# Прапор кінця гри
game_over = False

# Анімація ухилення
player1_dodging = False
player1_returning = False
player2_dodging = False
player2_returning = False

# Бот ухилення
bot_should_dodge = False

def reset_round():
    global brick_active, dodged, can_dodge, dodge_timer
    global player1_dodging, player1_returning
    global player2_dodging, player2_returning
    global bot_should_dodge

    player1.x = 100
    player1.y = HEIGHT - 200
    player2.x = 650
    player2.y = HEIGHT - 200
    brick.x = player2.centerx if player_turn == 2 else player1.centerx
    brick.y = player2.centery if player_turn == 2 else player1.centery
    brick_active = False
    dodged = False
    can_dodge = False
    dodge_timer = 0
    player1_dodging = False
    player1_returning = False
    player2_dodging = False
    player2_returning = False
    bot_should_dodge = False

    if player_turn == 2:
        pygame.time.set_timer(pygame.USEREVENT, 1000)

def show_text(text, size, y_offset=0, color=(255,255,255)):
    render = pygame.font.SysFont("Arial", size).render(text, True, color)
    rect = render.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))
    screen.blit(render, rect)

def draw_health_bar(x, y, health):
    pygame.draw.rect(screen, (255, 0, 0), (x, y, HEALTH_BAR_WIDTH, 10))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, max(0, health), 10))

def draw_game():
    screen.blit(background, (0, 0))
    screen.blit(player1_img, player1)
    screen.blit(player2_img, player2)
    if brick_active:
        screen.blit(brick_img, brick)

    info = f"Попадання: {score} | Раунд: {current_round}/{rounds}"
    screen.blit(font.render(info, True, (255,255,255)), (20, 20))

    draw_health_bar(player1.x, player1.y - 15, player1_health)
    draw_health_bar(player2.x, player2.y - 15, player2_health)

    if not game_over and current_round <= rounds and player1_health > 0 and player2_health > 0:
        if player_turn == 1 and not brick_active:
            color = (200, 200, 200)
            show_text("Кинути - (пробіл)", 24, HEIGHT//2 - 220, color=color)

    if not game_over:
        if can_dodge and player_turn == 2:
            draw_dodge_button()

    if game_over:
        show_text("Гру завершено!", 48, -30)
        if player1_health <= 0:
            show_text("Тебе перемогли!", 36, 20)
        elif player2_health <= 0:
            show_text("Ти переміг!", 36, 20)
        else:
            show_text(f"Твій результат: {score} попадань", 36, 20)
        show_text("Натисни R, щоб почати знову", 28, 70)

def draw_dodge_button():
    pygame.draw.rect(screen, (0, 200, 100), dodge_button, border_radius=10)
    dodge_label = font.render("Ускочити", True, (255,255,255))
    screen.blit(dodge_label, dodge_label.get_rect(center=dodge_button.center))

def launch_brick():
    global brick_active, can_dodge, bot_should_dodge
    throw_sound.play()
    brick_active = True
    if player_turn == 2:
        can_dodge = True
    if player_turn == 1:
        # Бот має 30% шанс ухилитися
        if random.random() < 0.3:
            bot_should_dodge = True
            player2_dodging = True

def check_collision():
    global score, current_round, player_turn, brick_active, game_over
    global player1_health, player2_health
    global bot_should_dodge

    hit = False
    if player_turn == 1 and brick.colliderect(player2):
        if bot_should_dodge:
            pass  # бот ухилився
        else:
            hit = True
            player2_health -= 35
    elif player_turn == 2 and brick.colliderect(player1):
        if not dodged:
            hit = True
            player1_health -= 35

    if hit:
        hit_sound.play()
        score += 1

    current_round += 1
    brick_active = False
    bot_should_dodge = False

    if player1_health <= 0 or player2_health <= 0 or current_round > rounds:
        game_over = True
    else:
        player_turn = 2 if player_turn == 1 else 1
        reset_round()

reset_round()

# Головний цикл
running = True
while running:
    screen.fill((0,0,0))
    draw_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                current_round = 1
                score = 0
                player_turn = 1
                game_over = False
                player1_health = 100
                player2_health = 100
                reset_round()

        if player_turn == 2 and can_dodge:
            if event.type == pygame.MOUSEBUTTONDOWN and dodge_button.collidepoint(event.pos):
                dodged = True
                dodge_timer = DODGE_DURATION
                player1_dodging = True

        if event.type == pygame.USEREVENT:
            pygame.time.set_timer(pygame.USEREVENT, 0)
            launch_brick()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if player_turn == 1 and not brick_active and not game_over:
                launch_brick()

    keys = pygame.key.get_pressed()
    if not game_over:
        if player_turn == 1:
            if keys[pygame.K_w] and player1.top > 0:
                player1.y -= speed
            if keys[pygame.K_s] and player1.bottom < HEIGHT:
                player1.y += speed
        else:
            if keys[pygame.K_UP] and player2.top > 0:
                player2.y -= speed
            if keys[pygame.K_DOWN] and player2.bottom < HEIGHT:
                player2.y += speed

        if brick_active:
            dx = brick_speed if player_turn == 1 else -brick_speed
            brick.x += dx
            if brick.x < 0 or brick.x > WIDTH:
                check_collision()
            elif (player_turn == 1 and brick.colliderect(player2)) or (player_turn == 2 and brick.colliderect(player1)):
                check_collision()

    # --- Анімація ухилення гравців ---
    if player1_dodging:
        player1.x -= 5
        if player1.x <= 50:
            player1_dodging = False
            player1_returning = True

    if player1_returning:
        player1.x += 5
        if player1.x >= 100:
            player1.x = 100
            player1_returning = False

    if dodged:
        dodge_timer -= 1
        if dodge_timer <= 0:
            dodged = False
            player1.x = 100

    if player2_dodging:
        player2.x += 5
        if player2.x >= 720:
            player2_dodging = False
            player2_returning = True

    if player2_returning:
        player2.x -= 5
        if player2.x <= 650:
            player2.x = 650
            player2_returning = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
