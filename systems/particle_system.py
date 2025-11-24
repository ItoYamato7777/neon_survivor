import pygame
import random

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.color = color
        self.life = 255
        self.size = random.randint(2, 5)

    def update(self):
        self.pos += self.velocity
        self.life -= 10 # Fade out speed
        if self.life < 0: self.life = 0

    def draw(self, surface):
        if self.life > 0:
            # Create a surface for the particle with alpha
            # We use a larger surface to avoid clipping if we add glow
            s = pygame.Surface((self.size*4, self.size*4), pygame.SRCALPHA)

            # Draw circle
            # Alpha is controlled by life
            alpha = max(0, min(255, int(self.life)))
            c = (*self.color, alpha)
            pygame.draw.circle(s, c, (self.size*2, self.size*2), self.size)

            # Blit with ADD blend mode for glow
            surface.blit(s, (self.pos.x - self.size*2, self.pos.y - self.size*2), special_flags=pygame.BLEND_ADD)

class ParticleManager:
    def __init__(self):
        self.particles = []

    def create_explosion(self, x, y, color):
        for _ in range(15):
            self.particles.append(Particle(x, y, color))

    def create_level_up_effect(self, x, y):
        colors = [(255, 215, 0), (0, 255, 255), (255, 255, 255)] # Gold, Cyan, White
        for _ in range(50):
            color = random.choice(colors)
            p = Particle(x, y, color)
            p.velocity = pygame.math.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
            p.life = 400 # Longer life
            self.particles.append(p)

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
