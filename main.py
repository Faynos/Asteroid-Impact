import pygame
import sys
import math
import random

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Impact")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKBLUE = (10, 10, 40)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)

FPS = 60
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("arial", 24)
large_font = pygame.font.SysFont("arial", 36)
title_font = pygame.font.SysFont("arial", 72)

# Game states
STATE_HOME = 0
STATE_NAME_INPUT = 1
STATE_SOLAR_MAP = 2
STATE_QUESTION = 3
STATE_RESULT = 4
STATE_SHOP = 5
STATE_EARTH_SAVE = 6
STATE_GAME_END = 7
STATE_BOSS_QUESTION = 8
STATE_LORE = 9

state = STATE_HOME

# Player info
player_name = ""
name_input = ""

# Spaceship
spaceship_pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
spaceship_angle = 0
spaceship_velocity = pygame.Vector2(0, 0)
max_fuel = 100
spaceship_fuel = max_fuel

# Planets info for solar system animation
sun_pos = (WIDTH//2, HEIGHT//2)
planet_orbits = [80, 120, 160, 200, 240, 280]
planet_colors = [YELLOW, (200, 100, 0), (0, 100, 255), (150, 150, 150), (255, 165, 0), (160, 82, 45)]
planet_angles = [0.0 for _ in planet_orbits]

# Asteroid sites (fixed positions)
asteroid_sites = [
    (200, 150), (250, 400), (350, 300), (450, 500),
    (550, 250), (650, 350), (700, 450), (800, 200), (150, 500), (400, 100)
]

extracted_asteroids = 0
doolars = 0
earth_health = 100

# Boss asteroid variables
boss_asteroid_alive = False
boss_asteroid_pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
boss_asteroid_radius = 100
boss_questions_answered = 0

# Upgrades
upgrades = {
    "fuel_efficiency": False,
    "engine_speed": False,
    "extra_doolars": False,
    "fuel_replenish": False,
}

shop_items = [
    {"name": "Fuel Efficiency Upgrade", "cost": 50, "desc": "Consume 25% less fuel", "effect": "fuel_efficiency", "bought": False},
    {"name": "Engine Speed Upgrade", "cost": 75, "desc": "Ship moves faster", "effect": "engine_speed", "bought": False},
    {"name": "Extra Doolars", "cost": 100, "desc": "Earn more doolars per correct answer", "effect": "extra_doolars", "bought": False},
    {"name": "Fuel Replenish Boost", "cost": 100, "desc": "Get more fuel after extraction", "effect": "fuel_replenish", "bought": False},
]

# Questions
normal_questions = [
    {"q": "What planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Saturn"], "answer": 1},
    {"q": "What is the center of our solar system?", "options": ["Moon", "Sun", "Earth", "Mars"], "answer": 1},
    {"q": "Which planet has rings?", "options": ["Venus", "Mars", "Saturn", "Mercury"], "answer": 2},
    {"q": "What force keeps planets in orbit?", "options": ["Gravity", "Magnetism", "Electricity", "Friction"], "answer": 0},
    {"q": "Which planet is closest to the Sun?", "options": ["Earth", "Venus", "Mercury", "Mars"], "answer": 2},
]

boss_questions = [
    {"q": "What is a light year?", "options": ["Time", "Distance", "Speed", "Brightness"], "answer": 1},
    {"q": "Which planet is largest?", "options": ["Earth", "Jupiter", "Saturn", "Neptune"], "answer": 1},
    {"q": "What does NASA stand for?", "options": ["National Aeronautics and Space Administration", "National Air and Space Agency", "North American Space Association", "National Aerospace Service Alliance"], "answer": 0},
    {"q": "What galaxy do we live in?", "options": ["Andromeda", "Milky Way", "Sombrero", "Whirlpool"], "answer": 1},
    {"q": "Which element fuels the Sun?", "options": ["Hydrogen", "Oxygen", "Helium", "Carbon"], "answer": 0},
]

question_data = {
    "q": "",
    "options": [],
    "answer": 0,
    "type": "normal"
}

selected_option = None
result_texts = []

# UI Button class for Home screen
class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback

    def draw(self):
        pygame.draw.rect(screen, DARKBLUE, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        text_surf = font.render(self.text, True, WHITE)
        screen.blit(text_surf, (self.rect.x + (self.rect.width - text_surf.get_width()) // 2,
                                self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

def start_game():
    global state
    state = STATE_NAME_INPUT

def show_lore():
    global state
    state = STATE_LORE

home_buttons = [
    Button("Start Game", WIDTH//2 - 100, 300, 200, 50, start_game),
    Button("Lore / Info", WIDTH//2 - 100, 370, 200, 50, show_lore),
    Button("Quit", WIDTH//2 - 100, 440, 200, 50, lambda: sys.exit()),
]

# Drawing functions
def draw_solar_system():
    # Draw sun
    pygame.draw.circle(screen, YELLOW, sun_pos, 40)
    # Draw planets orbiting
    for i, orbit in enumerate(planet_orbits):
        x = sun_pos[0] + math.cos(planet_angles[i]) * orbit
        y = sun_pos[1] + math.sin(planet_angles[i]) * orbit
        pygame.draw.circle(screen, planet_colors[i], (int(x), int(y)), 15)

def draw_asteroids():
    for (x, y) in asteroid_sites:
        pygame.draw.circle(screen, WHITE, (x, y), 15)

def draw_spaceship(pos, angle):
    points = []
    # Simple triangle ship shape
    size = 20
    points.append((pos.x + math.cos(angle) * size, pos.y + math.sin(angle) * size))
    points.append((pos.x + math.cos(angle + 2.5) * size * 0.6, pos.y + math.sin(angle + 2.5) * size * 0.6))
    points.append((pos.x + math.cos(angle - 2.5) * size * 0.6, pos.y + math.sin(angle - 2.5) * size * 0.6))
    pygame.draw.polygon(screen, GREEN, points)

def draw_ui():
    fuel_text = font.render(f"Fuel: {int(spaceship_fuel)} / {max_fuel}", True, WHITE)
    screen.blit(fuel_text, (10, 10))
    doolar_text = font.render(f"Doolars: {doolars}", True, WHITE)
    screen.blit(doolar_text, (10, 40))
    health_text = font.render(f"Earth Health: {earth_health}%", True, WHITE)
    screen.blit(health_text, (10, 70))
    asteroid_text = font.render(f"Asteroids Extracted: {extracted_asteroids}", True, WHITE)
    screen.blit(asteroid_text, (10, 100))
    if boss_asteroid_alive:
        boss_text = font.render("Boss Asteroid Incoming!", True, RED)
        screen.blit(boss_text, (WIDTH//2 - boss_text.get_width()//2, 10))

def draw_shop():
    y = 100
    screen.blit(title_font.render("Upgrade Shop", True, WHITE), (WIDTH//2 - 150, 40))
    for idx, item in enumerate(shop_items):
        status = "Bought" if item["bought"] else f"Cost: {item['cost']}"
        color = GREEN if item["bought"] else WHITE
        pygame.draw.rect(screen, DARKBLUE, (100, y - 10, 700, 50))
        name_text = font.render(f"{idx+1}. {item['name']} - {status}", True, color)
        desc_text = font.render(item['desc'], True, WHITE)
        screen.blit(name_text, (110, y))
        screen.blit(desc_text, (110, y + 25))
        y += 80
    screen.blit(font.render("Press number key to buy upgrade or B to exit shop.", True, WHITE), (100, y + 20))

def earth_save_animation():
    for radius in range(0, 150, 4):
        screen.fill(BLACK)
        draw_solar_system()
        pygame.draw.circle(screen, GREEN, sun_pos, radius, 5)
        pygame.display.flip()
        pygame.time.delay(20)

def draw_game_end():
    screen.fill(BLACK)
    screen.blit(title_font.render("GAME END", True, WHITE), (WIDTH//2 - 100, HEIGHT//2 - 100))
    lines = [
        "Made by:",
        "Faiyaz Eisa Mustaeen and Shennon Fernando",
        "from Gleneagles Secondary College",
        "for Science Talent Search"
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, WHITE), (WIDTH//2 - 220, HEIGHT//2 - 20 + i*40))

def boss_intro_cutscene():
    screen.fill(BLACK)
    text1 = large_font.render("WARNING!", True, RED)
    text2 = font.render("A giant asteroid is heading to Earth!", True, RED)
    text3 = font.render("Answer correctly to stop it!", True, WHITE)
    screen.blit(text1, (WIDTH//2 - 100, HEIGHT//2 - 80))
    screen.blit(text2, (WIDTH//2 - 220, HEIGHT//2))
    screen.blit(text3, (WIDTH//2 - 160, HEIGHT//2 + 40))
    pygame.display.flip()
    pygame.time.wait(3000)

def check_asteroid_collision():
    global extracted_asteroids, spaceship_fuel, doolars, state, selected_option, boss_asteroid_alive, boss_questions_answered, boss_asteroid_radius, earth_health

    # Check normal asteroids first
    for i, (ax, ay) in enumerate(asteroid_sites):
        dist = math.hypot(spaceship_pos.x - ax, spaceship_pos.y - ay)
        if dist < 30:
            # Extract asteroid
            del asteroid_sites[i]
            extracted_asteroids += 1

            # Fuel replenish on extraction
            fuel_replenish = 15
            if upgrades["fuel_replenish"]:
                fuel_replenish = 25
            spaceship_fuel = min(max_fuel, spaceship_fuel + fuel_replenish)

            # Prepare question for normal asteroid
            selected_option = None
            current_question = random.choice(normal_questions)
            question_data["q"] = current_question["q"]
            question_data["options"] = current_question["options"]
            question_data["answer"] = current_question["answer"]
            question_data["type"] = "normal"
            state = STATE_QUESTION
            return

    # If boss alive, check collision with boss asteroid
    if boss_asteroid_alive:
        dist = spaceship_pos.distance_to(boss_asteroid_pos)
        if dist < boss_asteroid_radius + 20:
            # Fuel replenish on boss asteroid hit
            fuel_replenish = 20
            if upgrades["fuel_replenish"]:
                fuel_replenish = 30
            spaceship_fuel = min(max_fuel, spaceship_fuel + fuel_replenish)

            # Prepare boss question
            selected_option = None
            current_question = boss_questions[boss_questions_answered]
            question_data["q"] = current_question["q"]
            question_data["options"] = current_question["options"]
            question_data["answer"] = current_question["answer"]
            question_data["type"] = "boss"
            state = STATE_BOSS_QUESTION
            return

def submit_answer(answer_idx):
    global state, doolars, earth_health, selected_option, boss_questions_answered, boss_asteroid_alive, boss_asteroid_radius, result_texts

    correct = (answer_idx == question_data["answer"])

    if question_data["type"] == "normal":
        if correct:
            gain = 10
            if upgrades["extra_doolars"]:
                gain = 15
            doolars += gain
            state = STATE_RESULT
            result_texts = [f"Correct! +{gain} Doolars and fuel refilled."]
        else:
            earth_health -= 10
            if earth_health < 0:
                earth_health = 0
            state = STATE_RESULT
            result_texts = ["Wrong! Earth health -10%."]

    elif question_data["type"] == "boss":
        if correct:
            boss_questions_answered += 1
            boss_asteroid_radius -= 15
            gain = 25
            if upgrades["extra_doolars"]:
                gain = 35
            doolars += gain
            result_texts = [f"Correct! Boss asteroid shrinks! +{gain} Doolars."]
            if boss_questions_answered >= len(boss_questions):
                # Boss defeated
                boss_asteroid_alive = False
                state = STATE_EARTH_SAVE
                return
        else:
            earth_health -= 20
            if earth_health < 0:
                earth_health = 0
            result_texts = ["Wrong! Boss asteroid still threatens Earth! Earth health -20%."]

        state = STATE_RESULT

def handle_name_input(event):
    global name_input, player_name, state
    if event.key == pygame.K_BACKSPACE:
        name_input = name_input[:-1]
    elif event.key == pygame.K_RETURN:
        if len(name_input) > 0:
            player_name = name_input
            name_input = ""
            # Move to solar map after name input
            global spaceship_pos, spaceship_velocity
            spaceship_pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
            spaceship_velocity = pygame.Vector2(0, 0)
            global extracted_asteroids, doolars, earth_health, boss_asteroid_alive, boss_questions_answered, boss_asteroid_radius
            extracted_asteroids = 0
            doolars = 0
            earth_health = 100
            boss_asteroid_alive = False
            boss_questions_answered = 0
            boss_asteroid_radius = 100
            # Reset shop upgrades
            for item in shop_items:
                item["bought"] = False
            for key in upgrades:
                upgrades[key] = False
            global spaceship_fuel, max_fuel
            max_fuel = 100
            spaceship_fuel = max_fuel
            state = STATE_SOLAR_MAP
    else:
        if len(name_input) < 12 and event.unicode.isalpha():
            name_input += event.unicode

def draw_lore():
    screen.fill(BLACK)
    lines = [
        "Asteroid Impact",
        "----------------------------------",
        "You are a space miner and scientist.",
        "Extract asteroids and answer science questions to earn Doolars.",
        "Use Doolars to buy upgrades in the shop.",
        "After mining 10 asteroids, a boss asteroid threatens Earth.",
        "Answer all boss questions correctly to save Earth.",
        "Wrong answers damage Earth's health.",
        "If Earth's health reaches 0, it's game over.",
        "Good luck!",
        "",
        "Press B to go back to main menu."
    ]
    for i, line in enumerate(lines):
        screen.blit(font.render(line, True, WHITE), (40, 40 + i*30))

def main():
    global state, selected_option, spaceship_angle, spaceship_pos, spaceship_velocity, spaceship_fuel, doolars, extracted_asteroids, boss_asteroid_alive, boss_questions_answered, boss_asteroid_radius, earth_health

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Input handling based on state
            if state == STATE_HOME:
                for btn in home_buttons:
                    btn.handle_event(event)

            elif state == STATE_NAME_INPUT:
                if event.type == pygame.KEYDOWN:
                    handle_name_input(event)

            elif state == STATE_SOLAR_MAP:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        state = STATE_SHOP

            elif state == STATE_QUESTION or state == STATE_BOSS_QUESTION:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        selected_option = event.key - pygame.K_1
                        submit_answer(selected_option)

            elif state == STATE_RESULT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Return to solar map or game end if earth health zero
                        if earth_health <= 0:
                            state = STATE_GAME_END
                        else:
                            if boss_asteroid_alive and question_data["type"] == "boss":
                                # Continue boss questions or solar map after result
                                if boss_questions_answered >= len(boss_questions):
                                    state = STATE_EARTH_SAVE
                                else:
                                    state = STATE_SOLAR_MAP
                            else:
                                state = STATE_SOLAR_MAP

            elif state == STATE_SHOP:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        state = STATE_SOLAR_MAP
                    elif event.unicode in ['1', '2', '3', '4']:
                        idx = int(event.unicode) - 1
                        item = shop_items[idx]
                        if not item["bought"] and doolars >= item["cost"]:
                            doolars -= item["cost"]
                            item["bought"] = True
                            upgrades[item["effect"]] = True
                            # Apply upgrades effects immediately
                            if item["effect"] == "fuel_efficiency":
                                pass  # Fuel consumption handled below
                            elif item["effect"] == "engine_speed":
                                pass  # Speed handled below
                            elif item["effect"] == "extra_doolars":
                                pass
                            elif item["effect"] == "fuel_replenish":
                                pass

            elif state == STATE_EARTH_SAVE:
                # Skip input during animation
                pass

            elif state == STATE_GAME_END:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        state = STATE_HOME

            elif state == STATE_LORE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        state = STATE_HOME

        # Update and draw based on state
        if state == STATE_HOME:
            screen.fill(DARKBLUE)
            title_text = title_font.render("Asteroid Impact", True, WHITE)
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
            for btn in home_buttons:
                btn.draw()

        elif state == STATE_NAME_INPUT:
            screen.fill(BLACK)
            prompt = font.render("Enter your name (letters only): " + name_input, True, WHITE)
            screen.blit(prompt, (50, HEIGHT//2))

        elif state == STATE_SOLAR_MAP:
            screen.fill(BLACK)
            # Update planet positions
            for i in range(len(planet_angles)):
                planet_angles[i] += 0.01 + i * 0.001
            draw_solar_system()
            draw_asteroids()
            draw_spaceship(spaceship_pos, spaceship_angle)
            draw_ui()

            # Spaceship movement
            keys = pygame.key.get_pressed()
            acceleration = 0.15
            if upgrades["engine_speed"]:
                acceleration = 0.25

            if keys[pygame.K_LEFT]:
                spaceship_angle -= 0.05
            if keys[pygame.K_RIGHT]:
                spaceship_angle += 0.05
            if keys[pygame.K_UP]:
                # Consume fuel with efficiency upgrade check
                fuel_cost = 0.3
                if upgrades["fuel_efficiency"]:
                    fuel_cost = 0.22
                if spaceship_fuel > 0:
                    spaceship_velocity.x += math.cos(spaceship_angle) * acceleration
                    spaceship_velocity.y += math.sin(spaceship_angle) * acceleration
                    spaceship_fuel -= fuel_cost
                    if spaceship_fuel < 0:
                        spaceship_fuel = 0

            # Apply friction and update position
            spaceship_velocity *= 0.97
            spaceship_pos += spaceship_velocity

            # Bounce off edges
            if spaceship_pos.x < 0:
                spaceship_pos.x = 0
                spaceship_velocity.x = -spaceship_velocity.x * 0.6
            if spaceship_pos.x > WIDTH:
                spaceship_pos.x = WIDTH
                spaceship_velocity.x = -spaceship_velocity.x * 0.6
            if spaceship_pos.y < 0:
                spaceship_pos.y = 0
                spaceship_velocity.y = -spaceship_velocity.y * 0.6
            if spaceship_pos.y > HEIGHT:
                spaceship_pos.y = HEIGHT
                spaceship_velocity.y = -spaceship_velocity.y * 0.6

            check_asteroid_collision()

            # Boss asteroid trigger
            if extracted_asteroids >= 10 and not boss_asteroid_alive:
                boss_intro_cutscene()
                boss_asteroid_alive = True
                boss_questions_answered = 0
                boss_asteroid_radius = 100
                boss_asteroid_pos.update(WIDTH//2, HEIGHT//2)

            # Draw boss asteroid if alive
            if boss_asteroid_alive:
                pygame.draw.circle(screen, RED, (int(boss_asteroid_pos.x), int(boss_asteroid_pos.y)), boss_asteroid_radius)

        elif state == STATE_QUESTION:
            screen.fill(BLACK)
            question_surface = large_font.render(question_data["q"], True, WHITE)
            screen.blit(question_surface, (50, 100))
            for i, option in enumerate(question_data["options"]):
                color = GREEN if selected_option == i else WHITE
                option_surface = font.render(f"{i+1}. {option}", True, color)
                screen.blit(option_surface, (100, 200 + i*40))
            screen.blit(font.render("Press 1-4 to answer.", True, WHITE), (50, 500))

        elif state == STATE_BOSS_QUESTION:
            screen.fill(BLACK)
            question_surface = large_font.render(question_data["q"], True, WHITE)
            screen.blit(question_surface, (50, 100))
            for i, option in enumerate(question_data["options"]):
                color = GREEN if selected_option == i else WHITE
                option_surface = font.render(f"{i+1}. {option}", True, color)
                screen.blit(option_surface, (100, 200 + i*40))
            pygame.draw.circle(screen, RED, (int(boss_asteroid_pos.x), int(boss_asteroid_pos.y)), boss_asteroid_radius)
            screen.blit(font.render("Press 1-4 to answer.", True, WHITE), (50, 500))

        elif state == STATE_RESULT:
            screen.fill(BLACK)
            for i, text in enumerate(result_texts):
                color = GREEN if "Correct" in text else RED
                result_surface = font.render(text, True, color)
                screen.blit(result_surface, (100, 200 + i*30))
            screen.blit(font.render("Press Enter to continue.", True, WHITE), (100, 500))

        elif state == STATE_SHOP:
            screen.fill(BLACK)
            draw_shop()

        elif state == STATE_EARTH_SAVE:
            earth_save_animation()

        elif state == STATE_GAME_END:
            screen.fill(BLACK)
            if earth_health <= 0:
                lose_text = title_font.render("Earth Destroyed!", True, RED)
                screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, HEIGHT//2 - 50))
                screen.blit(font.render("Press Enter to return to main menu.", True, WHITE), (WIDTH//2 - 180, HEIGHT//2 + 20))
            else:
                win_text = title_font.render("Earth Saved! Congratulations!", True, GREEN)
                screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
                screen.blit(font.render("Press Enter to return to main menu.", True, WHITE), (WIDTH//2 - 220, HEIGHT//2 + 20))
            # Credits
            credit_lines = [
                "Game by Faiyaz",
                "Powered by Pygame",
                "Science questions sourced from public domain"
            ]
            for i, line in enumerate(credit_lines):
                screen.blit(font.render(line, True, WHITE), (WIDTH//2 - 140, HEIGHT//2 + 80 + i*30))

        elif state == STATE_LORE:
            draw_lore()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()



