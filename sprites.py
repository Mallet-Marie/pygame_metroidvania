import pygame
import math
from pygame.constants import *
from settings import *
from os import path
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.load_images()
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.hitbox.inflate_ip(-104, -70)
        self.hitbox.move_ip(0, 35)
        self.rect.topleft = pos[0], pos[1]
        self.posx, self.posy = self.rect.topleft
        self.hitbox.center = self.rect.centerx, self.rect.centery+29
        self.health = 20
        self.velx = 0
        self.vely = 0
        self.acc = .5
        self.dx = 0
        self.jumps = 2
        self.jumping = True
        self.on_ground = False
        self.attacking = False
        self.invincible = False
        self.can_attack = True
        self.hit = False
        self.last_attack = pygame.time.get_ticks()
        self.end_game = pygame.time.get_ticks()
        self.attack_delay = 500
        self.sword = pygame.sprite.Sprite()
        self.been_hit = False
        self.frame, self.last_frame_update = 0, 0
        self.anim_list = self.r_idle
        self.facing_left, self.facing_right = False, True
        #pygame.draw.rect(self.image, GREEN, self.hitbox, 1) #hitbox
        self.iframes = pygame.time.get_ticks()

    def animate(self, dt):
        self.last_frame_update += dt
        if (self.anim_list == self.r_hit or self.anim_list == self.l_hit) and self.frame == len(self.anim_list)-1:
            self.hit = False
            
        if (self.anim_list == self.r_attack or self.anim_list == self.l_attack) and self.frame == len(self.anim_list)-3:
            if not self.sword.alive():
                if self.facing_left:
                    self.sword = Sword(self.posx-8, self.posy+8, 80, 80, 40, self.game)
                elif self.facing_right:
                    self.sword = Sword(self.posx+32, self.posy+8, 80, 80, 40, self.game)
                else:
                    self.sword = Sword(self.posx+32, self.posy+8, 80, 80, 40, self.game)
                self.game.attacks.add(self.sword)
                self.game.all_sprites.add(self.sword)

        if (self.anim_list == self.r_attack or self.anim_list == self.l_attack) and self.frame == len(self.anim_list)-1:
            self.attacking = False
        
        if self.health > 0:
            if self.attacking:
                if self.facing_left:
                    self.anim_list = self.l_attack
                elif self.facing_right:
                    self.anim_list = self.r_attack
                else:
                    self.anim_list = self.r_attack

            if self.hit:
                self.attacking = False
                if self.velx < 0:
                    self.anim_list = self.l_hit
                elif self.velx >= 0:
                    self.anim_list = self.r_hit

            if not self.hit and not self.attacking:
                if self.velx == 0:
                    if self.facing_left:
                        self.anim_list = self.l_idle
                    elif self.facing_right:
                        self.anim_list = self.r_idle
                else:
                    if self.facing_left:
                        self.anim_list = self.l_walk
                    elif self.facing_right:
                        self.anim_list = self.r_walk           

        if self.last_frame_update > 60/8:
            self.last_frame_update = 0
            self.frame = (self.frame+1)%len(self.anim_list)
            self.image = self.anim_list[self.frame]

    def load_images(self):
        self.l_walk = self.game.game.player_anims["l_walk"]
        self.r_walk = self.game.game.player_anims["r_walk"]
        self.l_attack = self.game.game.player_anims["l_attack"]
        self.r_attack = self.game.game.player_anims["r_attack"]
        self.l_idle = self.game.game.player_anims["l_idle"]
        self.r_idle = self.game.game.player_anims["r_idle"]
        self.l_hit = self.game.game.player_anims["l_hit"]
        self.r_hit = self.game.game.player_anims["r_hit"]
        self.l_kill = self.game.game.player_anims["l_kill"]
        self.r_kill = self.game.game.player_anims["r_kill"]

        self.image = self.l_walk[0]

    def horizontal_movement(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False, self.game.collide_hitbox)
        if hits:
            if self.dx > 0:
                self.posx = hits[0].hitbox.left - self.hitbox.width
            if self.dx < 0:
                self.posx = hits[0].hitbox.right
            self.velx = 0
            self.rect.x = self.posx-52
            self.hitbox.x = self.posx

    def vertical_movement(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False, self.game.collide_hitbox)
        if hits:
            if self.vely > 0:
                self.posy = hits[0].hitbox.top - self.hitbox.height
                self.on_ground = True
                self.vely = 0
                self.jumps = 2
                self.hitbox.y = self.posy
                self.rect.y = self.posy-70
            if self.vely < 0:
                self.vely = 0
                self.posy = hits[0].hitbox.bottom
                self.hitbox.y = self.posy
                self.rect.y = self.posy-70
                
        if self.on_ground and self.vely != 0:
            self.on_ground = False

    def attack(self):
        if not self.hit:
            now = pygame.time.get_ticks()
            if now - self.last_attack > self.attack_delay:
                self.last_attack = now
                self.frame = 0
                self.attacking = True
    
    def jump(self):
        self.jumping = True
        self.vely = -9
    
    def iframe(self, parry):
        if not parry:
            self.hit = True
        self.iframes = pygame.time.get_ticks()
        self.invincible = True

    def custom_kill(self):
        for group in self.groups():
            if group != self.game.all_sprites:
                group.remove(self)
    
    def update(self, dt, inputs, tiles):
        if self.hitbox.colliderect(self.game.visible_rect):
            self.inputs = inputs
            self.dx = self.inputs["right"] - self.inputs["left"]
            self.velx = dt * self.dx * 3  
            
            if self.inputs["space"] and self.can_attack:
                self.can_attack = False
                self.attack()
            if not self.inputs["space"]:
                self.can_attack = True
            if self.sword.alive():
                if self.facing_left:
                    self.sword.update(self.posx-8, self.posy+8, self)
                elif self.facing_right:
                    self.sword.update(self.posx+32, self.posy+8, self)
                else:
                    self.sword.update(self.posx+32, self.posy+8, self)
            if self.health <= 0:
                self.health = 0
                if self.velx <= 0:
                    self.anim_list = self.l_kill
                elif self.velx > 0:
                    self.anim_list = self.r_kill
                if self.frame == len(self.anim_list)-1 and (self.anim_list == self.l_kill or self.anim_list == self.r_kill) and self.vely == 0:
                    self.custom_kill()
                    self.end_game = pygame.time.get_ticks()

            self.posx += self.velx
            self.rect.x = self.posx-52
            self.hitbox.x = self.posx
            if self.posx < 0:
                self.posx = 0
                self.hitbox.x = 0
                self.rect.x = -52
            if self.hitbox.right > 3800:
                self.hitbox.right = 3800
                self.posx = self.hitbox.x
                self.rect.x = self.posx-52
            self.horizontal_movement(tiles)

            if self.inputs["up"] and not self.jumping and self.jumps > 0:
                self.jump()
                self.jumps -= 1
            elif not self.inputs["up"] and self.jumping:
                self.vely *= .25
                self.jumping = False

            self.vely += self.acc*.9 * dt
            if self.vely >= 10:
                self.vely = 10
            self.posy += ((self.vely * dt) + ((self.acc/2) * (dt**2)))
            self.rect.y = self.posy-70
            self.hitbox.y = self.posy
            self.vertical_movement(tiles)
            
            if self.velx > 0:
                self.facing_right = True
                self.facing_left = False
            elif self.velx < 0:
                self.facing_left = True
                self.facing_right = False
                
            if self.invincible and pygame.time.get_ticks() - self.iframes > 500:
                self.invincible = False
            self.animate(dt)

class Sword(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, rad, game):
        self.game = game
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        if rad:
            self.radius = rad
            self.image.set_colorkey(BLACK)
            #pygame.draw.circle(self.image, RED, self.rect.center, self.radius, 2)
        self.posx, self.posy = x, y
        self.rect.center = self.posx, self.posy
        self.hitbox.center = self.posx, self.posy
        self.finished = False
        self.spawn = pygame.time.get_ticks()
    
    def update(self, posx, posy, entity): 
        if self.hitbox.colliderect(self.game.visible_rect):
            if pygame.time.get_ticks() - self.spawn >= 200:
                self.finished = True
                self.kill()
            #print(self.finished)
            self.posx = posx
            self.posy = posy
            self.rect.centerx = self.posx
            self.rect.centery = self.posy
            self.hitbox.centerx = self.posx
            self.hitbox.centery = self.posy

class Shuriken(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.load_images()
        #self.image = pygame.image.load(path.join(self.game.game.sprite_dir, "shuriken.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.rect.centerx = x
        self.rect.centery = y
        self.hitbox.center = self.rect.center
        self.posx = x
        self.posy = y
        self.angle = angle
        self.frame = 0
        self.last_frame_update = 0

    def animate(self, dt):
        self.last_frame_update += dt        

        if self.last_frame_update > 60/8:
            self.last_frame_update = 0
            self.frame = (self.frame+1)%len(self.spin)
            self.image = self.spin[self.frame]  

    def load_images(self):
        self.spin = []
        sprite_dir = self.game.game.sprite_dir
        image1 = pygame.image.load(path.join(sprite_dir, "shuriken1.png")).convert_alpha()
        self.spin.append(image1)
        image2 = pygame.image.load(path.join(sprite_dir, "shuriken2.png")).convert_alpha()
        self.spin.append(image2)
        self.image = self.spin[0]
        
    def update(self, dt):
        if self.hitbox.colliderect(self.game.visible_rect):
            self.posx += 9*math.cos(self.angle)*dt
            self.posy += 9*math.sin(self.angle)*dt
            self.rect.centerx, self.rect.centery = self.posx, self.posy
            self.hitbox.center = self.rect.center
            self.animate(dt)
        else:
            self.kill()

class Ninja(pygame.sprite.Sprite):
    def __init__(self, game, pos, points):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.load_images()
        #self.image = pygame.transform.scale2x(self.image)
        #self.image.fill(BLACK)
        self.hitbox = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.hitbox.inflate_ip(-100, -68)
        self.hitbox.move_ip(0, 36)
        #pygame.draw.rect(self.image, GREEN, self.hitbox, 1) #hitbox
        #pygame.draw.rect(self.image, RED, self.rect, 1)
        self.rect.topleft = pos[0], pos[1]
        self.posx, self.posy = self.rect.topleft
        self.hitbox.center = self.rect.centerx, self.rect.centery+30
        self.attacking = False
        self.dx, self.dy = 0, 0
        self.dx_sword = 0
        self.rot = 0
        self.velx = 0
        self.vely = 0
        self.acc = .5
        self.health = 2
        self.invincible = False
        #self.hit = False
        self.been_hit = False
        self.fleeing = False
        self.should_attack = False
        self.points = points
        self.next_point = random.randint(1, 2)
        self.attack_time = pygame.time.get_ticks()
        self.iframes = pygame.time.get_ticks()
        self.last_throw = pygame.time.get_ticks()
        self.throw_interval = 2000
        self.dx_player = 0
        self.dy_player = 0
        self.jumping = False
        self.hit = False
        self.frame, self.last_frame_update = 0, 0
        self.anim_list = self.l_idle
        self.facing_left, self.facing_right = True, False
        self.run_left, self.run_right = True, False

    def animate(self, dt):
        self.last_frame_update += dt
        if (self.anim_list == self.r_hit or self.anim_list == self.l_hit) and self.frame == len(self.anim_list)-1:
            self.hit = False

        if (self.anim_list == self.r_attack or self.anim_list == self.l_attack) and self.frame == len(self.anim_list)-1:
            self.attacking = False
            if self.facing_left:
                shuriken = Shuriken(self.hitbox.x, self.hitbox.y, self.rot, self.game)
            elif self.facing_right:
                shuriken = Shuriken(self.hitbox.x+self.hitbox.width, self.hitbox.y, self.rot, self.game)
            self.game.all_sprites.add(shuriken)
            self.game.mob_attacks.add(shuriken)
            
        if self.hit and self.health > 0:
            if self.facing_left:
                self.anim_list = self.l_hit
            elif self.facing_right:
                self.anim_list = self.r_hit
        
        if self.attacking:
            if self.facing_left:
                self.anim_list = self.l_attack
            elif self.facing_right:
                self.anim_list = self.r_attack
                
        if not self.hit and not self.attacking:
            if self.velx == 0:
                if self.facing_left:
                    self.anim_list = self.l_idle
                elif self.facing_right:
                    self.anim_list = self.r_idle
            else:
                if self.run_left:
                    self.anim_list = self.l_walk
                elif self.run_right:
                    self.anim_list = self.r_walk           

        if self.anim_list == self.r_kill or self.anim_list == self.l_kill:
            if self.frame != len(self.anim_list)-1:
                if self.last_frame_update > 60/8:
                    self.last_frame_update = 0
                    self.frame = (self.frame+1)%len(self.anim_list)
                    self.image = self.anim_list[self.frame]
        else:
            if self.last_frame_update > 60/8:
                self.last_frame_update = 0
                self.frame = (self.frame+1)%len(self.anim_list)
                self.image = self.anim_list[self.frame]

    def custom_kill(self):
        for group in self.groups():
            if group != self.game.all_sprites:
                group.remove(self)

    def load_images(self):
        self.l_walk = self.game.game.ninja_anims["l_walk"]
        self.r_walk = self.game.game.ninja_anims["r_walk"]
        self.l_attack = self.game.game.ninja_anims["l_attack"]
        self.r_attack = self.game.game.ninja_anims["r_attack"]
        self.l_idle = self.game.game.ninja_anims["l_idle"]
        self.r_idle = self.game.game.ninja_anims["r_idle"]
        self.l_hit = self.game.game.ninja_anims["l_hit"]
        self.r_hit = self.game.game.ninja_anims["r_hit"]
        self.l_kill = self.game.game.ninja_anims["l_kill"]
        self.r_kill = self.game.game.ninja_anims["r_kill"]

        self.image = self.l_walk[0]

    def iframe(self):
        self.been_hit = True
        self.iframes = pygame.time.get_ticks()
        self.invincible = True
        self.hit = True

    def throw(self): #type 0
        now = pygame.time.get_ticks()
        if now - self.last_throw > self.throw_interval:
            self.attacking = True
            self.last_throw = now

    def vertical_collisions(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False, self.game.collide_hitbox)
        if hits:
            if self.vely > 0:
                self.posy = hits[0].hitbox.top - self.hitbox.height
                self.vely = 0
                self.hitbox.y = self.posy
                self.rect.y = self.posy - 68
            if self.vely < 0:
                self.vely = 0
                self.posy = hits[0].hitbox.bottom
                self.hitbox.y = self.posy
                self.rect.y = self.posy - 68
    
    def jump(self):
        self.jumping = True
        self.vely -= 10.3

    def update(self, dt, tiles):
        if self.hitbox.colliderect(self.game.visible_rect):
            if self.fleeing:
                if self.points[self.next_point]["cx"] * 8 - self.hitbox.x > 5:
                    self.dx = 1
                elif self.points[self.next_point]["cx"] * 8 - self.hitbox.x < -5:
                    self.dx = -1
                else:
                    self.dx = 0
                    self.fleeing = False
                    self.next_point = random.randint(0, 2)
                if (abs(self.hitbox.x - self.points[self.next_point]["cx"]*8)) <= 170 and self.hitbox.y - self.points[self.next_point]["cy"]*8 > 64 and not self.jumping:
                    self.jump()

            if self.hitbox.x < self.game.player.hitbox.x:
                self.dx_sword = 1
            elif self.hitbox.x > self.game.player.hitbox.x:
                self.dx_sword = -1
                
            if self.game.player.hitbox.centerx - self.hitbox.x < 15 and self.game.player.hitbox.centerx - self.hitbox.x > -15:
                self.fleeing = True

            self.velx = self.dx * 4 * dt

            if self.health <= 0:
                if self.velx <= 0:
                    self.anim_list = self.l_kill
                elif self.velx > 0:
                    self.anim_list = self.r_kill
                if self.frame == len(self.anim_list)-1 and (self.anim_list == self.l_kill or self.anim_list == self.r_kill) and self.vely == 0:
                    self.custom_kill()

            self.vely += self.acc*.9 *dt
            self.posy += ((self.vely * dt) + ((self.acc/2) * (dt**2)))
            self.rect.y = self.posy - 68
            self.hitbox.y = self.posy
            if self.invincible and pygame.time.get_ticks() - self.iframes > 500:
                self.invincible = False
            self.vertical_collisions(tiles)

            self.dx_player = self.game.player.hitbox.centerx-self.hitbox.x
            self.dy_player = self.game.player.hitbox.centery-self.hitbox.y
            if abs(self.dx_player) < 350 and abs(self.dx_player) > 100 and self.health > 0:
                self.rot = math.atan2(self.dy_player, self.dx_player)
                self.throw()

            self.posx += self.velx
            self.rect.x = self.posx-58
            self.hitbox.x = self.posx
            if self.hitbox.centerx < self.game.player.hitbox.centerx:
                self.facing_right = True
                self.facing_left = False
            elif self.hitbox.centerx > self.game.player.hitbox.centerx:
                self.facing_left = True
                self.facing_right = False
            else:
                self.facing_left = True
                self.facing_right = False
            if self.velx < 0:
                self.run_left = True
                self.run_right = False
            elif self.velx > 0:
                self.run_left = False
                self.run_right = True
            else:
                self.run_left = True
                self.run_right = False

            self.animate(dt)

class Samurai(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.load_images()
        #self.image = pygame.image.load(path.join(self.game.game.assets_dir, "samurai.png")).convert_alpha()
        #self.image = pygame.transform.flip(self.image, True, False)
        #self.image = pygame.Surface((32, 64))
        #self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.hitbox.inflate_ip(-96, -64)
        self.hitbox.move_ip(0, 32)
        #pygame.draw.rect(self.image, GREEN, self.hitbox, 1) #hitbox
        #pygame.draw.rect(self.image, RED, self.rect, 1)
        self.rect.topleft = pos[0], pos[1]
        self.posx, self.posy = self.rect.topleft
        self.hitbox.center = self.rect.centerx, self.rect.centery+32
        self.attack_area = pygame.Rect(0, 0, 96, 80)
        self.attack_area.center = self.hitbox.center
        self.bounds = (self.hitbox.centerx - 75, self.hitbox.centerx +75)
        self.vely = 0
        self.velx = 0
        self.acc = .5
        self.health = 3
        self.invincible = False
        self.patrol = True
        self.seeking = False
        self.attack_time = pygame.time.get_ticks()
        self.last_attack = pygame.time.get_ticks()
        self.attack_delay = 2500
        self.attacking = False
        self.facing_left, self.facing_right = False, False
        self.frame, self.last_frame_update = 0, 0
        self.anim_list = self.l_walk
        self.hit = False
        self.been_hit = False
        self.iframes = pygame.time.get_ticks()
        self.invincible = False
        self.dx = random.randint(-1, 1)
        self.sword = pygame.sprite.Sprite()
        while self.dx == 0:
            self.dx = random.randint(-1, 1)
    
    def iframe(self):
        self.iframes = pygame.time.get_ticks()
        self.invincible = True
        self.hit = True

    def custom_kill(self):
        for group in self.groups():
            if group != self.game.all_sprites:
                group.remove(self)

    def load_images(self):
        self.l_walk = self.game.game.samurai_anims["l_walk"]
        self.r_walk = self.game.game.samurai_anims["r_walk"]
        self.l_attack = self.game.game.samurai_anims["l_attack"]
        self.r_attack = self.game.game.samurai_anims["r_attack"]
        self.l_idle = self.game.game.samurai_anims["l_idle"]
        self.r_idle = self.game.game.samurai_anims["r_idle"]
        self.l_hit = self.game.game.samurai_anims["l_hit"]
        self.r_hit = self.game.game.samurai_anims["r_hit"]
        self.l_kill = self.game.game.samurai_anims["l_kill"]
        self.r_kill = self.game.game.samurai_anims["r_kill"]
        self.image = self.l_walk[0]
    
    def animate(self, dt):
        self.last_frame_update += dt
        if self.anim_list == self.r_hit or self.anim_list == self.l_hit:
            if self.frame >= 5:
                self.hit = False

        if (self.anim_list == self.r_attack or self.anim_list == self.l_attack) and self.frame == len(self.anim_list)-3:
            #self.attacking = False
            if not self.sword.alive():
                if self.dx == -1:
                    self.sword = Sword(self.hitbox.x, self.hitbox.y+16, 88, 88, 44, self.game)
                elif self.dx == 1:
                    self.sword = Sword(self.hitbox.x+32, self.hitbox.y+16, 88, 88, 44, self.game)
                else:
                    self.sword = Sword(self.hitbox.x, self.hitbox.y+16, 88, 88, 44, self.game)
                self.game.mob_melee.add(self.sword)
                self.game.all_sprites.add(self.sword)

        if (self.anim_list == self.r_attack or self.anim_list == self.l_attack) and self.frame == len(self.anim_list)-1:
            self.attacking = False
        
        if self.health > 0:
            if self.attacking:
                if self.facing_left:
                    self.anim_list = self.l_attack
                elif self.facing_right:
                    self.anim_list = self.r_attack
            
            if self.hit:
                if self.facing_left:
                    self.anim_list = self.l_hit
                elif self.facing_right:
                    self.anim_list = self.r_hit
                    
            if not self.hit and not self.attacking:
                if self.velx == 0:
                    if self.facing_left:
                        self.anim_list = self.l_idle
                    elif self.facing_right:
                        self.anim_list = self.r_idle
                else:
                    if self.facing_left:
                        self.anim_list = self.l_walk
                    elif self.facing_right:
                        self.anim_list = self.r_walk        

        if self.anim_list == self.r_kill or self.anim_list == self.l_kill:
            if self.frame != len(self.anim_list)-1:
                if self.last_frame_update > 60/8:
                    self.last_frame_update = 0
                    self.frame = (self.frame+1)%len(self.anim_list)
                    self.image = self.anim_list[self.frame]
        else:
            if self.last_frame_update > 60/8:
                self.last_frame_update = 0
                self.frame = (self.frame+1)%len(self.anim_list)
                self.image = self.anim_list[self.frame]              
 
    def attack(self):
        if not self.hit:
            now = pygame.time.get_ticks()
            if now - self.last_attack > self.attack_delay:
                self.last_attack = now
                self.frame = 0
                self.attacking = True
    
    def horizontal_collisions(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False, self.game.collide_hitbox)
        if hits:
            if self.dx > 0:
                self.posx = hits[0].hitbox.left - self.hitbox.width
            if self.dx < 0:
                self.posx = hits[0].hitbox.right
            self.velx = 0
            self.rect.x = self.posx-48
            self.hitbox.x = self.posx

    def vertical_collisions(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False, self.game.collide_hitbox)
        if hits:
            if self.vely > 0:
                self.posy = hits[0].hitbox.top - self.hitbox.height
                self.vely = 0
                self.hitbox.y = self.posy
                self.rect.y = self.posy-64
            if self.vely < 0:
                self.vely = 0
                self.posy = hits[0].hitbox.bottom
                self.rect.y = self.posy-64
                self.hitbox.y = self.posy

    def update(self, dt, tiles):
        if self.hitbox.colliderect(self.game.visible_rect):
            hits = self.attack_area.colliderect(self.game.player.rect)
            if hits and self.health>0:
                self.attack()
            
            self.velx = dt * self.dx * 2

            if self.dx == -1:
                self.sword.update(self.hitbox.x, self.hitbox.y+16, self)
            elif self.dx == 1:
                self.sword.update(self.hitbox.x+32, self.hitbox.y+16, self)
        
            if self.attacking and self.frame == len(self.anim_list)-1:
                if self.facing_left:
                    self.anim_list = self.l_attack
                elif self.facing_right:
                    self.anim_list = self.r_attack

            if self.health <= 0:
                if self.velx <= 0:
                    self.anim_list = self.l_kill
                elif self.velx > 0:
                    self.anim_list = self.r_kill
                if self.frame == len(self.anim_list)-1 and (self.anim_list == self.l_kill or self.anim_list == self.r_kill) and self.vely == 0:
                    self.custom_kill()
            if abs(self.hitbox.centerx - self.game.player.hitbox.centerx) <= 150:
                self.seeking = True
                self.patrol = False
            else:
                if self.seeking:
                    self.patrol = True
                    self.seeking = False
                    self.bounds = (self.hitbox.centerx - 75, self.hitbox.centerx +75)

            if self.patrol:
                if self.hitbox.centerx <= self.bounds[0]:
                    self.dx = 1
                elif self.hitbox.centerx >= self.bounds[1]:
                    self.dx = -1
            elif self.seeking:
                if self.hitbox.centerx - self.game.player.hitbox.centerx < -32:
                    self.dx = 1
                elif self.hitbox.centerx - self.game.player.hitbox.centerx > 32:
                    self.dx = -1
                else:
                    self.dx = 0

            self.posx += self.velx
            self.rect.x = self.posx - 48
            self.hitbox.x = self.posx
            self.horizontal_collisions(tiles)
            self.attack_area.centerx = self.hitbox.centerx

            self.vely += self.acc*.9 *dt
            self.posy += ((self.vely * dt) + ((self.acc/2) * (dt**2)))
            self.rect.y = self.posy-64
            self.hitbox.y = self.posy
            self.vertical_collisions(tiles)
            self.attack_area.centery = self.hitbox.centery
            if self.velx > 0:
                self.facing_right = True
                self.facing_left = False
            elif self.velx < 0:
                self.facing_left = True
                self.facing_right = False

            if self.invincible and pygame.time.get_ticks() - self.iframes > 500:
                self.invincible = False
            self.animate(dt)

class Gate(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.game.assets_dir, "torii.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()