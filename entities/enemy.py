import pygame
import math
import random
from settings import *

class Enemy:
    def __init__(self, x, y, type_name):
        self.pos = pygame.math.Vector2(x, y)
        self.type = type_name

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

    def update(self, player_pos):
        # Move towards player
        direction = player_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * self.speed

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

class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_timer = 0

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

        type_name = random.choice(['square', 'square', 'triangle']) # More squares
        self.enemies.append(Enemy(x, y, type_name))

    def update(self, dt, player_pos):
        self.spawn_timer += dt
        if self.spawn_timer >= ENEMY_SPAWN_RATE:
            self.spawn_timer = 0
            self.spawn_enemy(player_pos)

        for e in self.enemies:
            e.update(player_pos)

    def draw(self, screen):
        for e in self.enemies:
            e.draw(screen)
