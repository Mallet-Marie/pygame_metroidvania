import pygame as pg
from os import path
from settings import *

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.load_sprites()
        self.rect = self.cur_img.get_rect()
        self.rect.centerx, self.rect.centery = 200, 200
        self.is_jumping = False
        self.current_frame, self.last_frame_update = 0, 0
        self.velx = 0
        self.vely = 400 * self.game.dt

    def jump(self):
        pass

    def update(self, dt, actions):
        self.dx = actions["right"] - actions["left"]
        if actions['up'] and not self.is_jumping:
            self.is_jumping = True

        if self.is_jumping:
            if self.vely == 0:
                self.vely = -400 * dt
            else:
                self.vely += 50 * dt
            
            if self.vely > 400 * dt:
                self.is_jumping = False
        
        if self.rect.centery >= HEIGHT -50 and not self.is_jumping:
            self.vely = 0
        print(self.vely)
        self.velx = 200 * dt * self.dx
        self.rect.centerx += self.velx
        self.rect.centery += self.vely
        self.animate(dt, self.dx)
    
    def render(self, display):
        display.blit(self.cur_img, (self.rect.centerx, self.rect.centery))

    def animate(self, dt, dx):
        self.last_frame_update += dt

        if not(dx):
            self.cur_img = self.cur_anim_list[0]
            return

        if dx:
            if dx > 0:
                self.cur_anim_list = self.right_sprites
            else:
                self.cur_anim_list = self.left_sprites
        
        if self.last_frame_update > .15:
            self.last_frame_update = 0
            self.current_frame = (self.current_frame+1)%len(self.cur_anim_list)
            self.cur_img = self.cur_anim_list[self.current_frame]
    
    def load_sprites(self):
        self.sprite_dir = path.join(self.game.sprite_dir, "player")
        self.front_sprites, self.back_sprites, self.right_sprites, self.left_sprites = [], [], [], []

        for i in range(1, 5):
            self.front_sprites.append(pg.transform.scale2x(pg.image.load(path.join(self.sprite_dir, "player_front" + str(i) + ".png"))))
            self.back_sprites.append(pg.transform.scale2x(pg.image.load(path.join(self.sprite_dir, "player_back" + str(i) + ".png"))))
            self.right_sprites.append(pg.transform.scale2x(pg.image.load(path.join(self.sprite_dir, "player_right" + str(i) + ".png"))))
            self.left_sprites.append(pg.transform.scale2x(pg.image.load(path.join(self.sprite_dir, "player_left" + str(i) + ".png"))))
            
        self.cur_img = self.front_sprites[0]
        self.cur_anim_list = self.front_sprites