import pygame
import math
from pygame.constants import *
from settings import *
from os import path
import random
import json

class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.game.assets_dir, "player.png")).convert_alpha()
        #self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.hitbox = self.image.get_rect()
        self.hitbox.inflate_ip(-104, -70)
        self.hitbox.move_ip(0, 35)
        pygame.draw.rect(self.image, RED, self.rect, 1)
        pygame.draw.rect(self.image, GREEN, self.hitbox, 1)
        self.rect.topleft = pos[0], pos[1]
        self.posx, self.posy = self.rect.topleft
        self.hitbox.center = self.rect.centerx, self.rect.centery+29
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
            self.rect.x = self.posx-52
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
                self.rect.y = self.posy-70
            if self.vely < 0:
                self.vely = 0
                self.posy = hits[0].hitbox.bottom
                self.hitbox.y = self.posy
                self.rect.y = self.posy-70
                
        if self.on_ground and self.vely != 0:
            self.on_ground = False

    def attack(self):
        if self.inputs["left"]:
            self.attacking = True
            self.sword = Sword(self.posx, self.posy+8, 64, 64, 32, self.game)
        else:
            self.attacking = True
            self.sword = Sword(self.posx+32, self.posy+8, 64, 64, 32, self.game)
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
        print(self.vely)
        if self.hitbox.colliderect(self.game.visible_rect):
            self.inputs = inputs
            self.dx = self.inputs["right"] - self.inputs["left"]
            self.velx = dt * self.dx * 3  
            self.posx += self.velx
            self.rect.x = self.posx-52
            self.hitbox.x = self.posx
            if self.posx < 0:
                self.posx = 0
                self.hitbox.x = 0
                self.rect.x = -52
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
            if self.vely >= 10:
                self.vely = 10
            self.posy += ((self.vely * dt) + ((self.acc/2) * (dt**2)))
            self.rect.y = self.posy-70
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
            pygame.draw.circle(self.image, RED, self.rect.center, self.radius, 2)
        self.posx, self.posy = x, y
        self.rect.center = self.posx, self.posy
        self.hitbox.center = self.posx, self.posy
        self.finished = False
        self.spawn = pygame.time.get_ticks()
    
    def update(self, posx, posy, player): 
        if self.hitbox.colliderect(self.game.visible_rect):
            if pygame.time.get_ticks() - self.spawn >= 250:
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
        self.image = pygame.Surface((5, 5))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.rect.centerx = x
        self.rect.centery = y
        self.hitbox.center = self.rect.center
        self.posx = x
        self.posy = y
        self.angle = angle
    
    def update(self, dt):
        if self.hitbox.colliderect(self.game.visible_rect):
            self.posx += 7*math.cos(self.angle)*dt
            self.posy += 7*math.sin(self.angle)*dt
            self.rect.centerx, self.rect.centery = self.posx, self.posy
            self.hitbox.center = self.rect.center

class Ninja(pygame.sprite.Sprite):
    def __init__(self, game, pos, points):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.game.assets_dir, "ninja.png")).convert_alpha()
        #self.image = pygame.Surface((32, 64))
        self.image = pygame.transform.flip(self.image, True, False)
        self.image.set_colorkey(BLACK)
        #self.image = pygame.transform.scale2x(self.image)
        #self.image.fill(BLACK)
        self.hitbox = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.hitbox.inflate_ip(-100, -68)
        self.hitbox.move_ip(0, 36)
        pygame.draw.rect(self.image, GREEN, self.hitbox, 1) #hitbox
        pygame.draw.rect(self.image, RED, self.rect, 1)
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

    def iframe(self):
        self.been_hit = True
        self.iframes = pygame.time.get_ticks()
        self.invincible = True

    def attack(self):
        now = pygame.time.get_ticks()
        if now - self.attack_time > 300 and not self.attacking:
            self.attacking = True
            if self.dx_sword == 1:
                self.sword = Sword(self.posx+64, self.posy+32, 96, 8, 0, self.game)
            elif self.dx_sword == -1: 
                self.sword = Sword(self.posx-32, self.posy+32, 96, 8, 0, self.game)
            self.game.mob_melee.add(self.sword)
            self.game.all_sprites.add(self.sword)

    def throw(self): #type 0
        now = pygame.time.get_ticks()
        if now - self.last_throw > self.throw_interval:
            self.last_throw = now
            shuriken = Shuriken(self.hitbox.centerx, self.hitbox.centery, self.rot, self.game)
            self.game.all_sprites.add(shuriken)
            self.game.mob_attacks.add(shuriken)

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
                self.kill()
            self.vely += self.acc*.9 *dt
            self.posy += ((self.vely * dt) + ((self.acc/2) * (dt**2)))
            self.rect.y = self.posy - 68
            self.hitbox.y = self.posy
            if self.invincible and pygame.time.get_ticks() - self.iframes > 500:
                self.invincible = False
            self.vertical_collisions(tiles)

            self.dx_player = self.game.player.hitbox.x-self.hitbox.x
            self.dy_player = self.game.player.hitbox.y-self.hitbox.y
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
            self.rect.x = self.posx-58
            self.hitbox.x = self.posx

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
        pygame.draw.rect(self.image, GREEN, self.hitbox, 1) #hitbox
        pygame.draw.rect(self.image, RED, self.rect, 1)
        self.rect.topleft = pos[0], pos[1]
        self.posx, self.posy = self.rect.topleft
        self.hitbox.center = self.rect.centerx, self.rect.centery+32
        self.attack_area = pygame.Rect(0, 0, 96, 80)
        self.attack_area.center = self.hitbox.center
        self.bounds = (self.hitbox.centerx - 75, self.hitbox.centerx +75)
        self.vely = 0
        self.velx = 0
        self.acc = .5
        self.health = 4
        self.invincible = False
        self.patrol = True
        self.seeking = False
        self.attack_time = pygame.time.get_ticks()
        self.attack_delay = pygame.time.get_ticks()
        self.should_attack = False
        self.attacking = False
        self.facing_left, self.facing_right = False, False
        self.frame, self.last_frame_update = 0, 0
        self.anim_list = self.l_walk
        self.attack_done = True
        self.dx = random.randint(-1, 1)
        while self.dx == 0:
            self.dx = random.randint(-1, 1)
    
    def iframe(self):
        pass
    
    def load_images(self):
        sprite_dir = self.game.game.sprite_dir
        self.l_walk, self.r_walk, self.l_attack, self.r_attack, self.l_idle, self.r_idle = [], [], [], [], [], []

        l_walk_image = pygame.image.load(path.join(sprite_dir, "samurai_left_walk.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_left_walk.json")) as l_walk_file:
            l_walk = json.load(l_walk_file)
        frames = l_walk["frames"]
        for i in range(len(frames)):
            filename = 'samurai_walk {}.aseprite'.format(i)
            data = l_walk['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_walk_image, (0, 0), pygame.Rect(x, y, w, h))
            self.l_walk.append(image)
        l_walk_file.close()

        r_walk_image = pygame.image.load(path.join(sprite_dir, "samurai_right_walk.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_right_walk.json")) as r_walk_file:
            r_walk = json.load(r_walk_file)
        frames = r_walk["frames"]
        for i in range(len(frames)):
            filename = 'samurai_walk {}.aseprite'.format(i)
            data = r_walk['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_walk_image, (0, 0), pygame.Rect(x, y, w, h))
            self.r_walk.append(image)
        r_walk_file.close()

        l_attack_image = pygame.image.load(path.join(sprite_dir, "samurai_left_attack.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_left_attack.json")) as l_attack_file:
            l_attack = json.load(l_attack_file)
        frames = l_attack["frames"]
        for i in range(len(frames)):
            filename = 'samurai_attack {}.aseprite'.format(i)
            data = l_attack['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_attack_image, (0, 0), pygame.Rect(x, y, w, h))
            self.l_attack.append(image)
        l_attack_file.close()

        r_attack_image = pygame.image.load(path.join(sprite_dir, "samurai_right_attack.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_right_attack.json")) as r_attack_file:
            r_attack = json.load(r_attack_file)
        frames = r_attack["frames"]
        for i in range(len(frames)):
            filename = 'samurai_attack {}.aseprite'.format(i)
            data = r_attack['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_attack_image, (0, 0), pygame.Rect(x, y, w, h))
            self.r_attack.append(image)
        r_attack_file.close()

        l_idle_image = pygame.image.load(path.join(sprite_dir, "samurai_left_idle.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_left_idle.json")) as l_idle_file:
            l_idle = json.load(l_idle_file)
        frames = l_idle["frames"]
        for i in range(len(frames)):
            filename = 'samurai {}.aseprite'.format(i)
            data = l_idle['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_idle_image, (0, 0), pygame.Rect(x, y, w, h))
            self.l_idle.append(image)
        l_idle_file.close()

        r_idle_image = pygame.image.load(path.join(sprite_dir, "samurai_right_idle.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_right_idle.json")) as r_idle_file:
            r_idle = json.load(r_idle_file)
        frames = r_idle["frames"]
        for i in range(len(frames)):
            filename = 'samurai {}.aseprite'.format(i)
            data = r_idle['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_idle_image, (0, 0), pygame.Rect(x, y, w, h))
            self.r_idle.append(image)
        r_idle_file.close()

        self.image = self.l_walk[0]
    
    def animate(self, dt):
        self.last_frame_update += dt
        if self.attack_done and not self.attacking:
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

        #print(len(self.anim_list))
        #print(self.attack_done)
        if self.last_frame_update > 60/8:
            self.last_frame_update = 0
            self.frame = (self.frame+1)%len(self.anim_list)
            self.image = self.anim_list[self.frame]
 
    def attack(self):
        self.attack_time = pygame.time.get_ticks()
        self.attacking = True
        if self.dx == -1:
            self.sword = Sword(self.hitbox.x, self.hitbox.y+16, 88, 88, 44, self.game)
        elif self.dx == 1:
            self.sword = Sword(self.hitbox.x+32, self.hitbox.y+16, 88, 88, 44, self.game)
        self.game.mob_melee.add(self.sword)
        self.game.all_sprites.add(self.sword)
    
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
            if hits and not self.attacking:
                if not self.should_attack:
                    self.attack_delay = pygame.time.get_ticks()
                self.should_attack = True
            else:
                self.should_attack = False

            if self.attacking:
                self.velx = dt * self.dx * 2.5
                if self.dx == -1:
                    self.sword.update(self.hitbox.x, self.hitbox.y+16, self)
                elif self.dx == 1:
                    self.sword.update(self.hitbox.x+32, self.hitbox.y+16, self)
                if self.sword.finished:
                    self.attack_done = True
                    now = pygame.time.get_ticks()
                    if now - self.attack_time > 1500:
                        self.attacking = False

            if self.should_attack:
                self.velx = dt * self.dx * 1
                if not self.attacking:
                    self.attack_done = False
                    attack_delay = pygame.time.get_ticks()
                    self.frame = 0
                    if self.facing_left:
                        self.anim_list = self.l_attack
                    elif self.facing_right:
                        self.anim_list = self.r_attack  
                    if attack_delay - self.attack_delay > 200:
                        self.attack()
            else:
                self.velx = dt * self.dx * 2.5
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
                if self.hitbox.centerx - self.game.player.hitbox.centerx < -5:
                    self.dx = 1
                elif self.hitbox.centerx - self.game.player.hitbox.centerx > 5:
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
            if self.velx > 0:
                self.facing_right = True
                self.facing_left = False
            elif self.velx < 0:
                self.facing_left = True
                self.facing_right = False
            self.animate(dt)