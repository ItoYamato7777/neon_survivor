import pygame
import sys
from settings import *
from entities.player import Player
from entities.enemy import EnemyManager
from entities.projectile import ProjectileManager
from systems.particle_system import ParticleManager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.projectile_manager = ProjectileManager()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.projectile_manager)
        self.enemy_manager = EnemyManager()
        self.particle_manager = ParticleManager()
        self.font = pygame.font.SysFont("Arial", 24)
        self.score = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.game_over:
                self.__init__(self.screen) # Restart

    def update(self):
        if self.game_over:
            return

        dt = 1000 / FPS # Approximate dt

        self.player.update(self.enemy_manager.enemies)
        self.enemy_manager.update(dt, self.player.pos)
        self.projectile_manager.update()
        self.particle_manager.update()

        self.check_collisions()

    def check_collisions(self):
        # Projectiles vs Enemies
        for p in self.projectile_manager.projectiles[:]:
            hit = False
            for e in self.enemy_manager.enemies[:]:
                dist = p.pos.distance_to(e.pos)
                if dist < e.size + p.radius:
                    e.health -= 10
                    hit = True
                    self.particle_manager.create_explosion(e.pos.x, e.pos.y, COLOR_PROJECTILE)

                    if e.health <= 0:
                        self.enemy_manager.enemies.remove(e)
                        self.particle_manager.create_explosion(e.pos.x, e.pos.y, e.color)
                        self.score += e.score_value
                    break
            if hit:
                self.projectile_manager.projectiles.remove(p)

        # Player vs Enemies
        for e in self.enemy_manager.enemies:
            dist = self.player.pos.distance_to(e.pos)
            if dist < PLAYER_SIZE + e.size:
                self.game_over = True
                self.particle_manager.create_explosion(self.player.pos.x, self.player.pos.y, COLOR_PLAYER)

    def draw(self):
        self.projectile_manager.draw(self.screen)
        self.particle_manager.draw(self.screen)
        self.enemy_manager.draw(self.screen)

        if not self.game_over:
            self.player.draw(self.screen)
        else:
            text = self.font.render("GAME OVER - Press R to Restart", True, (255, 255, 255))
            rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text, rect)

        # UI
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        # Skill UI
        self.draw_skill_ui()

    def draw_skill_ui(self):
        # Skill Icon/Bar Background
        ui_x = SCREEN_WIDTH - 120
        ui_y = 20
        width = 100
        height = 20

        pygame.draw.rect(self.screen, (50, 50, 50), (ui_x, ui_y, width, height))
        pygame.draw.rect(self.screen, (255, 255, 255), (ui_x, ui_y, width, height), 2)

        # Cooldown / Active Bar
        if self.player.skill_active:
            # Show duration remaining (Gold)
            ratio = self.player.skill_timer / SKILL_DURATION
            pygame.draw.rect(self.screen, COLOR_SKILL_ACTIVE, (ui_x, ui_y, width * ratio, height))
            text = self.font.render("ACTIVE!", True, COLOR_SKILL_ACTIVE)
            self.screen.blit(text, (ui_x, ui_y + 25))
        elif self.player.skill_cooldown_timer > 0:
            # Show cooldown (Gray/Red)
            ratio = 1 - (self.player.skill_cooldown_timer / SKILL_COOLDOWN)
            pygame.draw.rect(self.screen, (100, 100, 100), (ui_x, ui_y, width * ratio, height))
            text = self.font.render(f"{int(self.player.skill_cooldown_timer/1000)+1}s", True, (200, 200, 200))
            self.screen.blit(text, (ui_x + 35, ui_y - 2))
        else:
            # Ready (Cyan)
            pygame.draw.rect(self.screen, (0, 255, 255), (ui_x, ui_y, width, height))
            text = self.font.render("READY (SPACE)", True, (0, 255, 255))
            self.screen.blit(text, (ui_x - 20, ui_y + 25))
