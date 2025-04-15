import pygame
import random
import os
import time
import sys
from pygame import mixer
import math

# Initialize pygame
pygame.init()
mixer.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Racer")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
DARK_BLUE = (0, 0, 100)
LIGHT_BLUE = (135, 206, 235)
SAND = (210, 180, 140)
MOUNTAIN_GREEN = (70, 90, 70)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3
LEVEL_TRANSITION = 4
game_state = MENU

# Road parameters
ROAD_WIDTH = 400
ROAD_X = (WIDTH - ROAD_WIDTH) // 2
STRIPE_HEIGHT = 50
STRIPE_GAP = 20

# Game parameters
clock = pygame.time.Clock()
FPS = 60
SCORE = 0
HIGH_SCORE = 0
POWERUP_DURATION = 5000  # 5 seconds for power-ups

# Level system
levels = [
    {   # Level 1 - City
        "name": "CITY",
        "speed": 5,
        "enemy_interval": 2000,
        "road_color": (80, 80, 80),
        "environment_color": (50, 50, 50),
        "required_score": 0,
        "stripe_color": YELLOW,
        "has_buildings": True,
        "has_trees": True,
        "tree_color": (0, 100, 0),
        "building_colors": [(120, 120, 120), (150, 150, 150), (180, 180, 180)]
    },
    {   # Level 2 - Desert
        "name": "DESERT",
        "speed": 7,
        "enemy_interval": 1500,
        "road_color": (160, 130, 90),
        "environment_color": SAND,
        "required_score": 50,
        "stripe_color": WHITE,
        "has_buildings": False,
        "has_trees": False,
        "has_cacti": True,
        "cactus_color": (50, 120, 50)
    },
    {   # Level 3 - Mountain
        "name": "MOUNTAIN",
        "speed": 9,
        "enemy_interval": 1000,
        "road_color": (100, 100, 100),
        "environment_color": MOUNTAIN_GREEN,
        "required_score": 100,
        "stripe_color": WHITE,
        "has_buildings": False,
        "has_trees": True,
        "tree_color": (30, 80, 30),
        "has_rocks": True,
        "rock_color": (90, 90, 90)
    }
]
current_level = 0

# Weather system
weather_types = ["clear", "rain", "snow"]
current_weather = "clear"
weather_change_time = pygame.time.get_ticks()
weather_duration = 10000  # Initial weather duration (10 seconds)

# Initialize rain drops
rain_drops = []
for _ in range(100):
    rain_drops.append([
        random.randint(0, WIDTH),
        random.randint(-HEIGHT, 0),
        random.randint(1, 3),  # speed
        random.randint(1, 3)   # length
    ])

# Initialize snow flakes
snow_flakes = []
for _ in range(50):
    snow_flakes.append([
        random.randint(0, WIDTH),
        random.randint(-HEIGHT, 0),
        random.uniform(0.5, 1.5),  # x speed
        random.uniform(1, 2)       # y speed
    ])






def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)












# Load images
def load_image(name, scale=1):
    try:
        image = pygame.image.load(resource_path(name))
        if scale != 1:
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] * scale)))
        return image
    except Exception as e:
        print(f"Error loading image {name}: {e}")
        # Create placeholder
        surf = pygame.Surface((50, 80))
        if "speed" in name:
            surf.fill(YELLOW)
        elif "shield" in name:
            surf.fill(BLUE)
        elif "bonus" in name:
            surf.fill(GREEN)
        elif "enemy" in name:
            surf.fill(RED)
        else:
            surf.fill(BLUE)
        return surf

# Load sounds
def load_sound(name):
    try:
        return mixer.Sound(resource_path(name))
    except Exception as e:
        print(f"Error loading sound {name}: {e}")
        return None

# Try to load assets
car_img = load_image("car.png", 0.1)
enemy_car_imgs = [
    load_image("enemy_car1.png", 0.1),
    load_image("enemy_car2.png", 0.1),
    load_image("enemy_car3.png", 0.1)
]

powerup_imgs = {
    "speed": load_image("speed_boost.png", 0.1),
    "shield": load_image("shield.png", 0.1),
    "points": load_image("bonus_points.png", 0.1)
}

# Sound effects
crash_sound = load_sound("crash.wav")
engine_sound = load_sound("engine.wav")
powerup_sound = load_sound("powerup.wav")
level_up_sound = load_sound("levelup.wav")
background_music = load_sound("background_music.wav")

if background_music:
    background_music.set_volume(0.5)
    background_music.play(-1)

# Fonts
try:
    font_small = pygame.font.SysFont("Arial", 25)
    font_medium = pygame.font.SysFont("Arial", 35, bold=True)
    font_large = pygame.font.SysFont("Arial", 50, bold=True)
except:
    # Fallback if system fonts aren't available
    font_small = pygame.font.Font(None, 25)
    font_medium = pygame.font.Font(None, 35)
    font_large = pygame.font.Font(None, 50)

class PlayerCar:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.img = car_img
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.base_speed = 5
        self.speed = self.base_speed
        self.shield = False
        self.shield_end_time = 0
        self.speed_boost_end_time = 0
        self.level3_speed_increase_timer = 0
        self.level3_speed_increment = 0.03
        
    def draw(self):
        screen.blit(self.img, (self.x, self.y))
        if self.shield:
            shield_rect = pygame.Rect(self.x-5, self.y-5, self.width+10, self.height+10)
            pygame.draw.ellipse(screen, BLUE, shield_rect, 2)
        
    def move(self):
        # Adjust speed based on weather
        if current_weather == "rain":
            effective_speed = self.speed * 0.9
        elif current_weather == "snow":
            effective_speed = self.speed * 0.8
        else:
            effective_speed = self.speed
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > ROAD_X + 20:
            self.x -= effective_speed
        if keys[pygame.K_RIGHT] and self.x < ROAD_X + ROAD_WIDTH - self.width - 20:
            self.x += effective_speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= effective_speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += effective_speed
            
    def update_powerups(self, current_time):
        if current_time > self.speed_boost_end_time and self.speed > self.base_speed:
            self.speed = self.base_speed
        if current_time > self.shield_end_time and self.shield:
            self.shield = False

class EnemyCar:
    def __init__(self):
        self.img = random.choice(enemy_car_imgs)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x = random.randint(ROAD_X + 20, ROAD_X + ROAD_WIDTH - self.width - 20)
        self.y = -self.height
        if current_level == 0:  # City
            self.speed = random.randint(3, 6)
        elif current_level == 1:  # Desert
            self.speed = random.randint(5, 8)
        else:  # Mountain
            self.speed = random.randint(7, 10)
        
    def draw(self):
        screen.blit(self.img, (self.x, self.y))
        
    def move(self):
        self.y += self.speed
        return self.y > HEIGHT
        
    def collide(self, player):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(enemy_rect)

class PowerUp:
    def __init__(self):
        self.type = random.choice(["speed", "shield", "points"])
        self.img = powerup_imgs[self.type]
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.x = random.randint(ROAD_X + 20, ROAD_X + ROAD_WIDTH - self.width - 20)
        self.y = -self.height
        self.speed = 3
        
    def move(self):
        self.y += self.speed
        return self.y > HEIGHT
    
    def draw(self):
        screen.blit(self.img, (self.x, self.y))

class Road:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.stripes = []
        self.y = 0
        self.speed = levels[current_level]["speed"]
        self.trees = []
        self.buildings = []
        self.init_environment()
        
    def init_environment(self):
        # Road stripes
        for i in range(0, HEIGHT, STRIPE_HEIGHT + STRIPE_GAP):
            self.stripes.append(pygame.Rect(ROAD_X + ROAD_WIDTH // 2 - 5, i, 10, STRIPE_HEIGHT))
        
        level = levels[current_level]
        
        # Left side environment
        for i in range(0, HEIGHT, 100):
            # City level - buildings and trees
            if level["name"] == "CITY":
                if random.random() > 0.3 and level["has_trees"]:
                    self.trees.append({
                        "x": random.randint(10, ROAD_X - 60),
                        "y": i,
                        "width": random.randint(30, 60),
                        "height": random.randint(60, 100),
                        "type": "tree"
                    })
                elif level["has_buildings"]:
                    self.buildings.append({
                        "x": random.randint(10, ROAD_X - 150),
                        "y": i,
                        "width": random.randint(80, 150),
                        "height": random.randint(100, 200),
                        "color": random.choice(level["building_colors"])
                    })
            
            # Desert level - cacti
            elif level["name"] == "DESERT" and level["has_cacti"]:
                if random.random() > 0.5:
                    self.trees.append({
                        "x": random.randint(10, ROAD_X - 40),
                        "y": i,
                        "width": random.randint(20, 40),
                        "height": random.randint(40, 80),
                        "type": "cactus"
                    })
            
            # Mountain level - trees and rocks
            elif level["name"] == "MOUNTAIN":
                if random.random() > 0.6 and level["has_trees"]:
                    self.trees.append({
                        "x": random.randint(10, ROAD_X - 60),
                        "y": i,
                        "width": random.randint(30, 60),
                        "height": random.randint(60, 100),
                        "type": "tree"
                    })
                elif level["has_rocks"] and random.random() > 0.7:
                    self.trees.append({
                        "x": random.randint(10, ROAD_X - 80),
                        "y": i,
                        "width": random.randint(50, 100),
                        "height": random.randint(30, 60),
                        "type": "rock"
                    })
        
        # Right side environment (same logic as left side)
        for i in range(0, HEIGHT, 100):
            # City level
            if level["name"] == "CITY":
                if random.random() > 0.3 and level["has_trees"]:
                    self.trees.append({
                        "x": random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - 60),
                        "y": i,
                        "width": random.randint(30, 60),
                        "height": random.randint(60, 100),
                        "type": "tree"
                    })
                elif level["has_buildings"]:
                    self.buildings.append({
                        "x": random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - 150),
                        "y": i,
                        "width": random.randint(80, 150),
                        "height": random.randint(100, 200),
                        "color": random.choice(level["building_colors"])
                    })
            
            # Desert level
            elif level["name"] == "DESERT" and level["has_cacti"]:
                if random.random() > 0.5:
                    self.trees.append({
                        "x": random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - 40),
                        "y": i,
                        "width": random.randint(20, 40),
                        "height": random.randint(40, 80),
                        "type": "cactus"
                    })
            
            # Mountain level
            elif level["name"] == "MOUNTAIN":
                if random.random() > 0.6 and level["has_trees"]:
                    self.trees.append({
                        "x": random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - 60),
                        "y": i,
                        "width": random.randint(30, 60),
                        "height": random.randint(60, 100),
                        "type": "tree"
                    })
                elif level["has_rocks"] and random.random() > 0.7:
                    self.trees.append({
                        "x": random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - 80),
                        "y": i,
                        "width": random.randint(50, 100),
                        "height": random.randint(30, 60),
                        "type": "rock"
                    })
    
    def update(self):
        # Move stripes
        for stripe in self.stripes:
            stripe.y += self.speed
            if stripe.y > HEIGHT:
                stripe.y = -STRIPE_HEIGHT
                
        # Move environment
        for tree in self.trees:
            tree["y"] += self.speed
            if tree["y"] > HEIGHT:
                tree["y"] = -tree["height"]
                tree["x"] = random.randint(10, ROAD_X - 60) if tree["x"] < ROAD_X else random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - 60)
                
        for building in self.buildings:
            building["y"] += self.speed
            if building["y"] > HEIGHT:
                building["y"] = -building["height"]
                building["x"] = random.randint(10, ROAD_X - 150) if building["x"] < ROAD_X else random.randint(ROAD_X + ROAD_WIDTH + 10, WIDTH - 150)
    
    def draw(self):
        # Draw sky background
        if current_weather == "clear":
            screen.fill(LIGHT_BLUE)
        elif current_weather == "rain":
            screen.fill(DARK_BLUE)
        else:  # snow
            screen.fill((200, 230, 255))
            
        # Draw road
        pygame.draw.rect(screen, levels[current_level]["road_color"], (ROAD_X, 0, ROAD_WIDTH, HEIGHT))
        
        # Draw borders
        pygame.draw.rect(screen, levels[current_level]["stripe_color"], (ROAD_X, 0, 10, HEIGHT))
        pygame.draw.rect(screen, levels[current_level]["stripe_color"], (ROAD_X + ROAD_WIDTH - 10, 0, 10, HEIGHT))
        
        # Draw stripes
        for stripe in self.stripes:
            pygame.draw.rect(screen, levels[current_level]["stripe_color"], stripe)
            
        # Draw grass/surroundings
        pygame.draw.rect(screen, levels[current_level]["environment_color"], (0, 0, ROAD_X, HEIGHT))
        pygame.draw.rect(screen, levels[current_level]["environment_color"], (ROAD_X + ROAD_WIDTH, 0, WIDTH - (ROAD_X + ROAD_WIDTH), HEIGHT))
        
        # Draw environment objects
        for obj in self.trees:
            if levels[current_level]["name"] == "CITY" and obj["type"] == "tree":
                # Draw city trees
                pygame.draw.rect(screen, (139, 69, 19), 
                               (obj["x"] + obj["width"]//2 - 5, obj["y"] + obj["height"]//2, 
                                10, obj["height"]//2))
                pygame.draw.ellipse(screen, levels[current_level]["tree_color"], 
                                 (obj["x"], obj["y"], obj["width"], obj["height"]//2))
            
            elif levels[current_level]["name"] == "DESERT" and obj["type"] == "cactus":
                # Draw cacti
                pygame.draw.rect(screen, levels[current_level]["cactus_color"],
                               (obj["x"] + obj["width"]//2 - 3, obj["y"],
                                6, obj["height"]))
                pygame.draw.rect(screen, levels[current_level]["cactus_color"],
                               (obj["x"], obj["y"] + obj["height"]//3,
                                obj["width"], obj["height"]//3))
                # Cactus arms
                pygame.draw.rect(screen, levels[current_level]["cactus_color"],
                               (obj["x"] - 10, obj["y"] + obj["height"]//2, 
                                obj["width"]//2, 5))
                pygame.draw.rect(screen, levels[current_level]["cactus_color"],
                               (obj["x"] + obj["width"]//2 + 5, obj["y"] + obj["height"]//3, 
                                5, obj["height"]//3))
            
            elif levels[current_level]["name"] == "MOUNTAIN":
                if obj["type"] == "tree":
                    # Draw mountain trees (smaller and darker)
                    pygame.draw.rect(screen, (100, 50, 0),
                                   (obj["x"] + obj["width"]//2 - 3, obj["y"] + obj["height"]//2,
                                    6, obj["height"]//2))
                    pygame.draw.polygon(screen, levels[current_level]["tree_color"], [
                        (obj["x"] + obj["width"]//2, obj["y"]),
                        (obj["x"], obj["y"] + obj["height"]//2),
                        (obj["x"] + obj["width"], obj["y"] + obj["height"]//2)
                    ])
                elif obj["type"] == "rock":
                    # Draw rocks
                    pygame.draw.ellipse(screen, levels[current_level]["rock_color"],
                                      (obj["x"], obj["y"], obj["width"], obj["height"]))

        # Draw buildings (only for city level)
        if levels[current_level]["has_buildings"]:
            for building in self.buildings:
                pygame.draw.rect(screen, building["color"],
                               (building["x"], building["y"], building["width"], building["height"]))
                # Draw windows
                for i in range(3):
                    for j in range(4):
                        pygame.draw.rect(screen, BLACK,
                                       (building["x"] + 10 + j*25, building["y"] + 10 + i*25, 15, 15))

def update_weather():
    global current_weather, weather_change_time, weather_duration
    
    current_time = pygame.time.get_ticks()
    if current_time - weather_change_time > weather_duration:
        current_weather = random.choice(weather_types)
        weather_change_time = current_time
        weather_duration = random.randint(8000, 15000)

def update_rain():
    for drop in rain_drops:
        drop[1] += drop[2]
        drop[0] += random.randint(-1, 1)
        if drop[1] > HEIGHT:
            drop[1] = random.randint(-50, 0)
            drop[0] = random.randint(0, WIDTH)

def update_snow():
    for flake in snow_flakes:
        flake[1] += flake[3]
        flake[0] += flake[2]
        if flake[1] > HEIGHT:
            flake[1] = random.randint(-50, 0)
            flake[0] = random.randint(0, WIDTH)
        if flake[0] > WIDTH:
            flake[0] = 0
        elif flake[0] < 0:
            flake[0] = WIDTH

def draw_text(text, font, color, x, y, center=True):
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)
    return text_rect

def draw_button(text, font, color, bg_color, x, y, width, height):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, bg_color, button_rect, border_radius=10)
    pygame.draw.rect(screen, color, button_rect, 2, border_radius=10)
    text_rect = draw_text(text, font, color, x + width//2, y + height//2)
    return button_rect

def level_transition():
    global game_state, transition_alpha, transition_time
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, transition_alpha))
    screen.blit(overlay, (0, 0))
    
    # Draw level info
    level_name = levels[current_level]["name"]
    draw_text(f"ENTERING {level_name}", font_large, WHITE, WIDTH//2, HEIGHT//2)
    
    # Update transition effect
    current_time = pygame.time.get_ticks()
    if current_time - transition_time > 30:
        transition_alpha += 5
        if transition_alpha >= 180:
            transition_alpha = 180
            if current_time - transition_time > 1500:  # Show message for 1.5 seconds
                game_state = PLAYING

def show_menu():
    global game_state, running
    
    # Background
    screen.fill(LIGHT_BLUE)
    
    # Title
    draw_text("ULTIMATE RACER", font_large, BLUE, WIDTH//2, 100)
    
    # Buttons
    play_rect = draw_button("PLAY", font_medium, GREEN, BLACK, WIDTH//2 - 100, 200, 200, 50)
    
    if SCORE > 0:
        resume_rect = draw_button("RESUME", font_medium, YELLOW, BLACK, WIDTH//2 - 100, 270, 200, 50)
    
    quit_rect = draw_button("QUIT", font_medium, RED, BLACK, WIDTH//2 - 100, 340 if SCORE > 0 else 270, 200, 50)
    
    # Current high score
    draw_text(f"High Score: {HIGH_SCORE}", font_small, WHITE, WIDTH//2, 450)
    
    # Handle clicks
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    
    if mouse_clicked:
        if play_rect.collidepoint(mouse_pos):
            reset_game()
            game_state = PLAYING
            if engine_sound:
                engine_sound.play(-1)
                engine_sound.set_volume(0.5)
            if background_music:
                background_music.stop()
        elif SCORE > 0 and resume_rect.collidepoint(mouse_pos):
            game_state = PLAYING
            if engine_sound:
                engine_sound.play(-1)
                engine_sound.set_volume(0.5)
            if background_music:
                background_music.stop()
        elif quit_rect.collidepoint(mouse_pos):
            # Proper exit handling for both script and EXE
            running = False
            pygame.quit()
            if getattr(sys, 'frozen', False):
                os._exit(0)  # Force exit for EXE
            else:
                sys.exit(0)  # Clean exit for script

def reset_game():
    global SCORE, current_level, current_weather, weather_change_time, player, enemies, powerups, road
    
    SCORE = 0
    current_level = 0
    current_weather = "clear"
    weather_change_time = pygame.time.get_ticks()
    player = PlayerCar()
    enemies = []
    powerups = []
    road = Road()

# Initialize game objects
player = PlayerCar()
enemies = []
powerups = []
road = Road()
last_enemy_time = pygame.time.get_ticks()
last_powerup_time = pygame.time.get_ticks()
enemy_interval = levels[current_level]["enemy_interval"]
powerup_interval = 5000

# Transition variables
transition_alpha = 0
transition_time = 0

# Load high score
try:
    with open("highscore.txt", "r") as f:
        HIGH_SCORE = int(f.read())
except:
    HIGH_SCORE = 0

# Main game loop
running = True
try:
    while running:
        current_time = pygame.time.get_ticks()
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == PLAYING:
                        # Stop engine sound when going to menu
                        if engine_sound:
                            engine_sound.stop()
                        # Play background music when going to menu
                        if background_music:
                            background_music.play(-1)
                        game_state = MENU
                    elif game_state == MENU:
                        running = False
                if event.key == pygame.K_p and game_state == PLAYING:
                    # Pause engine sound
                    if engine_sound:
                        engine_sound.stop()
                    # Play background music when paused
                    if background_music:
                        background_music.play(-1)
                    game_state = PAUSED
                elif event.key == pygame.K_p and game_state == PAUSED:
                    # Resume engine sound
                    if engine_sound:
                        engine_sound.play(-1)
                    # Stop background music when unpausing
                    if background_music:
                        background_music.stop()
                    game_state = PLAYING
        
        # State management
        if game_state == MENU:
            show_menu()
        elif game_state == LEVEL_TRANSITION:
            road.update()
            road.draw()
            level_transition()
        elif game_state == PLAYING:
            # Progressive speed increase in mountain level
            if current_level == 2:  # Mountain level
                player.level3_speed_increase_timer += 1/FPS
                if player.level3_speed_increase_timer >= 0.5:  # Every half second
                    player.base_speed += player.level3_speed_increment
                    player.level3_speed_increase_timer = 0
                    
                    # Increase enemy speed
                    for enemy in enemies:
                        enemy.speed += player.level3_speed_increment * 0.9
                    
                    # Increase road scroll speed
                    road.speed += player.level3_speed_increment * 0.7
            
            # Update game state
            player.move()
            player.update_powerups(current_time)
            road.update()
            update_weather()
            
            if current_weather == "rain":
                update_rain()
            elif current_weather == "snow":
                update_snow()
            
            # Check level progression
            if current_level < len(levels) - 1 and SCORE >= levels[current_level + 1]["required_score"]:
                current_level += 1
                if level_up_sound:
                    level_up_sound.play()
                game_state = LEVEL_TRANSITION
                transition_alpha = 0
                transition_time = current_time
                road = Road()  # Reinitialize road with new settings
            
            # Spawn enemies
            if current_time - last_enemy_time > enemy_interval:
                enemies.append(EnemyCar())
                last_enemy_time = current_time
                enemy_interval = max(500, enemy_interval - 10)
            
            # Spawn power-ups
            if current_time - last_powerup_time > powerup_interval:
                powerups.append(PowerUp())
                last_powerup_time = current_time
                powerup_interval = random.randint(3000, 8000)
            
            # Handle enemy collisions
            for enemy in enemies[:]:
                if enemy.move():
                    enemies.remove(enemy)
                    SCORE += 1
                elif enemy.collide(player):
                    if player.shield:
                        enemies.remove(enemy)
                        SCORE += 1
                    else:
                        if crash_sound:
                            crash_sound.play()
                        if engine_sound:
                            engine_sound.stop()
                        # Play background music when game over
                        if background_music:
                            background_music.play(-1)
                        game_state = GAME_OVER
                        if SCORE > HIGH_SCORE:
                            HIGH_SCORE = SCORE
                            with open("highscore.txt", "w") as f:
                                f.write(str(HIGH_SCORE))
            
            # Handle power-up collisions
            for powerup in powerups[:]:
                if powerup.move():
                    powerups.remove(powerup)
                elif (player.x < powerup.x + powerup.width and
                      player.x + player.width > powerup.x and
                      player.y < powerup.y + powerup.height and
                      player.y + player.height > powerup.y):
                    powerups.remove(powerup)
                    if powerup_sound:
                        powerup_sound.play()
                    if powerup.type == "speed":
                        player.speed = player.base_speed + 3
                        player.speed_boost_end_time = current_time + POWERUP_DURATION
                    elif powerup.type == "shield":
                        player.shield = True
                        player.shield_end_time = current_time + POWERUP_DURATION
                    elif powerup.type == "points":
                        SCORE += 10
            
            # Drawing
            road.draw()
            
            for enemy in enemies:
                enemy.draw()
            
            for powerup in powerups:
                powerup.draw()
            
            player.draw()
            
            # Draw weather effects
            if current_weather == "rain":
                for drop in rain_drops:
                    pygame.draw.line(screen, (100, 100, 255), (drop[0], drop[1]), (drop[0], drop[1] + drop[3]), 1)
            elif current_weather == "snow":
                for flake in snow_flakes:
                    pygame.draw.circle(screen, WHITE, (int(flake[0]), int(flake[1])), 2)
            
            # Draw HUD
            draw_text(f"Score: {SCORE}", font_small, WHITE, 10, 10, False)
            draw_text(f"High Score: {HIGH_SCORE}", font_small, YELLOW, 10, 40, False)
            draw_text(f"Level: {current_level + 1}", font_small, WHITE, 10, 70, False)
            draw_text(f"Weather: {current_weather.capitalize()}", font_small, WHITE, WIDTH - 10, 70, False)
            
            if player.shield:
                draw_text("SHIELD ACTIVE", font_small, BLUE, WIDTH - 10, 10, False)
            if player.speed > player.base_speed:
                draw_text("SPEED BOOST", font_small, YELLOW, WIDTH - 10, 40, False)
            
            draw_text("ESC: Menu | P: Pause", font_small, WHITE, WIDTH//2, 10)
        
        elif game_state == PAUSED:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            draw_text("GAME PAUSED", font_large, WHITE, WIDTH//2, HEIGHT//2 - 50)
            draw_text("Press P to resume", font_medium, WHITE, WIDTH//2, HEIGHT//2 + 20)
        
        elif game_state == GAME_OVER:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            draw_text("GAME OVER", font_large, RED, WIDTH//2, HEIGHT//2 - 100)
            draw_text(f"Your Score: {SCORE}", font_medium, WHITE, WIDTH//2, HEIGHT//2 - 30)
            draw_text(f"High Score: {HIGH_SCORE}", font_medium, YELLOW, WIDTH//2, HEIGHT//2 + 20)
            
            # Main Menu button
            menu_rect = draw_button("MAIN MENU", font_medium, WHITE, BLACK, WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50)
            
            # Handle clicks
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = pygame.mouse.get_pressed()[0]
            
            if mouse_clicked and menu_rect.collidepoint(mouse_pos):
                game_state = MENU
        
        pygame.display.update()

except SystemExit:
    pass
finally:
    # Clean up pygame
    pygame.quit()
    # Exit the program
    if getattr(sys, 'frozen', False):
        os._exit(0)  # Force exit for EXE
    else:
        sys.exit(0)  # Clean exit for script