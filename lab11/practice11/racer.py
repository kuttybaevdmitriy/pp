import pygame, random, sys, time

pygame.init()
screen = pygame.display.set_mode((1024, 1000))
WIDTH, HEIGHT = 1024, 1000
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()
FPS = 60

# --- Шрифты ---
font_big   = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)

# --- Картинки ---
image_background = pygame.image.load("resources/road.jpg")
image_player     = pygame.image.load("resources/car1.jpg")
image_enemy      = pygame.image.load("resources/car2.jpg")

# Масштабируем машины, если они слишком большие
max_width = WIDTH // 3
max_height = HEIGHT // 3
if image_player.get_width() > max_width or image_player.get_height() > max_height:
    image_player = pygame.transform.scale(image_player, (max_width, max_height))
if image_enemy.get_width() > max_width or image_enemy.get_height() > max_height:
    image_enemy = pygame.transform.scale(image_enemy, (max_width, max_height))

# --- Звуки ---
pygame.mixer.music.load("resources/background.mp3")
pygame.mixer.music.play(-1)
sound_crash = pygame.mixer.Sound("resources/crash.mp3")

# --- Игровые параметры ---
SPEED = 5
SCORE = 0
COINS = 0
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# --- Классы ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_player
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.move_ip(-self.speed, 0)
        if keys[pygame.K_RIGHT]:
            self.rect.move_ip(self.speed, 0)
        # Ограничения по краям экрана
        if self.rect.left < 0:      self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_enemy
        self.rect = self.image.get_rect()
        self._reset()

    def _reset(self):
        global SCORE
        SCORE += 1
        max_x = max(0, WIDTH - self.rect.width)
        self.rect.left = random.randint(0, max_x)
        self.rect.bottom = 0

    def update(self):
        self.rect.move_ip(0, SPEED)
        if self.rect.top > HEIGHT:
            self._reset()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # случайный вес монетки
        self.weight = random.choice([1, 2, 5])
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 215, 0))  # золотой цвет
        self.rect = self.image.get_rect(center=(random.randint(50, WIDTH-50), -20))

    def update(self):
        self.rect.y += 5
        if self.rect.top > HEIGHT:
            self.kill()

# --- Группы ---
player = Player()
enemy1 = Enemy()
enemy2 = Enemy()
enemy2.rect.bottom = -HEIGHT // 2   # второй враг стартует позже

all_sprites   = pygame.sprite.Group(player, enemy1, enemy2)
enemy_sprites = pygame.sprite.Group(enemy1, enemy2)
coin_sprites  = pygame.sprite.Group()

# --- Основной цикл ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == INC_SPEED:
            SPEED += 0.5

    # случайная генерация монет
    if random.randint(1, 50) == 1:
        coin_sprites.add(Coin())

    all_sprites.update()
    coin_sprites.update()

    # проверка столкновений с монетами
    for coin in coin_sprites:
        if player.rect.colliderect(coin.rect):
            COINS += coin.weight
            coin.kill()
            # ускоряем врагов каждые 10 монет
            if COINS % 10 == 0:
                SPEED += 1

    # --- Отрисовка ---
    screen.blit(image_background, (0, 0))
    all_sprites.draw(screen)
    coin_sprites.draw(screen)

    score_surf = font_small.render(
        f"Score: {int(SCORE)}   Coins: {COINS}   Speed: {SPEED:.1f}", True, "black"
    )
    screen.blit(score_surf, (10, 10))

    # --- Проверка столкновений с врагами ---
    if pygame.sprite.spritecollideany(player, enemy_sprites):
        sound_crash.play()
        time.sleep(1)
        screen.fill("red")
        go_surf = font_big.render("GAME OVER", True, "black")
        screen.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2,
                              HEIGHT//2 - go_surf.get_height()//2))
        pygame.display.flip()
        time.sleep(2)
        pygame.quit(); sys.exit()

    pygame.display.flip()
    clock.tick(FPS)
s