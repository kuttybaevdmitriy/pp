import pygame

pygame.init()

# Вспомогательная функция для рисования "детализированной" машины
def draw_detailed_car(surface, color, is_player=True):
    width, height = surface.get_size()
    # 1. Тень под машиной
    pygame.draw.ellipse(surface, (20, 20, 20, 150), (2, 5, width-4, height-5))
    
    # 2. Основной кузов (делаем его шире и с изгибами)
    body_color = color
    dark_color = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
    
    # Главный корпус
    pygame.draw.rect(surface, body_color, (5, 10, width-10, height-20), border_radius=10)
    # Крыша
    pygame.draw.rect(surface, dark_color, (10, 30, width-20, 30), border_radius=5)
    
    # 3. Стекла
    glass_color = (100, 150, 200)
    if is_player:
        # Лобовое (спереди для игрока - сверху)
        pygame.draw.rect(surface, glass_color, (12, 25, width-24, 10), border_top_left_radius=5, border_top_right_radius=5)
        # Заднее
        pygame.draw.rect(surface, glass_color, (12, 55, width-24, 5))
    else:
        # Для врага (едет вниз, значит лобовое снизу)
        pygame.draw.rect(surface, glass_color, (12, 55, width-24, 10), border_bottom_left_radius=5, border_bottom_right_radius=5)
        # Заднее
        pygame.draw.rect(surface, glass_color, (12, 25, width-24, 5))

    # 4. Фары
    if is_player:
        pygame.draw.circle(surface, (255, 255, 200), (12, 15), 4) # Левая передняя
        pygame.draw.circle(surface, (255, 255, 200), (width-12, 15), 4) # Правая передняя
        pygame.draw.rect(surface, (200, 0, 0), (8, height-15, 10, 3)) # Стопы
        pygame.draw.rect(surface, (200, 0, 0), (width-18, height-15, 10, 3))
    else:
        pygame.draw.circle(surface, (255, 255, 200), (12, height-15), 4) # Фары врага снизу
        pygame.draw.circle(surface, (255, 255, 200), (width-12, height-15), 4)
        pygame.draw.rect(surface, (200, 0, 0), (8, 12, 10, 3)) # Стопы сверху
        pygame.draw.rect(surface, (200, 0, 0), (width-18, 12, 10, 3))

    # 5. Колеса (широкие)
    wheel_color = (30, 30, 30)
    pygame.draw.rect(surface, wheel_color, (0, 15, 7, 18), border_radius=3) # ЛП
    pygame.draw.rect(surface, wheel_color, (width-7, 15, 7, 18), border_radius=3) # ПП
    pygame.draw.rect(surface, wheel_color, (0, 60, 7, 18), border_radius=3) # ЛЗ
    pygame.draw.rect(surface, wheel_color, (width-7, 60, 7, 18), border_radius=3) # ПЗ

# --- 1. Player (Синий спорткар, теперь 50x90) ---
player_img = pygame.Surface((50, 90), pygame.SRCALPHA)
draw_detailed_car(player_img, (30, 100, 255), is_player=True)
pygame.image.save(player_img, "Player.png")

# --- 2. Enemy (Красный маслкар, 50x90) ---
enemy_img = pygame.Surface((50, 90), pygame.SRCALPHA)
draw_detailed_car(enemy_img, (220, 30, 30), is_player=False)
pygame.image.save(enemy_img, "Enemy.png")

# --- 3. Coin (Золотая монета с блеском, 40x40) ---
coin_img = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(coin_img, (255, 215, 0), (20, 20), 18) # Золото
pygame.draw.circle(coin_img, (184, 134, 11), (20, 20), 18, 2) # Кант
pygame.draw.circle(coin_img, (255, 255, 255), (14, 14), 4) # Блик для объема
# Символ доллара или просто линия
pygame.draw.rect(coin_img, (184, 134, 11), (18, 10, 4, 20))
pygame.image.save(coin_img, "Coin.png")

# --- 4. AnimatedStreet (Текстурный асфальт, 400x600) ---
street_img = pygame.Surface((400, 600))
street_img.fill((50, 50, 50)) # Темный асфальт
# Рисуем "шум" асфальта
for i in range(500):
    x, y = (pygame.time.get_ticks() + i*13) % 400, (i*17) % 600
    pygame.draw.circle(street_img, (55, 55, 55), (x, y), 1)

pygame.draw.rect(street_img, (255, 255, 255), (5, 0, 5, 600)) # Обочина левая
pygame.draw.rect(street_img, (255, 255, 255), (390, 0, 5, 600)) # Обочина правая
for y in range(0, 600, 80):
    pygame.draw.rect(street_img, (255, 215, 0), (198, y, 4, 40)) # Желтая прерывистая

pygame.image.save(street_img, "AnimatedStreet.png")

print("Красивые картинки созданы! Теперь запускай main.py.")