import pygame
from settings import *

class Projectile:
    def __init__(self, x, y, direction):
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = direction.normalize() * 10
        self.radius = 4
        self.life = 100 # frames

    def update(self):
        self.pos += self.velocity
        self.life -= 1

    def draw(self, screen):
        # Draw glowing projectile
        # Core
        pygame.draw.circle(screen, COLOR_PROJECTILE, (int(self.pos.x), int(self.pos.y)), self.radius)
        # Glow (simple halo)
        s = pygame.Surface((self.radius*6, self.radius*6), pygame.SRCALPHA)
        pygame.draw.circle(s, (100, 255, 255, 100), (self.radius*3, self.radius*3), self.radius*2)
        screen.blit(s, (self.pos.x - self.radius*3, self.pos.y - self.radius*3), special_flags=pygame.BLEND_ADD)

class ProjectileManager:
    def __init__(self):
        self.projectiles = []

    def add_projectile(self, x, y, direction):
        self.projectiles.append(Projectile(x, y, direction))

    def update(self):
        for p in self.projectiles[:]:
            p.update()
            if p.life <= 0 or not (0 <= p.pos.x <= SCREEN_WIDTH and 0 <= p.pos.y <= SCREEN_HEIGHT):
                self.projectiles.remove(p)

    def draw(self, screen):
        for p in self.projectiles:
            p.draw(screen)
