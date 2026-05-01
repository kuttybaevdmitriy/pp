import pygame, sys, random, json, os
from pygame.locals import *
from datetime import datetime

# ==========================================
# 1. INITIALIZATION & GLOBAL SETTINGS
# ==========================================
pygame.init()
pygame.mixer.init()

FPS = 60
FramePerSec = pygame.time.Clock()

# Colors
BLUE   = (0, 0, 255)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
GRAY   = (100, 100, 100)
CYAN   = (0, 255, 255)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game - TSIS 3")

# Fonts
font_large = pygame.font.SysFont("Verdana", 50, bold=True)
font_medium = pygame.font.SysFont("Verdana", 30)
font_small = pygame.font.SysFont("Verdana", 20)

# Load Sound Effects safely
def load_sound(file):
    try:
        return pygame.mixer.Sound(file)
    except FileNotFoundError:
        return None

sound_coin = load_sound('coin.wav')
sound_crash = load_sound('crash.wav')

# Load original background safely
try:
    background = pygame.image.load("AnimatedStreet.png")
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
except FileNotFoundError:
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(GRAY) 

# ==========================================
# 2. PERSISTENCE (JSON LOAD/SAVE)
# ==========================================
SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

def load_settings():
    """Loads game settings from JSON. Creates default if missing."""
    default_settings = {"sound": True, "car_color": "BLUE", "difficulty": "MEDIUM"}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    with open(SETTINGS_FILE, "w") as f:
        json.dump(default_settings, f)
    return default_settings

def save_settings(settings):
    """Saves current settings to JSON."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def load_leaderboard():
    """Loads leaderboard from JSON."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return []

def save_score(name, score, distance):
    """Saves a new score, sorts the leaderboard, and keeps the top 10."""
    lb = load_leaderboard()
    lb.append({"name": name, "score": score, "distance": round(distance, 1), "date": str(datetime.now().date())})
    # Sort by score descending
    lb = sorted(lb, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(lb, f, indent=4)

SETTINGS = load_settings()

# ==========================================
# 3. GAME CLASSES (ENTITIES)
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.load_image()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.shielded = False # Power-up state

    def load_image(self):
        """Loads player image and applies a color tint based on Settings."""
        try:
            self.base_image = pygame.image.load("Player.png").convert_alpha()
        except FileNotFoundError:
            self.base_image = pygame.Surface((40, 60), pygame.SRCALPHA)
            self.base_image.fill((255, 255, 255))
        
        # Apply Color Setting
        color_map = {"BLUE": BLUE, "RED": RED, "GREEN": GREEN}
        tint = color_map.get(SETTINGS["car_color"], BLUE)
        
        self.image = self.base_image.copy()
        # Simple tinting effect
        self.image.fill(tint, special_flags=pygame.BLEND_MULT)

    def move(self):
        pressed_keys = pygame.key.get_pressed()
        move_speed = 7 # Player lateral speed
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-move_speed, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(move_speed, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Draw Shield Halo if active
        if self.shielded:
            pygame.draw.circle(surface, CYAN, self.rect.center, 40, 3)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, existing_sprites, base_speed):
        super().__init__() 
        try:
            self.image = pygame.image.load("Enemy.png").convert_alpha()
        except FileNotFoundError:
            self.image = pygame.Surface((40, 60))
            self.image.fill(RED)
        
        self.rect = self.image.get_rect()
        self.speed_offset = random.randint(0, 2) # Traffic cars move slightly faster than the road
        self.base_speed = base_speed
        self.spawn_safely(existing_sprites)

    def spawn_safely(self, existing_sprites):
        """Ensures the enemy doesn't spawn exactly on top of another object."""
        while True:
            self.rect.center = (random.randint(40, SCREEN_WIDTH-40), random.randint(-200, -50))
            if not pygame.sprite.spritecollideany(self, existing_sprites):
                break

    def move(self, global_speed):
        self.rect.move_ip(0, global_speed + self.speed_offset)

class Obstacle(pygame.sprite.Sprite):
    """Static hazards on the road (e.g., potholes, barriers)"""
    def __init__(self, existing_sprites):
        super().__init__()
        self.image = pygame.Surface((50, 20))
        self.image.fill((139, 69, 19)) # Brown color for barrier/pothole
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2) # Border
        
        self.rect = self.image.get_rect()
        self.spawn_safely(existing_sprites)

    def spawn_safely(self, existing_sprites):
        while True:
            self.rect.center = (random.randint(40, SCREEN_WIDTH-40), random.randint(-300, -50))
            if not pygame.sprite.spritecollideany(self, existing_sprites):
                break

    def move(self, global_speed):
        self.rect.move_ip(0, global_speed) # Moves exactly with the road

class Coin(pygame.sprite.Sprite):
    def __init__(self, existing_sprites):
        super().__init__()
        self.coin_images = {
            1: self.make_coin_img(BRONZE, 10),
            2: self.make_coin_img(SILVER, 15),
            3: self.make_coin_img(YELLOW, 20) 
        }
        self.spawn(existing_sprites)

    def make_coin_img(self, color, radius):
        surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (radius, radius), radius)
        pygame.draw.circle(surf, BLACK, (radius, radius), radius, 2)
        return surf

    def spawn(self, existing_sprites):
        self.weight = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
        self.image = self.coin_images[self.weight]
        self.rect = self.image.get_rect()
        
        while True:
            self.rect.center = (random.randint(40, SCREEN_WIDTH-40), random.randint(-400, -50))
            if not pygame.sprite.spritecollideany(self, existing_sprites):
                break

    def move(self, global_speed):
        self.rect.move_ip(0, global_speed)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, existing_sprites):
        super().__init__()
        # Types: NITRO, SHIELD, REPAIR
        self.type = random.choice(["NITRO", "SHIELD", "REPAIR"])
        self.image = pygame.Surface((30, 30))
        
        if self.type == "NITRO":
            self.image.fill((255, 100, 0)) # Orange
        elif self.type == "SHIELD":
            self.image.fill(CYAN)
        elif self.type == "REPAIR":
            self.image.fill(GREEN)
            
        pygame.draw.rect(self.image, WHITE, self.image.get_rect(), 3)
        self.rect = self.image.get_rect()
        
        while True:
            self.rect.center = (random.randint(40, SCREEN_WIDTH-40), random.randint(-500, -100))
            if not pygame.sprite.spritecollideany(self, existing_sprites):
                break

    def move(self, global_speed):
        self.rect.move_ip(0, global_speed)

# ==========================================
# 4. UI HELPER CLASSES
# ==========================================
class Button:
    def __init__(self, x, y, w, h, text, color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font_medium

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10) # Border
        
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def draw_text(surface, text, font, color, x, y, center=False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

# ==========================================
# 5. GAME SCREENS & LOGIC
# ==========================================

def get_base_speed():
    """Returns starting speed based on difficulty setting"""
    if SETTINGS["difficulty"] == "EASY": return 4
    if SETTINGS["difficulty"] == "MEDIUM": return 6
    if SETTINGS["difficulty"] == "HARD": return 8
    return 6

def play_sound(sound):
    if SETTINGS["sound"] and sound:
        sound.play()

def get_username():
    """Screen for player to input their name."""
    name = ""
    active = True
    while active:
        DISPLAYSURF.fill(BLACK)
        draw_text(DISPLAYSURF, "Enter Username:", font_medium, WHITE, SCREEN_WIDTH//2, 200, center=True)
        
        # Draw input box
        input_rect = pygame.Rect(50, 250, 300, 50)
        pygame.draw.rect(DISPLAYSURF, GRAY, input_rect)
        pygame.draw.rect(DISPLAYSURF, WHITE, input_rect, 2)
        
        draw_text(DISPLAYSURF, name + "|", font_medium, WHITE, 60, 260)
        draw_text(DISPLAYSURF, "Press ENTER to start", font_small, YELLOW, SCREEN_WIDTH//2, 350, center=True)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and len(name) > 0:
                    return name
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12 and event.unicode.isalnum():
                        name += event.unicode
                        
        pygame.display.update()
        FramePerSec.tick(FPS)

def game_loop(username):
    """Main playing loop."""
    P1 = Player()
    
    enemies = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    
    all_sprites.add(P1)

    # Initial spawns
    for _ in range(2):
        e = Enemy(all_sprites, get_base_speed())
        enemies.add(e); all_sprites.add(e)
        
    c = Coin(all_sprites)
    coins.add(c); all_sprites.add(c)

    # Game state variables
    score = 0
    distance = 0.0
    coins_collected = 0
    global_speed = get_base_speed()
    
    # Background scrolling variables
    bg_y1 = 0
    bg_y2 = -SCREEN_HEIGHT

    # Power-up state
    active_powerup = None
    powerup_timer = 0
    nitro_active = False

    # Timers for spawning
    spawn_timer = 0
    powerup_spawn_timer = 0

    running = True
    while running:
        # --- BACKGROUND SCROLLING ---
        current_bg_speed = global_speed + (5 if nitro_active else 0)
        bg_y1 += current_bg_speed
        bg_y2 += current_bg_speed
        if bg_y1 >= SCREEN_HEIGHT: bg_y1 = -SCREEN_HEIGHT
        if bg_y2 >= SCREEN_HEIGHT: bg_y2 = -SCREEN_HEIGHT
        
        DISPLAYSURF.blit(background, (0, bg_y1))
        DISPLAYSURF.blit(background, (0, bg_y2))

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

        # --- LOGIC & MOVEMENT ---
        P1.move()
        distance += (current_bg_speed / 60.0) # Calculate distance based on speed
        score = int(distance * 10) + (coins_collected * 50)

        # Move all other sprites
        for entity in all_sprites:
            if entity != P1:
                entity.move(current_bg_speed)
                # Remove if off-screen and respawn logic
                if entity.rect.top > SCREEN_HEIGHT:
                    entity.kill()

        # --- DYNAMIC SPAWNING ---
        spawn_timer += 1
        # Increase difficulty (spawn rate) as score goes up
        spawn_rate = max(20, 60 - (score // 1000)) 
        
        if spawn_timer > spawn_rate:
            spawn_timer = 0
            # 70% chance Enemy, 30% chance Obstacle
            if random.random() < 0.7:
                e = Enemy(all_sprites, global_speed)
                enemies.add(e); all_sprites.add(e)
            else:
                o = Obstacle(all_sprites)
                obstacles.add(o); all_sprites.add(o)

        # Ensure there's always at least one coin
        if len(coins) < 2:
            c = Coin(all_sprites)
            coins.add(c); all_sprites.add(c)

        # Spawn Powerups randomly (~every 15 seconds)
        powerup_spawn_timer += 1
        if powerup_spawn_timer > FPS * 15:
            powerup_spawn_timer = 0
            if random.random() < 0.5: # 50% chance to actually spawn
                p = PowerUp(all_sprites)
                powerups.add(p); all_sprites.add(p)

        # --- POWER-UP TIMERS ---
        if active_powerup:
            powerup_timer -= 1
            if powerup_timer <= 0:
                active_powerup = None
                nitro_active = False

        # --- COLLISIONS ---
        
        # 1. Coins
        for coin in pygame.sprite.spritecollide(P1, coins, True):
            play_sound(sound_coin)
            coins_collected += coin.weight
            # Speed scaling every 10 coins
            if coins_collected % 10 == 0:
                global_speed += 0.5

        # 2. Power-ups
        for pu in pygame.sprite.spritecollide(P1, powerups, True):
            active_powerup = pu.type
            if pu.type == "NITRO":
                nitro_active = True
                powerup_timer = FPS * 5 # 5 seconds
            elif pu.type == "SHIELD":
                P1.shielded = True
                powerup_timer = FPS * 15 # Shield lasts 15 seconds or until hit
            elif pu.type == "REPAIR":
                # Clear all enemies and obstacles instantly
                for e in enemies: e.kill()
                for o in obstacles: o.kill()
                active_powerup = "CLEAR BOMB!"
                powerup_timer = FPS * 2 # Just to show the text briefly

        # 3. Enemies and Obstacles (The Bad Stuff)
        hit_list = pygame.sprite.spritecollide(P1, enemies, False) + pygame.sprite.spritecollide(P1, obstacles, False)
        if hit_list:
            if P1.shielded:
                # Consume shield and destroy the object we hit
                play_sound(sound_crash)
                P1.shielded = False
                active_powerup = None
                hit_list[0].kill()
            else:
                # GAME OVER
                play_sound(sound_crash)
                pygame.time.wait(500)
                save_score(username, score, distance)
                return score, distance, coins_collected

        # --- RENDERING ---
        for entity in all_sprites:
            if entity == P1:
                entity.draw(DISPLAYSURF) # Custom draw for shield
            else:
                DISPLAYSURF.blit(entity.image, entity.rect)

        # UI
        pygame.draw.rect(DISPLAYSURF, BLACK, (0, 0, SCREEN_WIDTH, 40)) # Top Bar
        draw_text(DISPLAYSURF, f"Score: {score}", font_small, WHITE, 10, 10)
        draw_text(DISPLAYSURF, f"Dist: {distance:.1f}m", font_small, WHITE, 150, 10)
        draw_text(DISPLAYSURF, f"Coins: {coins_collected}", font_small, YELLOW, SCREEN_WIDTH - 100, 10)

        # Powerup Status
        if active_powerup:
            time_left = powerup_timer // FPS
            draw_text(DISPLAYSURF, f"[{active_powerup}] {time_left}s", font_small, CYAN, SCREEN_WIDTH//2, 60, center=True)

        pygame.display.update()
        FramePerSec.tick(FPS)

def game_over_screen(score, distance, coins):
    btn_retry = Button(100, 350, 200, 50, "Retry", GREEN, (0, 200, 0))
    btn_menu = Button(100, 420, 200, 50, "Main Menu", BLUE, (0, 0, 200))

    while True:
        DISPLAYSURF.fill(RED)
        draw_text(DISPLAYSURF, "CRASHED!", font_large, WHITE, SCREEN_WIDTH//2, 100, center=True)
        draw_text(DISPLAYSURF, f"Score: {score}", font_medium, WHITE, SCREEN_WIDTH//2, 180, center=True)
        draw_text(DISPLAYSURF, f"Distance: {distance:.1f}m", font_medium, WHITE, SCREEN_WIDTH//2, 230, center=True)
        draw_text(DISPLAYSURF, f"Coins: {coins}", font_medium, YELLOW, SCREEN_WIDTH//2, 280, center=True)

        btn_retry.draw(DISPLAYSURF)
        btn_menu.draw(DISPLAYSURF)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.is_clicked(event):
                return "RETRY"
            if btn_menu.is_clicked(event):
                return "MENU"

        pygame.display.update()
        FramePerSec.tick(FPS)

def settings_screen():
    global SETTINGS
    
    btn_sound = Button(100, 150, 200, 50, f"Sound: {'ON' if SETTINGS['sound'] else 'OFF'}", GRAY, (150, 150, 150))
    btn_color = Button(100, 250, 200, 50, f"Car: {SETTINGS['car_color']}", GRAY, (150, 150, 150))
    btn_diff = Button(100, 350, 200, 50, f"Diff: {SETTINGS['difficulty']}", GRAY, (150, 150, 150))
    btn_back = Button(100, 480, 200, 50, "Back", RED, (200, 0, 0))

    while True:
        DISPLAYSURF.fill(BLACK)
        draw_text(DISPLAYSURF, "SETTINGS", font_large, WHITE, SCREEN_WIDTH//2, 60, center=True)

        btn_sound.draw(DISPLAYSURF)
        btn_color.draw(DISPLAYSURF)
        btn_diff.draw(DISPLAYSURF)
        btn_back.draw(DISPLAYSURF)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            
            if btn_sound.is_clicked(event):
                SETTINGS["sound"] = not SETTINGS["sound"]
                btn_sound.text = f"Sound: {'ON' if SETTINGS['sound'] else 'OFF'}"
                save_settings(SETTINGS)
                
            if btn_color.is_clicked(event):
                colors = ["BLUE", "RED", "GREEN"]
                idx = colors.index(SETTINGS["car_color"])
                SETTINGS["car_color"] = colors[(idx + 1) % 3]
                btn_color.text = f"Car: {SETTINGS['car_color']}"
                save_settings(SETTINGS)

            if btn_diff.is_clicked(event):
                diffs = ["EASY", "MEDIUM", "HARD"]
                idx = diffs.index(SETTINGS["difficulty"])
                SETTINGS["difficulty"] = diffs[(idx + 1) % 3]
                btn_diff.text = f"Diff: {SETTINGS['difficulty']}"
                save_settings(SETTINGS)
                
            if btn_back.is_clicked(event):
                return

        pygame.display.update()
        FramePerSec.tick(FPS)

def leaderboard_screen():
    btn_back = Button(100, 500, 200, 50, "Back", RED, (200, 0, 0))
    lb = load_leaderboard()

    while True:
        DISPLAYSURF.fill(BLACK)
        draw_text(DISPLAYSURF, "TOP 10 SCORES", font_medium, YELLOW, SCREEN_WIDTH//2, 40, center=True)

        y = 100
        if not lb:
            draw_text(DISPLAYSURF, "No scores yet!", font_small, WHITE, SCREEN_WIDTH//2, 200, center=True)
        else:
            for i, entry in enumerate(lb):
                text = f"{i+1}. {entry['name']} - {entry['score']} ({entry['distance']}m)"
                draw_text(DISPLAYSURF, text, font_small, WHITE, 20, y)
                y += 35

        btn_back.draw(DISPLAYSURF)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if btn_back.is_clicked(event):
                return

        pygame.display.update()
        FramePerSec.tick(FPS)

def main_menu():
    btn_play = Button(100, 200, 200, 60, "PLAY", GREEN, (0, 200, 0))
    btn_lb = Button(100, 280, 200, 60, "LEADERBOARD", BLUE, (0, 0, 200))
    btn_settings = Button(100, 360, 200, 60, "SETTINGS", GRAY, (150, 150, 150))
    btn_quit = Button(100, 440, 200, 60, "QUIT", RED, (200, 0, 0))

    while True:
        # Static background for menu
        DISPLAYSURF.blit(background, (0, 0))
        # Dim the background slightly
        dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        dim_surface.set_alpha(150)
        dim_surface.fill(BLACK)
        DISPLAYSURF.blit(dim_surface, (0, 0))

        draw_text(DISPLAYSURF, "RACER", font_large, YELLOW, SCREEN_WIDTH//2, 100, center=True)

        btn_play.draw(DISPLAYSURF)
        btn_lb.draw(DISPLAYSURF)
        btn_settings.draw(DISPLAYSURF)
        btn_quit.draw(DISPLAYSURF)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            
            if btn_play.is_clicked(event):
                name = get_username()
                while True:
                    score, dist, coins = game_loop(name)
                    action = game_over_screen(score, dist, coins)
                    if action == "MENU":
                        break # Break inner loop, go back to main menu
            
            if btn_lb.is_clicked(event):
                leaderboard_screen()
                
            if btn_settings.is_clicked(event):
                settings_screen()
                
            if btn_quit.is_clicked(event):
                pygame.quit(); sys.exit()

        pygame.display.update()
        FramePerSec.tick(FPS)

# ==========================================
# 6. START APPLICATION
# ==========================================
if __name__ == "__main__":
    main_menu()