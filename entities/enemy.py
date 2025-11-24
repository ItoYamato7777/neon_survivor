import pygame
import math
import random
from settings import *

class Enemy:
    def __init__(self, x, y, type_name, projectile_manager=None):
        self.pos = pygame.math.Vector2(x, y)
        self.type = type_name
        self.projectile_manager = projectile_manager
        self.timer = 0 # General purpose timer
        self.state = "idle" # idle, charge, attack


        if self.type == 'square':
            self.color = COLOR_ENEMY_SQUARE
            self.speed = 2
            self.health = 30
            self.size = 20
            self.score_value = 10
        elif self.type == 'triangle':
            self.color = COLOR_ENEMY_TRIANGLE
            self.speed = 3.5
            self.health = 10
            self.size = 15
            self.score_value = 20
        elif self.type == 'hexagon':
            self.color = COLOR_ENEMY_HEXAGON
            self.speed = ENEMY_HEXAGON_SPEED
            self.health = ENEMY_HEXAGON_HEALTH
            self.size = 25
            self.score_value = ENEMY_HEXAGON_SCORE
            self.attack_range = ENEMY_HEXAGON_RANGE
        elif self.type == 'star':
            self.color = COLOR_ENEMY_STAR
            self.speed = ENEMY_STAR_SPEED
            self.health = ENEMY_STAR_HEALTH
            self.size = 20
            self.score_value = ENEMY_STAR_SCORE
        elif self.type == 'boss':
            self.color = COLOR_ENEMY_BOSS
            self.speed = 0.5
            self.health = ENEMY_BOSS_HEALTH
            self.size = ENEMY_BOSS_SIZE
            self.score_value = ENEMY_BOSS_SCORE
            self.max_health = ENEMY_BOSS_HEALTH


    def update(self, player_pos, dt):
        if self.type == 'square' or self.type == 'triangle':
            # Simple chase
            direction = player_pos - self.pos
            if direction.length() > 0:
                direction = direction.normalize()
            self.pos += direction * self.speed

        elif self.type == 'hexagon':
            dist = self.pos.distance_to(player_pos)
            if dist > self.attack_range:
                # Move closer
                direction = player_pos - self.pos
                if direction.length() > 0:
                    direction = direction.normalize()
                self.pos += direction * self.speed
            else:
                # Shoot
                self.timer += dt
                if self.timer > 2000: # Shoot every 2s
                    self.timer = 0
                    direction = player_pos - self.pos
                    if self.projectile_manager:
                        self.projectile_manager.add_projectile(self.pos.x, self.pos.y, direction, "enemy")

        elif self.type == 'star':
            if self.state == "idle":
                # Slow approach
                direction = player_pos - self.pos
                if direction.length() > 0:
                    self.pos += direction.normalize() * self.speed

                self.timer += dt
                if self.timer > 3000: # Charge every 3s
                    self.timer = 0
                    self.state = "charging"
                    self.charge_dir = (player_pos - self.pos).normalize()

            elif self.state == "charging":
                self.pos += self.charge_dir * ENEMY_STAR_DASH_SPEED
                self.timer += dt
                if self.timer > 500: # Dash for 0.5s
                    self.timer = 0
                    self.state = "idle"

        elif self.type == 'boss':
            # Move slowly towards center Y
            target_y = SCREEN_HEIGHT // 2
            if abs(self.pos.y - target_y) > 10:
                dir_y = 1 if target_y > self.pos.y else -1
                self.pos.y += dir_y * self.speed

            self.timer += dt
            if self.timer > 2000: # Attack every 2s
                self.timer = 0
                # Ring attack
                for angle in range(0, 360, 20):
                    direction = pygame.math.Vector2(1, 0).rotate(angle)
                    if self.projectile_manager:
                        self.projectile_manager.add_projectile(self.pos.x, self.pos.y, direction, "enemy")


    def draw(self, screen):
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = self.pos

        if self.type == 'square':
            pygame.draw.rect(screen, self.color, rect)
            # Glow
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, 100), (self.size//2, self.size//2, self.size, self.size))
            screen.blit(s, (self.pos.x - self.size, self.pos.y - self.size), special_flags=pygame.BLEND_ADD)

        elif self.type == 'triangle':
            # Calculate triangle points based on center
            half = self.size / 2
            points = [
                (self.pos.x, self.pos.y - half), # Top
                (self.pos.x - half, self.pos.y + half), # Bottom Left
                (self.pos.x + half, self.pos.y + half)  # Bottom Right
            ]
            pygame.draw.polygon(screen, self.color, points)

            # Glow (simplified as circle for triangle for performance/aesthetics)
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, 80), (self.size, self.size), self.size//1.5)
            screen.blit(s, (self.pos.x - self.size, self.pos.y - self.size), special_flags=pygame.BLEND_ADD)

        elif self.type == 'hexagon':
            # Draw Hexagon
            points = []
            for i in range(6):
                angle = math.radians(60 * i)
                x = self.pos.x + self.size * math.cos(angle)
                y = self.pos.y + self.size * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(screen, self.color, points)

        elif self.type == 'star':
            # Draw Star (simplified)
            points = []
            for i in range(10):
                angle = math.radians(36 * i - 90)
                radius = self.size if i % 2 == 0 else self.size / 2
                x = self.pos.x + radius * math.cos(angle)
                y = self.pos.y + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(screen, self.color, points)

        elif self.type == 'boss':
            # Draw Octagon
            points = []
            for i in range(8):
                angle = math.radians(45 * i)
                x = self.pos.x + self.size * math.cos(angle)
                y = self.pos.y + self.size * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(screen, self.color, points)

            # Boss Health Bar
            bar_width = 100
            bar_height = 10
            ratio = self.health / self.max_health
            pygame.draw.rect(screen, (50, 0, 0), (self.pos.x - bar_width//2, self.pos.y - self.size - 20, bar_width, bar_height))
            pygame.draw.rect(screen, (255, 0, 0), (self.pos.x - bar_width//2, self.pos.y - self.size - 20, bar_width * ratio, bar_height))


class EnemyManager:
    def __init__(self, projectile_manager):
        self.enemies = []
        self.spawn_timer = 0
        self.projectile_manager = projectile_manager
        self.boss_spawned = False


    def spawn_enemy(self, player_pos):
        # Spawn at edge of screen
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, SCREEN_WIDTH)
            y = -50
        elif side == 'bottom':
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 50
        elif side == 'left':
            x = -50
            y = random.randint(0, SCREEN_HEIGHT)
        elif side == 'right':
            x = SCREEN_WIDTH + 50
            y = random.randint(0, SCREEN_HEIGHT)

        type_name = random.choices(
            ['square', 'triangle', 'hexagon', 'star'],
            weights=[50, 30, 10, 10],
            k=1
        )[0]
        self.enemies.append(Enemy(x, y, type_name, self.projectile_manager))

    def spawn_boss(self):
        self.enemies.append(Enemy(SCREEN_WIDTH + 100, SCREEN_HEIGHT // 2, 'boss', self.projectile_manager))
        self.boss_spawned = True


    def update(self, dt, player_pos):
        self.spawn_timer += dt
        if self.spawn_timer >= ENEMY_SPAWN_RATE:
            self.spawn_timer = 0
            self.spawn_enemy(player_pos)

        for e in self.enemies:
            e.update(player_pos, dt)


    def draw(self, screen):
        for e in self.enemies:
            e.draw(screen)
