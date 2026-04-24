import pygame, random

pygame.init()
WIDTH, HEIGHT = 700, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("04 - Collision Detection")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 24)

class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 15))
        self.image.fill("black")
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.y = random.randrange(-300, -20)
        self.rect.x = random.randrange(WIDTH - 20)

    def update(self):
        self.rect.y += 3
        if self.rect.top > HEIGHT:
            self.reset_position()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 15))
        self.image.fill("red")
        self.rect = self.image.get_rect()

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.x, self.rect.y = pos

block_group = pygame.sprite.Group()
for _ in range(50):
    b = Block()
    b.rect.x = random.randrange(WIDTH)
    b.rect.y = random.randrange(HEIGHT)
    block_group.add(b)

player = Player()
all_sprites = pygame.sprite.Group(block_group, player)

score = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    hit_list = pygame.sprite.spritecollide(player, block_group, True)
    for block in hit_list:
        block.reset_position()
        score += 1

    screen.fill("white")
    all_sprites.draw(screen)
    score_text = font.render(f"Score: {score}", True, "black")
    screen.blit(score_text, (10, 10))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
