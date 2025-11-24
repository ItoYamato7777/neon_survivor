import pygame
from settings import *

class Player:
    def __init__(self, x, y, projectile_manager):
        self.pos = pygame.math.Vector2(x, y)
        self.projectile_manager = projectile_manager
        self.last_shot_time = 0
        self.health = PLAYER_HEALTH

        # Skill state
        self.skill_active = False
        self.skill_timer = 0
        self.skill_cooldown_timer = 0
        self.trail_positions = []
        self.trail_timer = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
import pygame
from settings import *

class Player:
    def __init__(self, x, y, projectile_manager):
        self.pos = pygame.math.Vector2(x, y)
        self.projectile_manager = projectile_manager
        self.last_shot_time = 0
        self.health = PLAYER_HEALTH

        # Skill state
        self.skill_active = False
        self.skill_timer = 0
        self.skill_cooldown_timer = 0
        self.trail_positions = []
        self.trail_timer = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w]: direction.y = -1
        if keys[pygame.K_s]: direction.y = 1
        if keys[pygame.K_a]: direction.x = -1
        if keys[pygame.K_d]: direction.x = 1

        # Skill activation
        if keys[pygame.K_SPACE] and self.skill_cooldown_timer <= 0 and not self.skill_active:
            self.activate_skill()

        speed = PLAYER_SPEED
        if self.skill_active:
            speed *= SKILL_SPEED_MULTIPLIER

            # Add trail
            current_time = pygame.time.get_ticks()
            if current_time - self.trail_timer > 50: # Add trail every 50ms
                self.trail_positions.append((self.pos.copy(), 255)) # Pos, Alpha
                self.trail_timer = current_time

        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * speed

        # Clamp to screen
        self.pos.x = max(PLAYER_SIZE, min(SCREEN_WIDTH - PLAYER_SIZE, self.pos.x))
        self.pos.y = max(PLAYER_SIZE, min(SCREEN_HEIGHT - PLAYER_SIZE, self.pos.y))

    def activate_skill(self):
        self.skill_active = True
        self.skill_timer = SKILL_DURATION
        self.skill_cooldown_timer = SKILL_COOLDOWN

    def auto_attack(self, enemies, current_time):
        cooldown = PLAYER_ATTACK_COOLDOWN
        if self.skill_active:
            cooldown *= SKILL_ATTACK_COOLDOWN_MULTIPLIER

        if current_time - self.last_shot_time < cooldown:
            return

        # Find closest enemy
        closest_dist = float('inf')
        closest_enemy = None

        for enemy in enemies:
            dist = self.pos.distance_to(enemy.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_enemy = enemy

        if closest_enemy and closest_dist < 400: # Range check
            direction = closest_enemy.pos - self.pos
            self.projectile_manager.add_projectile(self.pos.x, self.pos.y, direction)
            self.last_shot_time = current_time

    def update(self, enemies):
        dt = 1000 / FPS # Approx

        # Update skill timers
        if self.skill_active:
            self.skill_timer -= dt
            if self.skill_timer <= 0:
                self.skill_active = False

        if self.skill_cooldown_timer > 0:
            self.skill_cooldown_timer -= dt

        self.handle_input()
        self.auto_attack(enemies, pygame.time.get_ticks())

    def draw(self, screen):
        # Draw trails
        for i, (pos, alpha) in enumerate(self.trail_positions):
            alpha -= 10
            if alpha <= 0:
                self.trail_positions.pop(i)
                continue
            self.trail_positions[i] = (pos, alpha)

            s = pygame.Surface((PLAYER_SIZE*2, PLAYER_SIZE*2), pygame.SRCALPHA)
            color = (*COLOR_SKILL_ACTIVE, int(alpha))
            pygame.draw.circle(s, color, (PLAYER_SIZE, PLAYER_SIZE), PLAYER_SIZE)
            screen.blit(s, (pos.x - PLAYER_SIZE, pos.y - PLAYER_SIZE), special_flags=pygame.BLEND_ADD)

        # Draw Player
        color = COLOR_SKILL_ACTIVE if self.skill_active else COLOR_PLAYER
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), PLAYER_SIZE)

        # Glow
        s = pygame.Surface((PLAYER_SIZE*4, PLAYER_SIZE*4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, 100), (PLAYER_SIZE*2, PLAYER_SIZE*2), PLAYER_SIZE + 5)
        screen.blit(s, (self.pos.x - PLAYER_SIZE*2, self.pos.y - PLAYER_SIZE*2), special_flags=pygame.BLEND_ADD)
