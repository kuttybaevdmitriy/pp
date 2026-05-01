import pygame
from datetime import datetime
import os

def flood_fill(surface, pos, fill_color):
    """
    Заливка области (как в Paint).
    Берём цвет в точке клика и заменяем его на новый.
    """
    target_color = surface.get_at(pos)
    
    # Если цвет совпадает с новым — смысла нет, выходим
    if target_color == surface.map_rgb(fill_color):
        return

    stack = [pos]  # список точек для проверки
    width, height = surface.get_size()
    fill_mapped = surface.map_rgb(fill_color)

    while stack:
        x, y = stack.pop()
        # проверяем границы и совпадение цвета
        if 0 <= x < width and 0 <= y < height:
            if surface.get_at((x, y)) == target_color:
                surface.set_at((x, y), fill_mapped)
                # добавляем соседей (вверх, вниз, влево, вправо)
                stack.append((x + 1, y))
                stack.append((x - 1, y))
                stack.append((x, y + 1))
                stack.append((x, y - 1))

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # canvas — постоянный холст, screen — слой для предпросмотра
    canvas = pygame.Surface((800, 600))
    canvas.fill((0, 0, 0))
    clock = pygame.time.Clock()
    
    # Настройка шрифта для текста
    font = pygame.font.SysFont(None, 36)
    
    radius = 5          # Толщина кисти
    color = (0, 0, 255) # Текущий цвет
    mode = 'pen'        # Текущий инструмент
    last_pos, start_pos = None, None
    drawing = False
    
    # Переменные для текстового инструмента
    typing = False
    text_input = ""
    text_pos = None

    print("=== КОНТРОЛЫ ===")
    print("Цвета: R, G, B, Y, W")
    print("Размер кисти: 1, 2, 3")
    print("Инструменты: P(Карандаш), L(Линия), F(Заливка), T(Текст), E(Ластик)")
    print("Фигуры: S(Прямоуг), C(Круг), 4(Квадрат), 5(Прям. треуг), 6(Равн. треуг), 7(Ромб)")
    print("Сохранение: Ctrl + S")
    print("================")

    while True:
        pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            # --- ОБРАБОТКА КЛАВИАТУРЫ ---
            if event.type == pygame.KEYDOWN:
                # Если вводим текст
                if typing:
                    if event.key == pygame.K_RETURN:
                        # Запекаем текст на холст
                        text_surface = font.render(text_input, True, color)
                        canvas.blit(text_surface, text_pos)
                        typing = False
                        text_input = ""
                    elif event.key == pygame.K_ESCAPE:
                        # Отмена ввода
                        typing = False
                        text_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    else:
                        text_input += event.unicode
                
                # Горячие клавиши и переключение инструментов
                else:
                    mods = pygame.key.get_mods()
                    # Сохранение с датой (Ctrl+S)
                    if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        filename = f"canvas_{timestamp}.png"
                        pygame.image.save(canvas, filename)
                        print(f"Сохранено: {filename}")
                        continue 

                    # Переключение цветов
                    if event.key == pygame.K_r: color = (255, 0, 0)
                    elif event.key == pygame.K_g: color = (0, 255, 0)
                    elif event.key == pygame.K_b: color = (0, 0, 255)
                    elif event.key == pygame.K_y: color = (255, 255, 0)
                    elif event.key == pygame.K_w: color = (255, 255, 255)
                    
                    # Размер кисти
                    elif event.key == pygame.K_1: radius = 2
                    elif event.key == pygame.K_2: radius = 5
                    elif event.key == pygame.K_3: radius = 10
                    
                    # Инструменты
                    elif event.key == pygame.K_p: mode = 'pen'
                    elif event.key == pygame.K_l: mode = 'line'
                    elif event.key == pygame.K_f: mode = 'fill'
                    elif event.key == pygame.K_t: mode = 'text'
                    elif event.key == pygame.K_s: mode = 'rect'
                    elif event.key == pygame.K_c: mode = 'circle'
                    elif event.key == pygame.K_e: mode = 'eraser'
                    elif event.key == pygame.K_4: mode = 'square'
                    elif event.key == pygame.K_5: mode = 'right_tri'
                    elif event.key == pygame.K_6: mode = 'eq_tri'
                    elif event.key == pygame.K_7: mode = 'rhombus'

            # --- НАЖАТИЕ МЫШИ ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # ЛКМ
                    if mode == 'fill':
                        flood_fill(canvas, event.pos, color)
                    elif mode == 'text':
                        # Если уже вводим текст и кликаем в другое место — запекаем старый
                        if typing:
                            text_surface = font.render(text_input, True, color)
                            canvas.blit(text_surface, text_pos)
                        typing = True
                        text_pos = event.pos
                        text_input = ""
                    else:
                        # Для фигур/линий запоминаем стартовую точку
                        drawing = True
                        start_pos = event.pos 
                        
                # Колёсико мыши — динамическая смена размера кисти
                elif event.button == 4: radius = min(100, radius + 2)
                elif event.button == 5: radius = max(2, radius - 2)
            
            # --- ОТПУСКАНИЕ МЫШИ ---
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    drawing = False
                    # Рисуем финальную фигуру на холсте
                    if mode == 'rect': draw_rect(canvas, start_pos, event.pos, radius, color)
                    elif mode == 'circle': draw_circle(canvas, start_pos, event.pos, radius, color)
                    elif mode == 'square': draw_square(canvas, start_pos, event.pos, radius, color)
                    elif mode == 'right_tri': draw_right_triangle(canvas, start_pos, event.pos, radius, color)
                    elif mode == 'eq_tri': draw_equilateral_triangle(canvas, start_pos, event.pos, radius, color)
                    elif mode == 'rhombus': draw_rhombus(canvas, start_pos, event.pos, radius, color)
                    elif mode == 'line': pygame.draw.line(canvas, color, start_pos, event.pos, radius)
                    
                    start_pos = None
                last_pos = None

        # --- НЕПРЕРЫВНОЕ РИСОВАНИЕ (карандаш/ластик) ---
        if drawing:
            if mode == 'pen' and last_pos is not None:
                draw_line(canvas, last_pos, pos, radius, color)
            elif mode == 'eraser' and last_pos is not None:
                draw_line(canvas, last_pos, pos, radius, (0, 0, 0)) 
            last_pos = pos

        # --- ОТОБРАЖЕНИЕ ---
        screen.blit(canvas, (0, 0))  # постоянный холст
        
        # Предпросмотр фигуры (только на экране)
        if drawing and start_pos is not None:
            if mode == 'rect': draw_rect(screen, start_pos, pos, radius, color)
            elif mode == 'circle': draw_circle(screen, start_pos, pos, radius, color)
            elif mode == 'square': draw_square(screen, start_pos, pos, radius, color)
            elif mode == 'right_tri': draw_right_triangle(screen, start_pos, pos, radius, color)
            elif mode == 'eq_tri': draw_equilateral_triangle(screen, start_pos, pos, radius, color)
            elif mode == 'rhombus': draw_rhombus(screen, start_pos, pos, radius, color)
            elif mode == 'line': pygame.draw.line(screen, color, start_pos, pos, radius)

        # Отображение текста во время ввода
        if typing and text_pos:
            text_surface = font.render(text_input, True, color)
            screen.blit(text_surface, text_pos)
            # мигающий курсор
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = text_pos[0] + text_surface.get_width()
                pygame.draw.line(screen, color, (cursor_x, text_pos[1]), (cursor_x, text_pos[1] + font.get_height()), 2)

        # Индикатор размера кисти рядом с курсором
        if mode not in ['text', 'fill']:
            pygame.draw.circle(screen, 
                               color if mode != 'eraser' else (255, 255, 255), 
                               pos, radius, 1)

        pygame.display.flip()
        clock.tick(120)

# --- ФУНКЦИИ ДЛЯ РИСОВАНИЯ ФИГУР ---

def draw_line(surf, start, end, width, color):
    """
    Рисуем линию маленькими кружками.
    Так она получается гладкой, даже если мышь двигается быстро.
    """
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = max(abs(dx), abs(dy))
    
    if distance == 0:
        pygame.draw.circle(surf, color, start, width)
        return
        
    for i in range(distance):
        x = int(start[0] + float(i) / distance * dx)
        y = int(start[1] + float(i) / distance * dy)
        pygame.draw.circle(surf, color, (x, y), width)

def draw_rect(surf, start, end, width, color):
    """Прямоугольник: берём начальную и конечную точку и рисуем рамку."""
    x1, y1 = start
    x2, y2 = end
    pygame.draw.rect(surf, color, 
                     (min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2)), 
                     width)

def draw_circle(surf, start, end, width, color):
    """Круг: радиус равен расстоянию между точками."""
    r = int(((start[0] - end[0])**2 + (start[1] - end[1])**2)**0.5)
    if r > width: 
        pygame.draw.circle(surf, color, start, r, width)

def draw_square(surf, start, end, width, color):
    """Квадрат: стороны равные, берём максимальную длину."""
    side_length = max(abs(start[0] - end[0]), abs(start[1] - end[1]))
    rect_x = start[0] if end[0] > start[0] else start[0] - side_length
    rect_y = start[1] if end[1] > start[1] else start[1] - side_length
    if side_length > 0:
        pygame.draw.rect(surf, color, (rect_x, rect_y, side_length, side_length), width)

def draw_right_triangle(surf, start, end, width, color):
    """Прямоугольный треугольник: три точки — старт, низ и конец."""
    points = [(start[0], start[1]), (start[0], end[1]), (end[0], end[1])]
    if len(set(points)) > 2:
        pygame.draw.polygon(surf, color, points, width)

def draw_equilateral_triangle(surf, start, end, width, color):
    """Равносторонний треугольник: верхняя точка по центру, низ — по краям."""
    mid_x = (start[0] + end[0]) // 2
    points = [(mid_x, start[1]), (start[0], end[1]), (end[0], end[1])]
    if len(set(points)) > 2:
        pygame.draw.polygon(surf, color, points, width)

def draw_rhombus(surf, start, end, width, color):
    """Ромб: считаем середины сторон и соединяем их."""
    mid_x = (start[0] + end[0]) // 2
    mid_y = (start[1] + end[1]) // 2
    points = [(mid_x, start[1]), (end[0], mid_y), (mid_x, end[1]), (start[0], mid_y)]
    if len(set(points)) > 2:
        pygame.draw.polygon(surf, color, points, width)

# --- ЗАПУСК ПРОГРАММЫ ---
if __name__ == "__main__":
    main()
