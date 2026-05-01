import pygame, sys, random, json, os
import psycopg2
from pygame.locals import *

# ==========================================
# INITIALIZATION
# ==========================================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 400
BLOCK = 20
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - TSIS 4")
clock = pygame.time.Clock()

font_large  = pygame.font.SysFont("Verdana", 40, bold=True)
font_style  = pygame.font.SysFont("Verdana", 20)
font_small  = pygame.font.SysFont("Verdana", 15)

C_BG         = (20, 20, 30)
WHITE        = (255, 255, 255)
BLACK        = (0, 0, 0)
GRAY         = (100, 100, 100)
RED          = (255, 0, 0)
POISON_COLOR = (139, 0, 0)
GREEN        = (0, 255, 0)
BLUE         = (0, 100, 255)
CYAN         = (0, 255, 255)
YELLOW       = (255, 215, 0)
FOOD_COLORS  = {1: RED, 2: CYAN, 3: YELLOW}

# ==========================================
# SOUND (загружаем с проверкой)
# ==========================================
def load_sound(filename):
    if os.path.exists(filename):
        try:
            return pygame.mixer.Sound(filename)
        except Exception as e:
            print(1)
    else:
        print(1)
    return None

eat_sound   = load_sound("eat.wav")
crash_sound = load_sound("crash.wav")

def play_sound(sound):
    if sound:
        sound.play()

def play_music(filename):
    if os.path.exists(filename):
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            print(1)
        except Exception as e:
            print(1)
    else:
        print(1)

def stop_music():
    pygame.mixer.music.stop()

def pause_music():
    pygame.mixer.music.pause()

def unpause_music():
    pygame.mixer.music.unpause()

# ==========================================
# DATABASE
# ==========================================
DB_CONFIG = {
    "host":     "",          # ← укажи свой хост
    "user":     "postgres",
    "password": "33333333",
    "dbname":   "snake_game",
    "port":     "5432"
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn:
        print("⚠️ Игра запущена без базы данных")
        return
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS game_sessions (
        id SERIAL PRIMARY KEY, player_id INTEGER REFERENCES players(id),
        score INTEGER NOT NULL, level_reached INTEGER NOT NULL,
        played_at TIMESTAMP DEFAULT NOW())""")
    conn.commit()
    cur.close(); conn.close()
    print("✅ БД готова")

init_db()

def save_score_to_db(username, score, level):
    conn = get_db_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT DO NOTHING RETURNING id", (username,))
        row = cur.fetchone()
        if not row:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
        player_id = row[0]
        cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s,%s,%s)",
                    (player_id, score, level))
        conn.commit()
        print(f"✅ Сохранено: {username} — {score} очков")
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
    finally:
        cur.close(); conn.close()

def get_leaderboard():
    conn = get_db_connection()
    if not conn: return []
    try:
        cur = conn.cursor()
        cur.execute("""SELECT p.username, gs.score, gs.level_reached
                       FROM game_sessions gs JOIN players p ON gs.player_id = p.id
                       ORDER BY gs.score DESC LIMIT 10""")
        return cur.fetchall()
    except Exception as e:
        print(f"❌ Ошибка лидерборда: {e}")
        return []
    finally:
        cur.close(); conn.close()

def get_personal_best(username):
    conn = get_db_connection()
    if not conn: return 0
    try:
        cur = conn.cursor()
        cur.execute("""SELECT MAX(gs.score) FROM game_sessions gs
                       JOIN players p ON gs.player_id = p.id WHERE p.username = %s""", (username,))
        result = cur.fetchone()
        return result[0] if result and result[0] else 0
    except:
        return 0
    finally:
        cur.close(); conn.close()

# ==========================================
# SETTINGS
# ==========================================
SETTINGS_FILE = "settings.json"

def load_settings():
    default = {"snake_color": [50, 205, 50], "grid": False, "sound": True}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except:
            pass
    return default

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f)

SETTINGS = load_settings()

# ==========================================
# UI HELPERS
# ==========================================
class Button:
    def __init__(self, x, y, w, h, text, color, hover):
        self.rect  = pygame.Rect(x, y, w, h)
        self.text  = text
        self.color = color
        self.hover = hover

    def draw(self, surf):
        col = self.hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surf, col, self.rect, border_radius=5)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=5)
        txt = font_style.render(self.text, True, WHITE)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

def draw_text(surf, text, font, color, x, y, center=False):
    obj  = font.render(text, True, color)
    rect = obj.get_rect()
    if center: rect.center = (x, y)
    else:      rect.topleft = (x, y)
    surf.blit(obj, rect)

# ==========================================
# GAMEPLAY HELPERS
# ==========================================
def get_safe_spawn(snake_list, obstacles):
    while True:
        x = random.randrange(0, WIDTH, BLOCK)
        y = random.randrange(0, HEIGHT, BLOCK)
        if [x, y] not in snake_list and (x, y) not in obstacles:
            return x, y

def generate_obstacles(level, snake_list, current_obs):
    obs = current_obs[:]
    if level < 3: return obs
    num = max(4, (level - 2) * 4)
    while len(obs) < num:
        ox, oy = get_safe_spawn(snake_list, obs)
        if abs(ox - snake_list[-1][0]) > BLOCK*3 or abs(oy - snake_list[-1][1]) > BLOCK*3:
            obs.append((ox, oy))
    return obs

# ==========================================
# GAMEPLAY
# ==========================================
def play_game(username):
    pb = get_personal_best(username)

    x = y = WIDTH // 2
    dx = dy = 0
    snake_list = [[x, y]]
    length = 1
    score  = 0
    level  = 1
    obstacles = []

    fx, fy   = get_safe_spawn(snake_list, obstacles)
    f_weight = random.randint(1, 3)
    f_time   = pygame.time.get_ticks()

    px, py = get_safe_spawn(snake_list, obstacles)

    pu_active = False
    pux = puy = -100
    pu_type = None
    pu_spawn_time = 0

    shielded       = False
    current_effect = None
    effect_end_time = 0

    obstacles = generate_obstacles(level, snake_list, obstacles)

    while True:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if   event.key == K_LEFT  and dx !=  BLOCK: dx, dy = -BLOCK, 0
                elif event.key == K_RIGHT and dx != -BLOCK: dx, dy =  BLOCK, 0
                elif event.key == K_UP    and dy !=  BLOCK: dx, dy = 0, -BLOCK
                elif event.key == K_DOWN  and dy != -BLOCK: dx, dy = 0,  BLOCK

        x += dx
        y += dy

        # Collision
        if (x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT or
                (x, y) in obstacles or [x, y] in snake_list[:-1]):
            if shielded:
                shielded = False
                x -= dx; y -= dy
                dx = dy = 0
            else:
                play_sound(crash_sound)
                save_score_to_db(username, score, level)
                return score, level, pb

        snake_list.append([x, y])
        if len(snake_list) > length:
            del snake_list[0]

        # Draw
        display.fill(C_BG)

        if SETTINGS.get("grid"):
            for i in range(0, WIDTH, BLOCK):
                pygame.draw.line(display, GRAY, (i, 0), (i, HEIGHT))
            for i in range(0, HEIGHT, BLOCK):
                pygame.draw.line(display, GRAY, (0, i), (WIDTH, i))

        for ox, oy in obstacles:
            pygame.draw.rect(display, GRAY, (ox, oy, BLOCK, BLOCK))

        pygame.draw.rect(display, POISON_COLOR, (px, py, BLOCK, BLOCK), border_radius=4)

        if pu_active:
            if now - pu_spawn_time > 8000:
                pu_active = False
            else:
                col = BLUE if pu_type == "SHIELD" else YELLOW if pu_type == "BOOST" else CYAN
                pygame.draw.circle(display, col, (pux + BLOCK//2, puy + BLOCK//2), BLOCK//2)

        # Food timer
        if now - f_time > 5000:
            fx, fy   = get_safe_spawn(snake_list, obstacles)
            f_weight = random.randint(1, 3)
            f_time   = now

        pygame.draw.rect(display, FOOD_COLORS[f_weight], (fx, fy, BLOCK, BLOCK), border_radius=4)
        timer_w = BLOCK * (1 - (now - f_time) / 5000.0)
        pygame.draw.rect(display, WHITE, (fx, fy - 5, timer_w, 3))

        # Snake
        snake_color = tuple(SETTINGS.get("snake_color", [50, 205, 50]))
        head_color  = tuple(min(255, c + 50) for c in snake_color)
        for i, seg in enumerate(snake_list):
            col = head_color if i == len(snake_list) - 1 else snake_color
            pygame.draw.rect(display, col, (*seg, BLOCK, BLOCK))
            if i == len(snake_list) - 1:
                pygame.draw.rect(display, CYAN if shielded else WHITE, (*seg, BLOCK, BLOCK), 3)

        # Eat food
        if x == fx and y == fy:
            play_sound(eat_sound)
            score += f_weight
            length += f_weight
            fx, fy   = get_safe_spawn(snake_list, obstacles)
            f_weight = random.randint(1, 3)
            f_time   = now
            new_level = (score // 10) + 1
            if new_level > level:
                level     = new_level
                obstacles = generate_obstacles(level, snake_list, obstacles)

        # Eat poison
        if x == px and y == py:
            length = max(1, length - 2)
            snake_list = snake_list[-length:]
            if length <= 1:
                play_sound(crash_sound)
                save_score_to_db(username, score, level)
                return score, level, pb
            px, py = get_safe_spawn(snake_list, obstacles)

        # Power-up spawn
        if not pu_active and random.random() < 0.008:
            pux, puy      = get_safe_spawn(snake_list, obstacles)
            pu_type       = random.choice(["BOOST", "SLOW", "SHIELD"])
            pu_spawn_time = now
            pu_active     = True

        # Power-up collect
        if pu_active and x == pux and y == puy:
            if pu_type == "SHIELD":
                shielded = True
            else:
                current_effect  = pu_type
                effect_end_time = now + 5000
            pu_active = False

        if current_effect and now > effect_end_time:
            current_effect = None

        # HUD
        pygame.draw.rect(display, BLACK, (0, 0, WIDTH, 30))
        draw_text(display, f"Score: {score}",       font_small, WHITE,  10,         5)
        draw_text(display, f"Level: {level}",       font_small, WHITE,  160,        5)
        draw_text(display, f"PB: {max(pb, score)}", font_small, YELLOW, WIDTH-110,  5)
        if shielded:
            draw_text(display, "SHIELD ACTIVE", font_small, CYAN,   WIDTH//2, 5, center=True)
        elif current_effect:
            draw_text(display, f"{current_effect}!", font_small, YELLOW, WIDTH//2, 5, center=True)

        pygame.display.update()
        clock.tick(12 + level)

# ==========================================
# MENUS
# ==========================================
def get_username():
    name = ""
    while True:
        display.fill(C_BG)
        draw_text(display, "Enter Username:", font_large, WHITE, WIDTH//2, HEIGHT//2 - 60, center=True)
        box = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 45)
        pygame.draw.rect(display, GRAY, box)
        pygame.draw.rect(display, WHITE, box, 2)
        draw_text(display, name + "|", font_style, WHITE, WIDTH//2 - 140, HEIGHT//2 + 8)
        draw_text(display, "Press ENTER to continue", font_small, YELLOW, WIDTH//2, HEIGHT//2 + 80, center=True)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name:
                    return name
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 15 and event.unicode.isalnum():
                    name += event.unicode
        pygame.display.update()
        clock.tick(30)

def game_over_screen(score, level, pb):
    btn_retry = Button(WIDTH//2 - 100, 220, 200, 45, "Retry",     GREEN, (0, 200, 0))
    btn_menu  = Button(WIDTH//2 - 100, 280, 200, 45, "Main Menu", BLUE,  (0, 0, 200))
    while True:
        display.fill(C_BG)
        draw_text(display, "GAME OVER",                    font_large,  RED,    WIDTH//2, 70,  center=True)
        draw_text(display, f"Score: {score}",              font_style,  WHITE,  WIDTH//2, 140, center=True)
        draw_text(display, f"Level: {level}",              font_style,  WHITE,  WIDTH//2, 170, center=True)
        draw_text(display, f"Personal Best: {max(score,pb)}", font_style, YELLOW, WIDTH//2, 200, center=True)
        btn_retry.draw(display); btn_menu.draw(display)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.is_clicked(event): return "RETRY"
            if btn_menu.is_clicked(event):  return "MENU"
        pygame.display.update()
        clock.tick(30)

def leaderboard_screen():
    btn_back = Button(WIDTH//2 - 100, HEIGHT - 70, 200, 45, "Back", RED, (200, 0, 0))
    lb = get_leaderboard()
    while True:
        display.fill(C_BG)
        draw_text(display, "TOP 10 LEADERBOARD", font_large, YELLOW, WIDTH//2, 40, center=True)
        if not lb:
            draw_text(display, "No scores yet", font_style, GRAY, WIDTH//2, 180, center=True)
        else:
            draw_text(display, "Rank  Name           Score  Level", font_small, WHITE, 50, 85)
            for i, (name, score, lvl) in enumerate(lb):
                draw_text(display, f"{i+1:<4} {name:<14} {score:<6} {lvl}", font_small, WHITE, 50, 110 + i*28)
        btn_back.draw(display)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if btn_back.is_clicked(event): return
        pygame.display.update()
        clock.tick(30)

def settings_screen():
    global SETTINGS
    colors      = {"GREEN": [50, 205, 50], "RED": [255, 80, 80], "BLUE": [80, 120, 255]}
    color_list  = list(colors.keys())
    current_name = next((n for n, c in colors.items() if c == SETTINGS.get("snake_color")), "GREEN")

    btn_grid  = Button(WIDTH//2 - 110, 130, 220, 45, f"Grid: {'ON' if SETTINGS['grid'] else 'OFF'}", GRAY, (160,160,160))
    btn_color = Button(WIDTH//2 - 110, 190, 220, 45, f"Color: {current_name}", GRAY, (160,160,160))
    btn_back  = Button(WIDTH//2 - 110, 270, 220, 45, "Save & Back", RED, (200, 0, 0))

    while True:
        display.fill(C_BG)
        draw_text(display, "SETTINGS", font_large, WHITE, WIDTH//2, 60, center=True)
        btn_grid.draw(display); btn_color.draw(display); btn_back.draw(display)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if btn_grid.is_clicked(event):
                SETTINGS["grid"] = not SETTINGS["grid"]
                btn_grid.text = f"Grid: {'ON' if SETTINGS['grid'] else 'OFF'}"
            if btn_color.is_clicked(event):
                idx = (color_list.index(current_name) + 1) % len(color_list)
                current_name = color_list[idx]
                SETTINGS["snake_color"] = colors[current_name]
                btn_color.text = f"Color: {current_name}"
            if btn_back.is_clicked(event):
                save_settings(SETTINGS); return
        pygame.display.update()
        clock.tick(30)

def main_menu():
    play_music("background.mp3")   # фоновая музыка в меню (поменяй на свой файл)
    btn_play     = Button(WIDTH//2 - 100, 160, 200, 45, "PLAY",        GREEN, (0, 220, 0))
    btn_lb       = Button(WIDTH//2 - 100, 220, 200, 45, "LEADERBOARD", BLUE,  (0, 0, 220))
    btn_settings = Button(WIDTH//2 - 100, 280, 200, 45, "SETTINGS",    GRAY,  (160,160,160))
    btn_quit     = Button(WIDTH//2 - 100, 340, 200, 45, "QUIT",        RED,   (220, 0, 0))

    while True:
        display.fill(C_BG)
        draw_text(display, "SNAKE GAME", font_large, GREEN, WIDTH//2, 80,  center=True)
        draw_text(display, "TSIS 4",     font_style, WHITE, WIDTH//2, 125, center=True)
        btn_play.draw(display); btn_lb.draw(display)
        btn_settings.draw(display); btn_quit.draw(display)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if btn_play.is_clicked(event):
                username = get_username()
                play_music("game.mp3")   # музыка во время игры (поменяй на свой файл)
                while True:
                    score, level, pb = play_game(username)
                    if game_over_screen(score, level, pb) == "MENU":
                        play_music("background.mp3")   # возвращаем музыку меню
                        break
            if btn_lb.is_clicked(event):       leaderboard_screen()
            if btn_settings.is_clicked(event): settings_screen()
            if btn_quit.is_clicked(event):
                pygame.quit(); sys.exit()

        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main_menu()
