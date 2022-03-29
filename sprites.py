import pygame
import math
from settings import *
from os import path
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.game.assets_dir, "player.png"))
        self.image = pygame.Surface((32, 64))
        #self.image = pygame.transform.scale2x(self.image)
        #self.image.set_alpha(64) make transparent
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, RED, self.rect, 1)
        self.rect.topleft = pos[0], pos[1]
        self.posx, self.posy = self.rect.topleft
        self.health = 5
        self.velx = 0
        self.vely = 0
        self.acc = .5
        self.dx = 0
        self.jumps = 2
        self.jumping = True
        self.on_ground = False
        self.attacking = False
        self.invincible = False
        #self.hit = False
        self.been_hit = False
        self.hitbox = self.rect.copy()
        pygame.draw.rect(self.image, GREEN, self.hitbox, 1) #hitbox
        self.iframes = pygame.time.get_ticks()

    def horizontal_movement(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False, self.game.collide_hitbox)
        if hits:
            if self.dx > 0:
                self.posx = hits[0].hitbox.left - self.hitbox.width
            if self.dx < 0:
                self.posx = hits[0].hitbox.right
            self.velx = 0
            self.rect.x = self.posx
            self.hitbox.x = self.posx

    def vertical_movement(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False, self.game.collide_hitbox)
        if hits:
            #print("tile" + str(hits[0].rect.top))
            #print("player" + str(self.rect.bottom))
            
            if self.vely > 0:
                self.posy = hits[0].hitbox.top - self.hitbox.height
                self.on_ground = True
                self.vely = 0
                self.jumps = 2
                self.hitbox.y = self.posy
                self.rect.y = self.posy
            if self.vely < 0:
                self.vely = 0
                self.posy = hits[0].rect.bottom
                self.hitbox.y = self.posy
                self.rect.y = self.posy
                
        if self.on_ground and self.vely != 0:
            self.on_ground = False

    def attack(self):
        if self.inputs["left"]:
            self.attacking = True
            self.sword = Sword(self.posx, self.posy+8, 64, 64, 32)
        else:
            self.attacking = True
            self.sword = Sword(self.posx+32, self.posy+8, 64, 64, 32)
        self.game.attacks.add(self.sword)
        self.game.all_sprites.add(self.sword)
    
    def jump(self):
        self.jumping = True
        self.vely = -9
    
    def iframe(self):
        self.been_hit = True
        self.iframes = pygame.time.get_ticks()
        self.invincible = True
    
    def update(self, dt, inputs, tiles):
        self.inputs = inputs
        self.dx = self.inputs["right"] - self.inputs["left"]
        self.velx = dt * self.dx * 3  
        self.posx += self.velx
        self.rect.x = self.posx
        self.hitbox.x = self.posx
        self.horizontal_movement(tiles)
       # if self.jumping:
          #  print(self.rect.x)
        if self.inputs["up"] and not self.jumping and self.jumps > 0:
            self.jump()
            self.jumps -= 1
        elif not self.inputs["up"] and self.jumping:
            self.vely *= .25
            self.jumping = False
        self.vely += self.acc*.9 * dt
        self.posy += ((self.vely * dt) + ((self.acc/2) * (dt**2)))
        self.rect.y = self.posy
        self.hitbox.y = self.posy

        self.vertical_movement(tiles)
        if self.invincible and pygame.time.get_ticks() - self.iframes > 500:
            self.invincible = False
        
        if self.inputs["space"] and not self.attacking:
            self.attack()
        if not self.inputs["space"] and self.attacking:
            if self.sword.finished == True:
                self.attacking = False
        if self.attacking:
            if self.inputs["left"]:
                self.sword.update(self.posx, self.posy+8, self)
            else:
                self.sword.update(self.posx+32, self.posy+8, self)

class Sword(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, rad):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        if rad:
            self.radius = rad
            self.image.set_colorkey(BLACK)
            pygame.draw.circle(self.image, RED, self.rect.center, self.radius, 2)
        self.posx, self.posy = x, y
        self.rect.center = self.posx, self.posy
        self.hitbox.center = self.posx, self.posy
        self.finished = False
        self.spawn = pygame.time.get_ticks()
    
    def update(self, posx, posy, player): 
        if pygame.time.get_ticks() - self.spawn >= 250:
            self.finished = True
            self.kill()
        self.posx = posx
        self.posy = posy
        self.rect.centerx = self.posx
        self.rect.centery = self.posy
        self.hitbox.centerx = self.posx
        self.hitbox.centery = self.posy

class Shuriken(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5, 5))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.rect.centerx = x
        self.rect.centery = y
        self.posx = x
        self.posy = y
        self.angle = angle
    
    def update(self, dt):
        self.posx += 7*math.cos(self.angle)*dt
        self.posy += 7*math.sin(self.angle)*dt
        self.rect.centerx, self.rect.centery = self.posx, self.posy
        self.hitbox.center = self.rect.center

class Ninja(pygame.sprite.Sprite):
    def __init__(self, game, pos, points):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.game.assets_dir, "ninja.png")).convert_alpha()
        self.image = pygame.Surface((32, 64))
        #self.image = pygame.transform.flip(self.image, True, False)
        #self.image.set_colorkey(BLACK)
        #self.image = pygame.transform.scale2x(self.image)
        self.image.fill(RED)
        self.hitbox = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.hitbox = self.hitbox.inflate(-35, -5)
        self.hitbox = self.hitbox.move(0, 3)
        pygame.draw.rect(self.image, GREEN, self.hitbox, 1) #hitbox
        pygame.draw.rect(self.image, RED, self.rect, 1)
        self.rect.topleft = pos[0], pos[1]
        self.posx, self.posy = self.rect.center
        self.hitbox.center = self.posx - 1, self.posy + 3
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

    def iframe(self):
        self.been_hit = True
        self.iframes = pygame.time.get_ticks()
        self.invincible = True

    def attack(self):
        now = pygame.time.get_ticks()
        if now - self.attack_time > 300 and not self.attacking:
            self.attacking = True
            if self.dx_sword == 1:
                self.sword = Sword(self.posx+64, self.posy+32, 96, 8, 0)
            elif self.dx_sword == -1: 
                self.sword = Sword(self.posx-32, self.posy+32, 96, 8, 0)
            self.game.mob_melee.add(self.sword)
            self.game.all_sprites.add(self.sword)

    def throw(self): #type 0
        now = pygame.time.get_ticks()
        if now - self.last_throw > self.throw_interval:
            self.last_throw = now
            shuriken = Shuriken(self.rect.centerx, self.rect.centery, self.rot)
            self.game.all_sprites.add(shuriken)
            self.game.mob_attacks.add(shuriken)

    def vertical_collisions(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False)
        if hits:
            if self.vely > 0:
                self.posy = hits[0].rect.top - self.rect.height
                self.vely = 0
                self.rect.y = self.posy
            if self.vely < 0:
                self.vely = 0
                self.posy = hits[0].rect.bottom
                self.rect.y = self.posy
    
    def jump(self):
        self.jumping = True
        self.vely -= 10.3

    def update(self, dt, tiles):
        if self.fleeing:
            if self.points[self.next_point]["cx"] * 8 < self.rect.x:
                self.dx = -1
            elif self.points[self.next_point]["cx"] * 8 > self.rect.x:
                self.dx = 1
            else:
                self.dx = 0
            if (abs(self.rect.x - self.points[self.next_point]["cx"]*8)) <= 170 and self.rect.y - self.points[self.next_point]["cy"]*8 > 64 and not self.jumping:
                self.jump()

        if self.rect.x < self.game.player.rect.x:
            self.dx_sword = 1
        elif self.rect.x > self.game.player.rect.x:
            self.dx_sword = -1
                
        self.velx = self.dx * 4 * dt
        if self.health <= 0:
            self.kill()
        self.vely += self.acc*.9 *dt
        self.posy += ((self.vely * dt) + ((self.acc/2) * (dt**2)))
        self.rect.y = self.posy
        self.hitbox.y = self.posy
        if self.invincible and pygame.time.get_ticks() - self.iframes > 500:
            self.invincible = False
        self.vertical_collisions(tiles)

        self.dx_player = self.game.player.rect.x-self.rect.x
        self.dy_player = self.game.player.rect.y-self.rect.y
        if abs(self.dx_player) < 350 and abs(self.dx_player) > 100 and not self.attacking :
            self.rot = math.atan2(self.dy_player, self.dx_player)
            self.throw()
        if self.should_attack:
            self.attack()
        if self.attacking:
            if self.dx_sword == 1:
                self.sword.update(self.posx+64, self.posy+32, self)
            elif self.dx_sword == -1:
                self.sword.update(self.posx-32, self.posy+32, self)
            if self.sword.finished:
                self.should_attack = False
                self.attacking = False
                self.fleeing = True

        self.posx += self.velx
        self.rect.x = self.posx
        self.hitbox.x = self.rect.x

class Samurai(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.game.assets_dir, "samurai.png")).convert_alpha()
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.hitbox = self.hitbox.inflate(-35, -5)
        self.hitbox = self.hitbox.move(-6, 3)
        pygame.draw.rect(self.image, GREEN, self.hitbox, 1) #hitbox
        pygame.draw.rect(self.image, RED, self.rect, 1)
        self.rect.topleft = pos[0], pos[1]
        self.posx, self.posy = self.rect.center
        self.hitbox.center = (self.posx, self.posy)
        self.bounds = (self.posx - 75, self.posx +75)
        self.vely = 0
        self.velx = 0
        self.acc = .5
        self.health = 4
        self.dx = random.randint(-1, 1)
        while self.dx == 0:
            self.dx = random.randint(-1, 1)
    
    def vertical_collisions(self, tiles):
        hits = pygame.sprite.spritecollide(self, tiles, False)
        if hits:
            if self.vely > 0:
                self.posy = hits[0].rect.top - self.rect.height
                self.vely = 0
                self.rect.y = self.posy
            if self.vely < 0:
                self.vely = 0
                self.posy = hits[0].rect.bottom
                self.rect.y = self.posy

    def update(self, dt, tiles):
        self.velx = dt * self.dx * 3.5
        self.posx += self.velx
        self.rect.centerx = self.posx
        self.hitbox.centerx = self.posx
        if self.rect.centerx <= self.bounds[0]:
            self.dx = 1
        elif self.rect.centerx >= self.bounds[1]:
            self.dx = -1

        self.vely += self.acc*.9 *dt
        self.posy += ((self.vely * dt) + ((self.acc/2) * (dt**2)))
        self.rect.y = self.posy
        self.hitbox.y = self.posy
        self.vertical_collisions(tiles)