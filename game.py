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
        self.enemy_manager = EnemyManager(self.projectile_manager)
        self.particle_manager = ParticleManager()
        self.font = pygame.font.SysFont("Arial", 24)
        self.score = 0
        self.score = 0
        self.game_over = False
        self.state = "PLAYING" # PLAYING, LEVEL_UP
        self.upgrade_options = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "LEVEL_UP":
                self.handle_level_up_input(event.key)
            elif event.key == pygame.K_r and self.game_over:
                self.__init__(self.screen) # Restart
            elif event.key == pygame.K_SPACE and not self.game_over:
                 # Pass space to player manually if needed, but player handles it via get_pressed
                 pass

    def update(self):
        if self.game_over:
            return

        if self.state == "LEVEL_UP":
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
                        self.add_xp(e.score_value) # Use score value as XP for now
                    break
            if hit:
                self.projectile_manager.projectiles.remove(p)

        # Enemy Projectiles vs Player
        for p in self.projectile_manager.projectiles[:]:
            if p.owner == "enemy":
                dist = p.pos.distance_to(self.player.pos)
                if dist < PLAYER_SIZE + p.radius:
                    self.player.health -= 10
                    self.projectile_manager.projectiles.remove(p)
                    self.particle_manager.create_explosion(self.player.pos.x, self.player.pos.y, COLOR_PLAYER)
                    if self.player.health <= 0:
                        self.game_over = True

        # Player vs Enemies
        for e in self.enemy_manager.enemies:
            dist = self.player.pos.distance_to(e.pos)
            if dist < PLAYER_SIZE + e.size:
                self.game_over = True
                self.particle_manager.create_explosion(self.player.pos.x, self.player.pos.y, COLOR_PLAYER)

    def add_xp(self, amount):
        self.player.xp += amount
        if self.player.xp >= self.player.xp_to_next_level:
            self.player.xp -= self.player.xp_to_next_level
            self.player.level += 1
            self.player.xp_to_next_level = int(self.player.xp_to_next_level * XP_GROWTH_FACTOR)
            self.trigger_level_up()

            # Boss Spawn Check
            if self.player.level % 5 == 0:
                self.enemy_manager.spawn_boss()

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

        # XP Bar
        self.draw_xp_bar()

        if self.state == "LEVEL_UP":
            self.draw_upgrade_menu()

    def add_xp(self, amount):
        self.player.xp += amount
        if self.player.xp >= self.player.xp_to_next_level:
            self.player.xp -= self.player.xp_to_next_level
            self.player.level += 1
            self.player.xp_to_next_level = int(self.player.xp_to_next_level * XP_GROWTH_FACTOR)
            self.trigger_level_up()

    def trigger_level_up(self):
        self.state = "LEVEL_UP"
        # Generate 3 options
        options = ["multishot", "damage", "speed"]
        self.upgrade_options = options # For now just static, could be random if we had more

    def handle_level_up_input(self, key):
        choice = -1
        if key == pygame.K_1: choice = 0
        elif key == pygame.K_2: choice = 1
        elif key == pygame.K_3: choice = 2

        if choice != -1 and choice < len(self.upgrade_options):
            upgrade_type = self.upgrade_options[choice]
            if self.player.upgrades[upgrade_type] < MAX_UPGRADE_LEVEL:
                self.player.upgrades[upgrade_type] += 1
                self.state = "PLAYING"
                self.particle_manager.create_level_up_effect(self.player.pos.x, self.player.pos.y)

    def draw_xp_bar(self):
        bar_width = SCREEN_WIDTH
        bar_height = 10
        ratio = self.player.xp / self.player.xp_to_next_level
        pygame.draw.rect(self.screen, (50, 50, 50), (0, SCREEN_HEIGHT - bar_height, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (0, SCREEN_HEIGHT - bar_height, bar_width * ratio, bar_height))

        level_text = self.font.render(f"LVL {self.player.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (10, SCREEN_HEIGHT - 40))

    def draw_upgrade_menu(self):
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_UI_BG)
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("LEVEL UP! Choose an Upgrade", True, COLOR_UI_TEXT)
        rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(title, rect)

        # Options
        start_y = 250
        gap = 100

        for i, option in enumerate(self.upgrade_options):
            level = self.player.upgrades[option]
            text_str = f"{i+1}. {option.upper()} (Lvl {level}/{MAX_UPGRADE_LEVEL})"
            if level >= MAX_UPGRADE_LEVEL:
                text_str += " - MAX"

            color = COLOR_UI_TEXT
            if level >= MAX_UPGRADE_LEVEL:
                color = (150, 150, 150)

            text = self.font.render(text_str, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH//2, start_y + i * gap))

            # Box
            box_rect = rect.inflate(40, 20)
            pygame.draw.rect(self.screen, COLOR_UI_SELECTED, box_rect, border_radius=10)
            pygame.draw.rect(self.screen, COLOR_UI_BORDER, box_rect, 2, border_radius=10)

            self.screen.blit(text, rect)

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
