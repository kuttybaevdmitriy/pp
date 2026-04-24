import pygame, sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    radius = 5
    color = (0, 0, 255)
    mode = "brush"
    start_pos = None

    font = pygame.font.SysFont("Verdana", 16)

    # фон закрашиваем один раз
    screen.fill((0,0,0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: color = (255, 0, 0)
                if event.key == pygame.K_g: color = (0, 255, 0)
                if event.key == pygame.K_b: color = (0, 0, 255)
                if event.key == pygame.K_y: color = (255, 255, 0)

                if event.key == pygame.K_1: mode = "brush"
                if event.key == pygame.K_2: mode = "rect"
                if event.key == pygame.K_3: mode = "circle"
                if event.key == pygame.K_4: mode = "eraser"

            if event.type == pygame.MOUSEBUTTONDOWN:
                start_pos = event.pos
                if mode == "brush":
                    pygame.draw.circle(screen, color, event.pos, radius)
                elif mode == "eraser":
                    pygame.draw.circle(screen, (0,0,0), event.pos, radius)

            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                if mode == "brush":
                    pygame.draw.circle(screen, color, event.pos, radius)
                elif mode == "eraser":
                    pygame.draw.circle(screen, (0,0,0), event.pos, radius)

            if event.type == pygame.MOUSEBUTTONUP and start_pos:
                end_pos = event.pos
                if mode == "rect":
                    rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    pygame.draw.rect(screen, color, rect, 2)
                elif mode == "circle":
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    radius_circle = int((dx**2 + dy**2)**0.5)
                    pygame.draw.circle(screen, color, start_pos, radius_circle, 2)
                start_pos = None

        # подсказки рисуем поверх
        help_text = [
            "1 - Кисть",
            "2 - Прямоугольник",
            "3 - Круг",
            "4 - Ластик",
            "R/G/B/Y - Цвет",
            "ESC - Выход"
        ]
        y = 5
        for line in help_text:
            surf = font.render(line, True, (200,200,200))
            screen.blit(surf, (5,y))
            y += 20

        pygame.display.flip()
        clock.tick(60)

main()
