import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 150, 255)

# Physics Settings
GRAVITY = 0.25
AIR_RESISTANCE = 0.99
RECOIL_FORCE = 12.0
SPIN_SPEED_AIR = 0.15  # Auto-spin speed while in mid-air

# Setup Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gun Spinner - Recoil Physics Launcher")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)
large_font = pygame.font.SysFont("Arial", 48)

class Gun:
    def __init__(self):
        self.reset()

    def reset(self):
        # Initial positions
        self.x = 150
        self.y = SCREEN_HEIGHT - 120
        self.vx = 0
        self.vy = 0
        self.angle = 0  # In radians
        self.ammo = 9
        self.is_launched = False
        self.max_distance = 0
        self.game_over = False

    def update(self):
        if not self.is_launched:
            # Stationary on ground, just spinning gracefully waiting for launch
            self.angle += 0.05
        else:
            # Physics movement
            self.vy += GRAVITY
            self.vx *= AIR_RESISTANCE
            self.vy *= AIR_RESISTANCE
            
            self.x += self.vx
            self.y += self.vy
            
            # Spin the gun automatically in mid-air
            self.angle += SPIN_SPEED_AIR

            # Track maximum distance traveled
            if self.x - 150 > self.max_distance:
                self.max_distance = int(self.x - 150)

            # Check floor collision / Game Over boundary
            if self.y >= SCREEN_HEIGHT - 100:
                self.y = SCREEN_HEIGHT - 100
                self.vx = 0
                self.vy = 0
                if self.ammo <= 0 or (abs(self.vx) < 0.1 and abs(self.vy) < 0.1):
                    self.game_over = True

    def fire(self):
        if self.ammo > 0 and not self.game_over:
            self.ammo -= 1
            self.is_launched = True
            
            # Recoil math: force acts directly opposite to where the barrel points
            # Assuming gun barrel points to the "right" of its drawn structure
            self.vx -= math.cos(self.angle) * RECOIL_FORCE
            self.vy -= math.sin(self.angle) * RECOIL_FORCE
            
            # Spawn a bullet flare for visual effect
            return Bullet(self.x, self.y, self.angle)
        return None

    def draw(self, surface):
        # Programmatically draw a gun shape since we don't have external assets
        # Create a surface for the gun with transparency
        gun_surf = pygame.Surface((60, 40), pygame.SRCALPHA)
        
        # Draw Barrel
        pygame.draw.rect(gun_surf, GRAY, (20, 10, 40, 12))
        # Draw Grip
        pygame.draw.rect(gun_surf, RED, (10, 15, 12, 22))
        # Draw Trigger Guard area
        pygame.draw.rect(gun_surf, BLACK, (20, 22, 10, 8), 2)
        
        # Rotate the gun surface based on current angle
        # Deg = -Rad * 180 / PI because pygame coordinates invert Y axis
        rotated_surf = pygame.transform.rotate(gun_surf, -math.degrees(self.angle))
        new_rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
        
        surface.blit(rotated_surf, new_rect.topleft)

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        # Bullets travel forward out of the barrel
        self.vx = math.cos(angle) * 20
        self.vy = math.sin(angle) * 20
        self.life = 20  # Frames to live

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 4)


def draw_environment(surface, camera_x):
    # Draw simple scrolling ground lines and distance markers
    pygame.draw.rect(surface, GREEN, (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))
    pygame.draw.line(surface, WHITE, (0, SCREEN_HEIGHT - 80), (SCREEN_WIDTH, SCREEN_HEIGHT - 80), 4)
    
    # Calculate starting marker based on camera displacement
    start_marker = int(camera_x // 100) * 100
    for m in range(start_marker, start_marker + SCREEN_WIDTH + 200, 100):
        screen_pos = m - camera_x
        pygame.draw.line(surface, WHITE, (screen_pos, SCREEN_HEIGHT - 80), (screen_pos, SCREEN_HEIGHT - 60), 2)
        marker_text = font.render(f"{m}m", True, BLACK)
        surface.blit(marker_text, (screen_pos - 15, SCREEN_HEIGHT - 55))

def main():
    gun = Gun()
    bullets = []
    camera_x = 0

    running = True
    while running:
        clock.tick(FPS)
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if gun.game_over:
                        gun.reset()
                        bullets.clear()
                    else:
                        new_bullet = gun.fire()
                        if new_bullet:
                            bullets.append(new_bullet)
                            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if gun.game_over:
                        gun.reset()
                        bullets.clear()
                    else:
                        new_bullet = gun.fire()
                        if new_bullet:
                            bullets.append(new_bullet)

        # 2. Update Game Entities
        gun.update()
        
        for bullet in bullets[:]:
            bullet.update()
            if bullet.life <= 0:
                bullets.remove(bullet)

        # Camera dynamic follow logic (centers on gun horizontally once passed midpoint)
        if gun.x > SCREEN_WIDTH // 3:
            camera_x = gun.x - SCREEN_WIDTH // 3
        else:
            camera_x = 0

        # Adjust entities positions visually using camera offsets
        # We transform coordinates safely during drawing loop instead of altering physics positions
        
        # 3. Drawing Layout
        screen.fill(BLUE)  # Sky Background
        
        # Draw background and environment shifted by camera
        draw_environment(screen, camera_x)
        
        # Render gun with camera calculation offset
        original_gun_x = gun.x
        gun.x -= camera_x
        gun.draw(screen)
        gun.x = original_gun_x  # Restore exact physics property

        # Render bullets with camera calculation offset
        for bullet in bullets:
            original_bx = bullet.x
            bullet.x -= camera_x
            bullet.draw(screen)
            bullet.x = original_bx

        # UI Overlay (Stays static on screen)
        ammo_text = font.render(f"AMMO: {gun.ammo}", True, WHITE)
        dist_text = font.render(f"DISTANCE: {gun.max_distance} m", True, WHITE)
        screen.blit(ammo_text, (20, 20))
        screen.blit(dist_text, (20, 50))

        # Game Over state rendering
        if gun.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Semi-transparent backdrop
            screen.blit(overlay, (0,0))
            
            go_text = large_font.render("RUN FINISHED!", True, RED)
            score_text = font.render(f"Final Distance Traveled: {gun.max_distance} meters", True, WHITE)
            restart_text = font.render("Press SPACEBAR or CLICK to try again", True, GREEN)
            
            screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 200))
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 340))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
