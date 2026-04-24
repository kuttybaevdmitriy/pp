import pygame, random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("02 - Sprite Groups")
clock = pygame.time.Clock()

class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(4, 12)
        self.image = pygame.Surface((size, size))
        self.image.fill("white")
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(0, HEIGHT)
        self.speed = random.randint(1, 4)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
            self.rect.x = random.randint(0, WIDTH)

stars = pygame.sprite.Group()
for _ in range(60):
    stars.add(Star())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    stars.update()
    screen.fill("black")
    stars.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
