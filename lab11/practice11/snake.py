import pygame, random, sys, time

pygame.init()
WIDTH, HEIGHT = 600, 600
CELL = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

snake = [(WIDTH//2, HEIGHT//2)]
direction = (CELL, 0)
foods = []
score = 0
level = 1
speed = 10

font = pygame.font.SysFont("Verdana", 20)

class Food:
    def __init__(self, snake):
        self.weight = random.choice([1, 2, 5])   # вес еды
        self.pos = (random.randrange(0, WIDTH, CELL),
                    random.randrange(0, HEIGHT, CELL))
        while self.pos in snake:                 # еда не на змее
            self.pos = (random.randrange(0, WIDTH, CELL),
                        random.randrange(0, HEIGHT, CELL))
        self.spawn_time = time.time()

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

    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # проверка выхода за границу
    if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
        running = False

    snake.insert(0, new_head)

    # генерация еды
    if random.randint(1, 30) == 1:
        foods.append(Food(snake))

    ate_food = None
    for food in foods[:]:
        if new_head == food.pos:
            score += food.weight
            ate_food = food.weight
            foods.remove(food)
            if score % 3 == 0:
                level += 1
                speed += 2
        elif time.time() - food.spawn_time > 5:
            foods.remove(food)

    # если еду не съели — удаляем хвост
    if not ate_food:
        snake.pop()
    else:
        # если еда весом >1, добавляем дополнительные сегменты
        for _ in range(ate_food - 1):
            snake.append(snake[-1])  # удлиняем хвост

    # проверка столкновения с собой
    if new_head in snake[1:]:
        running = False

    # отрисовка
    screen.fill((0,0,0))
    for seg in snake:
        pygame.draw.rect(screen, (0,255,0), (*seg, CELL, CELL))
    for food in foods:
        if food.weight == 1: color = (255,255,0)   # жёлтая
        elif food.weight == 2: color = (0,255,255) # голубая
        else: color = (255,0,0)                    # красная
        pygame.draw.rect(screen, color, (*food.pos, CELL, CELL))

    text = font.render(f"Score: {score}  Level: {level}", True, (255,255,255))
    screen.blit(text, (10,10))

    pygame.display.flip()
    clock.tick(speed)

pygame.quit()
