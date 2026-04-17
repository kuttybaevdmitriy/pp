import pygame

class Ball:
    def __init__(self, x, y, radius=25, color=(255,0,0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.step = 20

    def move(self, key, width, height):
        if key == pygame.K_UP and self.y - self.step - self.radius >= 0:
            self.y -= self.step
        if key == pygame.K_DOWN and self.y + self.step + self.radius <= height:
            self.y += self.step
        if key == pygame.K_LEFT and self.x - self.step - self.radius >= 0:
            self.x -= self.step
        if key == pygame.K_RIGHT and self.x + self.step + self.radius <= width:
            self.x += self.step

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)