import pygame, random, sys

pygame.init()
WIDTH, HEIGHT = 600, 600
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

snake = [(WIDTH//2, HEIGHT//2)]
direction = (CELL, 0)
food = None
score = 0
level = 1
speed = 10

font = pygame.font.SysFont("Verdana", 20)

def new_food():
    while True:
        pos = (random.randrange(0, WIDTH, CELL), random.randrange(0, HEIGHT, CELL))
        if pos not in snake:  # еда не на змее
            return pos

food = new_food()

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]: direction = (0, -CELL)
    if keys[pygame.K_DOWN]: direction = (0, CELL)
    if keys[pygame.K_LEFT]: direction = (-CELL, 0)
    if keys[pygame.K_RIGHT]: direction = (CELL, 0)

    # движение змеи
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # проверка выхода за границу
    if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
        running = False

    snake.insert(0, new_head)

    # проверка еды
    if new_head == food:
        score += 1
        food = new_food()
        # уровень каждые 3 очка
        if score % 3 == 0:
            level += 1
            speed += 2
    else:
        snake.pop()

    # проверка столкновения с собой
    if new_head in snake[1:]:
        running = False

    # отрисовка
    screen.fill((0,0,0))
    for seg in snake:
        pygame.draw.rect(screen, (0,255,0), (*seg, CELL, CELL))
    pygame.draw.rect(screen, (255,0,0), (*food, CELL, CELL))

    text = font.render(f"Score: {score}  Level: {level}", True, (255,255,255))
    screen.blit(text, (10,10))

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()
