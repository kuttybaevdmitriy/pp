import pygame, sys
from clock import MickeyClock

pygame.init()
screen = pygame.display.set_mode((1000, 950))
pygame.display.set_caption("Mickey's Clock")

center = (450, 450)

clock = MickeyClock(
    screen,
    "images/body.png",
    "images/right_hand.png",
    "images/left_hand.png",
    center
)
running = True
timer = pygame.time.Clock()

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    clock.draw()
    pygame.display.flip()
    timer.tick(1)  # обновляем каждую секунду

pygame.quit()
sys.exit()