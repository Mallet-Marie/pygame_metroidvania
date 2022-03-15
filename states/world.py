import pygame
from os import path
from states.state import State 
from states.pause import PauseMenu
from settings import *
from sprites import *

class World(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.all_sprites = pygame.sprite.Group()
        self.dependants = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.attacks = pygame.sprite.Group()
        self.mob_attacks = pygame.sprite.Group()
        self.mob_melee = pygame.sprite.Group()
        self.player = Player(self)
        self.mob = Ninja(self)
        self.mobs.add(self.mob)
        self.all_sprites.add(self.mob)
        self.mob = Samurai(self)
        self.mobs.add(self.mob)
        self.all_sprites.add(self.mob)
        self.dependants.add(self.player)
        self.all_sprites.add(self.player)

    def collide_hitbox(self, left, right):
        return left.hitbox.colliderect(right.hitbox)

    def collide_circle_hitbox(self, left, right):
        return left.hitbox.collide_circle(right.hitbox)
    
    def collide_circle_rect(self, right, left):
        circle_distance_x = abs(right.hitbox.centerx-left.hitbox.centerx)
        circle_distance_y = abs(right.hitbox.centery-left.hitbox.centery)
        if circle_distance_x > left.hitbox.w/2.0+right.radius or circle_distance_y > left.hitbox.h/2.0+right.radius:
            return False
        if circle_distance_x <= left.hitbox.w/2.0 or circle_distance_y <= left.hitbox.h/2.0:
            return True
        corner_x = circle_distance_x-left.hitbox.w/2.0
        corner_y = circle_distance_y-left.hitbox.h/2.0
        corner_distance_sq = corner_x**2.0 +corner_y**2.0
        return corner_distance_sq <= right.radius**2.0

    def update(self, dt, inputs):
        self.dt = dt
        if inputs["enter"]:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        self.dependants.update(self.dt, inputs)
        self.mob_attacks.update(self.dt)
        self.mobs.update(self.dt)
        sword_hits = pygame.sprite.groupcollide(self.attacks, self.mobs, False, True, self.collide_circle_rect)
        player_hits = pygame.sprite.spritecollide(self.player, self.mobs, False, self.collide_hitbox)
        mob_hits = pygame.sprite.spritecollide(self.player, self.mob_attacks, True, self.collide_hitbox)
        mob_melee_hits = pygame.sprite.spritecollide(self.player, self.mob_melee, True, self.collide_hitbox)
        if not self.player.invincible:
            for hit in mob_melee_hits:
                self.player.health -= 1
                if self.player.health <= 0:
                    self.player.kill()
                    self.game.playing = False
                    self.game.running = False
            for hit in mob_hits:
                self.player.health -= 1
                if self.player.health <= 0:
                    self.player.kill()
                    self.game.playing = False
                    self.game.running = False
            if player_hits:
                self.player.health -= 1
                if self.player.health <= 0:
                    self.player.kill()
                    self.game.playing = False
                    self.game.running = False

        parry_hits = pygame.sprite.groupcollide(self.attacks, self.mob_attacks, True, True, pygame.sprite.collide_circle)
        mob_melee_parry = pygame.sprite.groupcollide(self.attacks, self.mob_melee, True, True, pygame.sprite.collide_circle)

    def draw_health(self, display, x, y, health):
        for i in range(health):
            heart_img = pygame.Surface((10, 10))
            heart_img.fill(RED)
            heart_rect = heart_img.get_rect()
            heart_rect.centerx = x+15*i
            heart_rect.centery = y
            display.blit(heart_img, heart_rect)

    def draw(self, display):
        display.fill(WHITE) # Erase screen/draw background
        # *after* drawing everything, flip the display
        self.draw_health(display, 10, 10, self.player.health)
        self.all_sprites.draw(display)