import pygame
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import randint, choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor')
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_menu = True  # Variable para controlar el menú de inicio

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # gun timer
        self.can_shoot = True
        self.shoot_time = 0 
        self.gun_cooldown = 100

        # enemy timer 
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        # setup
        self.setup()

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False

    def display_menu(self):
        # Colores y fuente del menú
        title_font = pygame.font.Font(None, 74)
        option_font = pygame.font.Font(None, 50)
        
        title_text = title_font.render("SURVIVOR", True, (255, 0, 0))
        play_text = option_font.render("1. JUGAR", True, (255, 255, 255))
        exit_text = option_font.render("2. SALIR", True, (255, 255, 255))

        # Posición de los elementos
        self.display_surface.fill((0, 0, 0))
        self.display_surface.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))
        self.display_surface.blit(play_text, (WINDOW_WIDTH // 2 - play_text.get_width() // 2, 300))
        self.display_surface.blit(exit_text, (WINDOW_WIDTH // 2 - exit_text.get_width() // 2, 400))
        pygame.display.flip()

    def menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Tecla 1 para jugar
                    self.show_menu = False
                elif event.key == pygame.K_2:  # Tecla 2 para salir
                    self.running = False

    def run(self):
        while self.running:
            if self.show_menu:
                self.display_menu()
                self.menu_events()
            else:
                # dt 
                dt = self.clock.tick() / 1000

                # event loop 
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                # update 
                self.gun_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()

                # draw
                self.display_surface.fill('black')
                self.all_sprites.draw(self.player.rect.center)
                pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
