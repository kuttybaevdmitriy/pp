import pygame, sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    color = (0, 0, 255)
    mode = "brush"
    start_pos = None
    font = pygame.font.SysFont("Verdana", 16)

    screen.fill((255,255,255))  # белый фон

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                # выбор цвета
                if event.key == pygame.K_r: color = (255, 0, 0)
                if event.key == pygame.K_g: color = (0, 255, 0)
                if event.key == pygame.K_b: color = (0, 0, 255)
                if event.key == pygame.K_y: color = (255, 255, 0)

                # выбор режима
                if event.key == pygame.K_1: mode = "brush"
                if event.key == pygame.K_2: mode = "rect"
                if event.key == pygame.K_3: mode = "circle"
                if event.key == pygame.K_4: mode = "square"
                if event.key == pygame.K_5: mode = "right_triangle"
                if event.key == pygame.K_6: mode = "equilateral_triangle"
                if event.key == pygame.K_7: mode = "rhombus"
                if event.key == pygame.K_8: mode = "eraser"

            if event.type == pygame.MOUSEBUTTONDOWN:
                start_pos = event.pos
                if mode == "brush":
                    pygame.draw.circle(screen, color, event.pos, 5)
                elif mode == "eraser":
                    pygame.draw.circle(screen, (255,255,255), event.pos, 10)

            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                if mode == "brush":
                    pygame.draw.circle(screen, color, event.pos, 5)
                elif mode == "eraser":
                    pygame.draw.circle(screen, (255,255,255), event.pos, 10)

            if event.type == pygame.MOUSEBUTTONUP and start_pos:
                end_pos = event.pos
                x1, y1 = start_pos
                x2, y2 = end_pos

                if mode == "rect":
                    rect = pygame.Rect(x1, y1, x2-x1, y2-y1)
                    pygame.draw.rect(screen, color, rect, 2)

                elif mode == "circle":
                    dx, dy = x2-x1, y2-y1
                    radius = int((dx**2 + dy**2)**0.5)
                    pygame.draw.circle(screen, color, start_pos, radius, 2)

                elif mode == "square":
                    side = min(abs(x2-x1), abs(y2-y1))
                    rect = pygame.Rect(x1, y1, side, side)
                    pygame.draw.rect(screen, color, rect, 2)

                elif mode == "right_triangle":
                    points = [(x1,y1), (x1,y2), (x2,y2)]
                    pygame.draw.polygon(screen, color, points, 2)

                elif mode == "equilateral_triangle":
                    side = abs(x2-x1)
                    height = int((3**0.5/2)*side)
                    points = [(x1,y2), (x1+side,y2), (x1+side//2,y2-height)]
                    pygame.draw.polygon(screen, color, points, 2)

                elif mode == "rhombus":
                    dx = abs(x2-x1)//2
                    dy = abs(y2-y1)//2
                    points = [(x1+dx,y1), (x2,y1+dy), (x1+dx,y2), (x1,y1+dy)]
                    pygame.draw.polygon(screen, color, points, 2)

                start_pos = None

        # подсказки
        help_text = [
            "1 - Кисть",
            "2 - Прямоугольник",
            "3 - Круг",
            "4 - Квадрат",
            "5 - Прямоугольный треугольник",
            "6 - Равносторонний треугольник",
            "7 - Ромб",
            "8 - Ластик",
            "R/G/B/Y - Цвет"
        ]
        y = 5
        for line in help_text:
            surf = font.render(line, True, (0,0,0))
            screen.blit(surf, (5,y))
            y += 20

        pygame.display.flip()
        clock.tick(60)

main()
