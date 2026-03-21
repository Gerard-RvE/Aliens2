import pygame
import sys
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound

# Screen setup (16:9 ratio)
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two-Player Space Invaders")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)  # Color for invincibility upgrade
ORANGE = (255, 165, 0)  # Color for fast shoot upgrade
CYAN = (0, 255, 255)  # Color for triple shot upgrade

# Load sound effects with error handling
def load_sound(filename):
    try:
        sound = pygame.mixer.Sound(filename)
        return sound
    except:
        print(f"Warning: Could not load sound file {filename}. Continuing without sound.")
        return None

shoot_sound = load_sound("shoot.wav")
hit_sound = load_sound("hit.wav")
game_over_sound = load_sound("game_over.wav")
upgrade_sound = load_sound("upgrade.wav")
life_lost_sound = load_sound("life_lost.wav")

game_over_played = False

# Draw player ship (triangle with base)
def draw_player_ship(surface, x, y, color):
    pygame.draw.polygon(surface, color, [(x + 10, y), (x, y + 20), (x + 20, y + 20)])
    pygame.draw.rect(surface, color, (x, y + 20, 20, 5))

# Draw alien (octopus style)
def draw_alien(surface, x, y, color):
    pygame.draw.ellipse(surface, color, (x, y, 20, 15))
    pygame.draw.circle(surface, WHITE, (x + 5, y + 5), 3)
    pygame.draw.circle(surface, WHITE, (x + 15, y + 5), 3)
    pygame.draw.circle(surface, BLACK, (x + 5, y + 5), 1)
    pygame.draw.circle(surface, BLACK, (x + 15, y + 5), 1)
    pygame.draw.line(surface, color, (x, y + 15), (x - 5, y + 20), 2)
    pygame.draw.line(surface, color, (x + 5, y + 15), (x + 5, y + 20), 2)
    pygame.draw.line(surface, color, (x + 15, y + 15), (x + 15, y + 20), 2)
    pygame.draw.line(surface, color, (x + 20, y + 15), (x + 25, y + 20), 2)

# Draw upgrade (star shape)
def draw_upgrade(surface, x, y, color):
    pygame.draw.polygon(surface, color, [
        (x + 10, y), (x + 14, y + 10), (x + 22, y + 10),
        (x + 16, y + 16), (x + 19, y + 26), (x + 10, y + 20),
        (x + 1, y + 26), (x + 4, y + 16), (x - 2, y + 10)
    ])

# Player class
class Player:
    def __init__(self, x, y, controls, side):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 25
        self.speed = 5
        self.controls = controls
        self.shoot_delay = 250  # milliseconds
        self.last_shot = 0
        self.side = side  # 0 for left, 1 for right
        self.lives = 10  # Each player starts with 10 lives
        self.upgrade_active = False
        self.upgrade_type = None
        self.upgrade_timer = 0
        self.upgrade_notification = None
        self.upgrade_notification_timer = 0

    def draw(self):
        # Change ship color based on upgrade
        if self.upgrade_active:
            if self.upgrade_type == "fast_shoot":
                draw_player_ship(screen, self.x, self.y, ORANGE)
            elif self.upgrade_type == "invincibility":
                draw_player_ship(screen, self.x, self.y, PURPLE)
            elif self.upgrade_type == "triple_shot":
                draw_player_ship(screen, self.x, self.y, CYAN)
        else:
            draw_player_ship(screen, self.x, self.y, GREEN)

    def move(self, keys):
        if keys[self.controls["left"]] and self.x > (0 if self.side == 0 else WIDTH//2):
            self.x -= self.speed
        if keys[self.controls["right"]] and self.x < (WIDTH//2 - self.width if self.side == 0 else WIDTH - self.width):
            self.x += self.speed
        if keys[self.controls["up"]] and self.y > 0:
            self.y -= self.speed
        if keys[self.controls["down"]] and self.y < HEIGHT - self.height:
            self.y += self.speed

    def shoot(self, keys):
        now = pygame.time.get_ticks()
        if keys[self.controls["shoot"]] and now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if shoot_sound:
                shoot_sound.play()
            if self.upgrade_active and self.upgrade_type == "triple_shot":
                # Fire three bullets: one straight, two angled
                middle_bullet = Bullet(self.x + self.width//2 - 2, self.y)
                left_bullet = Bullet(self.x + self.width//2 - 7, self.y)
                left_bullet.speed_x = -1  # Move left slightly
                right_bullet = Bullet(self.x + self.width//2 + 3, self.y)
                right_bullet.speed_x = 1   # Move right slightly
                return [middle_bullet, left_bullet, right_bullet]
            else:
                return Bullet(self.x + self.width//2 - 2, self.y)
        return None

# Alien class
class Alien:
    def __init__(self, x, y, side):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.speed_x = random.uniform(0.5, 3.5) * random.choice([-1, 1])
        self.speed_y = random.uniform(0.5, 1.5)  # Random vertical speed
        self.side = side  # 0 for left, 1 for right

    def draw(self):
        draw_alien(screen, self.x, self.y, RED)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        # Bounce off the sides of the screen half
        if self.side == 0:  # left side
            if self.x <= 0 or self.x + self.width >= WIDTH//2:
                self.speed_x *= -1
        else:  # right side
            if self.x <= WIDTH//2 or self.x + self.width >= WIDTH:
                self.speed_x *= -1

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = -7
        self.speed_x = 0  # Add horizontal speed

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

    def update(self):
        self.y += self.speed
        self.x += self.speed_x  # Update horizontal position

# Upgrade class
class Upgrade:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = 2
        self.type = random.choice(["fast_shoot", "invincibility", "triple_shot"])  # Added triple_shot

    def draw(self):
        draw_upgrade(screen, self.x, self.y, YELLOW)

    def update(self):
        self.y += self.speed

# Reset game
def reset_game():
    global left_player, right_player, aliens, bullets, upgrades, game_over, winner, game_started, game_over_played
    left_player = Player(100, HEIGHT - 50, {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s, "shoot": pygame.K_LCTRL}, 0)
    right_player = Player(WIDTH//2 + 100, HEIGHT - 50, {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN, "shoot": pygame.K_RSHIFT}, 1)
    aliens = [Alien(random.randint(0, WIDTH//2 - 25), 50, 0), Alien(random.randint(WIDTH//2, WIDTH - 25), 50, 1)]
    bullets = []
    upgrades = []
    game_over = False
    winner = None
    game_started = False
    game_over_played = False

# Initialize game
reset_game()

# Font
font = pygame.font.SysFont("Arial", 36)
notification_font = pygame.font.SysFont("Arial", 24)

# Main game loop
running = True
while running:
    screen.fill(BLACK)
    pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Use Spacebar to start/restart
                if not game_started or game_over:
                    reset_game()
                    game_started = True

    if not game_started:
        # Draw intro screen
        intro_text = font.render("Two-Player Space Invaders", True, WHITE)
        controls_text = font.render("Left: WASD to move, CTRL to shoot   Right: ARROWS to move, SHIFT to shoot", True, WHITE)
        start_text = font.render("Press SPACEBAR to start", True, WHITE)
        screen.blit(intro_text, (WIDTH//2 - intro_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT//2))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 + 60))
    elif game_over:
        # Draw game over screen
        if game_over_sound and not game_over_played:
            game_over_sound.play()
            game_over_played = True
        game_over_text = font.render(f"Player {winner} wins!", True, WHITE)
        restart_text = font.render("Press SPACEBAR to restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 30))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 30))
    else:
        # Game logic
        keys = pygame.key.get_pressed()

        # Player movement and shooting
        left_player.move(keys)
        right_player.move(keys)

        # Handle shooting for left player
        bullet = left_player.shoot(keys)
        if bullet:
            if isinstance(bullet, list):  # Handle triple shot
                bullets.extend(bullet)
            else:
                bullets.append(bullet)

        # Handle shooting for right player
        bullet = right_player.shoot(keys)
        if bullet:
            if isinstance(bullet, list):  # Handle triple shot
                bullets.extend(bullet)
            else:
                bullets.append(bullet)

        # Update bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.y < 0:
                bullets.remove(bullet)

        # Update aliens
        for alien in aliens[:]:
            alien.update()
            # Check if alien reached bottom
            if alien.y + alien.height >= HEIGHT:
                aliens.remove(alien)
                if alien.side == 0 and not left_player.upgrade_active:
                    left_player.lives -= 1
                    if life_lost_sound:
                        life_lost_sound.play()
                    if left_player.lives <= 0:
                        game_over = True
                        winner = "Right"
                elif alien.side == 1 and not right_player.upgrade_active:
                    right_player.lives -= 1
                    if life_lost_sound:
                        life_lost_sound.play()
                    if right_player.lives <= 0:
                        game_over = True
                        winner = "Left"
                # Spawn a new alien on the same side
                if alien.side == 0:
                    aliens.append(Alien(random.randint(0, WIDTH//2 - 25), 50, 0))
                else:
                    aliens.append(Alien(random.randint(WIDTH//2, WIDTH - 25), 50, 1))
                # Random chance to drop an upgrade (15%)
                if random.random() < 0.15:  # Increased drop rate
                    upgrades.append(Upgrade(alien.x, alien.y))

            # Check for bullet-alien collision
            for bullet in bullets[:]:
                if (alien.x < bullet.x < alien.x + alien.width and
                    alien.y < bullet.y < alien.y + alien.height):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if alien in aliens:
                        aliens.remove(alien)
                        if hit_sound:
                            hit_sound.play()
                        # Random chance to drop an upgrade (15%)
                        if random.random() < 0.15:  # Increased drop rate
                            upgrades.append(Upgrade(alien.x, alien.y))
                    # Spawn two new aliens on the other side
                    if alien.side == 0:
                        aliens.append(Alien(random.randint(WIDTH//2, WIDTH - 25), 50, 1))
                        aliens.append(Alien(random.randint(WIDTH//2, WIDTH - 25), 50, 1))
                    else:
                        aliens.append(Alien(random.randint(0, WIDTH//2 - 25), 50, 0))
                        aliens.append(Alien(random.randint(0, WIDTH//2 - 25), 50, 0))
                    break

        # Update upgrades
        for upgrade in upgrades[:]:
            upgrade.update()
            # Check if upgrade is collected by a player (more forgiving collision)
            for player in [left_player, right_player]:
                if (player.x - 10 < upgrade.x < player.x + player.width + 10 and
                    player.y - 10 < upgrade.y < player.y + player.height + 10):
                    player.upgrade_type = upgrade.type
                    if upgrade.type == "fast_shoot":
                        player.shoot_delay = 100  # Faster shooting
                        player.upgrade_notification = "Fast Shoot!"
                    elif upgrade.type == "invincibility":
                        player.upgrade_active = True
                        player.upgrade_timer = pygame.time.get_ticks() + 5000  # 5 seconds
                        player.upgrade_notification = "Invincibility!"
                    elif upgrade.type == "triple_shot":
                        player.upgrade_active = True
                        player.upgrade_type = "triple_shot"
                        player.upgrade_timer = pygame.time.get_ticks() + 5000  # 5 seconds
                        player.upgrade_notification = "Triple Shot!"
                    if upgrade_sound:
                        upgrade_sound.play()
                    player.upgrade_notification_timer = pygame.time.get_ticks() + 2000  # Show notification for 2 seconds
                    upgrades.remove(upgrade)
                    break  # Exit the loop once the upgrade is collected
            # Remove upgrades that fall off the screen
            if upgrade.y > HEIGHT:
                upgrades.remove(upgrade)

        # Check for upgrade timer
        for player in [left_player, right_player]:
            if player.upgrade_active and pygame.time.get_ticks() > player.upgrade_timer:
                player.upgrade_active = False
                player.shoot_delay = 250  # Reset shoot delay

        # Draw everything
        left_player.draw()
        right_player.draw()
        for alien in aliens:
            alien.draw()
        for bullet in bullets:
            bullet.draw()
        for upgrade in upgrades:
            upgrade.draw()

        # Draw stationary life counters (centered in each half)
        left_lives_x = (WIDTH//4) - (left_player.lives * 3.75)
        right_lives_x = (WIDTH//2 + WIDTH//4) - (right_player.lives * 3.75)
        for i in range(left_player.lives):
            pygame.draw.circle(screen, GREEN, (left_lives_x + i * 15, HEIGHT - 20), 5)
        for i in range(right_player.lives):
            pygame.draw.circle(screen, GREEN, (right_lives_x + i * 15, HEIGHT - 20), 5)

        # Draw upgrade notifications (centered in each half)
        for player in [left_player, right_player]:
            if player.upgrade_notification and pygame.time.get_ticks() < player.upgrade_notification_timer:
                notification_text = notification_font.render(player.upgrade_notification, True, YELLOW)
                x_pos = WIDTH//4 if player.side == 0 else WIDTH//2 + WIDTH//4
                screen.blit(notification_text, (x_pos - notification_text.get_width()//2, 50))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
