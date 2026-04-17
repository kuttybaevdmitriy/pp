import pygame
from ball import Ball

pygame.init()
width, height = 400, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Moving Ball Game")

ball = Ball(width//2, height//2)
clock = pygame.time.Clock()

run = True
while run:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False
        if e.type == pygame.KEYDOWN:
            ball.move(e.key, width, height)

    screen.fill((255,255,255))   # белый фон
    ball.draw(screen)            # рисуем шар
    pygame.display.flip()
    clock.tick(30)               # плавная анимация

pygame.quit()