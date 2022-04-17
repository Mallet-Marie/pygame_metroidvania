import pygame
import json
from os import path
import math
from states.state import State 
from states.pause import PauseMenu
from settings import *
from sprites import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, id, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.posx = pos[0]
        self.posy = pos[1]
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.id = id

    def update(self, shift):
        self.posx += -shift
        self.rect.topleft = (self.posx, self.posy)
        self.hitbox.topleft = (self.posx, self.posy)

class StaticTile(Tile):
    def __init__(self, id, pos, flip, surface):
        Tile.__init__(self, id, pos)
        self.image = surface
        if flip == 1:
            self.image = pygame.transform.flip(self.image, True, False)
        elif flip == 2:
            self.image = pygame.transform.flip(self.image, False, True)
        elif flip == 3:
            self.image = pygame.transform.flip(self.image, True, True)

class CameraGroup(pygame.sprite.Group):
    def __init__(self, game):
        pygame.sprite.Group.__init__(self)
        self.game = game
        self.offsetx, self.offsety = 100, 300
        self.half_w, self.half_h = WIDTH//2, HEIGHT//2
        self.cam_left = 200
        self.cam_right = 200
        self.cam_top = 50
        self.cam_bottom = 75
        self.cam_width = WIDTH - (self.cam_left + self.cam_right)
        self.cam_height = HEIGHT - (self.cam_top + self.cam_bottom)
        self.camera_rect = pygame.Rect(self.cam_left, self.cam_top, self.cam_width, self.cam_height)
        self.visible_rect = pygame.Rect(-50, -50, WIDTH+100, HEIGHT+100)

    def custom_draw(self, display, player):
        self.offsetx, self.offsety = self.camera_rect.left - self.cam_left, self.camera_rect.top - self.cam_top
        #player.rect.centerx - self.half_w, player.rect.centery - self.half_h
        
        if player.hitbox.left < self.camera_rect.left and player.hitbox.left > 200:
            self.camera_rect.left = player.hitbox.left
        if player.hitbox.right > self.camera_rect.right and player.hitbox.right < 3600:
            self.camera_rect.right = player.hitbox.right
        if player.hitbox.top < self.camera_rect.top:
            self.camera_rect.top = player.hitbox.top
        if player.hitbox.bottom > self.camera_rect.bottom and (player.hitbox.bottom < 456 or player.hitbox.bottom > 504):
            self.camera_rect.bottom = player.hitbox.bottom
        self.visible_rect.topleft = self.camera_rect.x-250, self.camera_rect.y-100
        self.game.visible_rect.topleft = self.visible_rect.topleft
        for sprite in self.sprites():
            if self.visible_rect.colliderect(sprite.hitbox):
                offset_x = sprite.rect.x - self.offsetx
                offset_y = sprite.rect.y - self.offsety
                display.blit(sprite.image, (offset_x, offset_y))

class Spark():
    def __init__(self, loc, angle, speed, color, scale=1):
        self.loc = loc
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.color = color
        self.alive = True

    def point_towards(self, angle, rate):
        rotate_direction = ((angle - self.angle + math.pi * 3) % (math.pi * 2)) - math.pi
        try:
            rotate_sign = abs(rotate_direction) / rotate_direction
        except ZeroDivisionError:
            rotate_sing = 1
        if abs(rotate_direction) < rate:
            self.angle = angle
        else:
            self.angle += rate * rotate_sign

    def calculate_movement(self, dt):
        return [math.cos(self.angle) * self.speed * dt, math.sin(self.angle) * self.speed * dt]


    # gravity and friction
    def velocity_adjust(self, friction, force, terminal_velocity, dt):
        movement = self.calculate_movement(dt)
        movement[1] = min(terminal_velocity, movement[1] + force * dt)
        movement[0] *= friction
        self.angle = math.atan2(movement[1], movement[0])
        # if you want to get more realistic, the speed should be adjusted here

    def move(self, dt):
        movement = self.calculate_movement(dt)
        self.loc[0] += movement[0]
        self.loc[1] += movement[1]

        # a bunch of options to mess around with relating to angles...
        self.point_towards(math.pi / 2, 0.02)
        #self.velocity_adjust(0.975, 0.2, 8, dt)
        #self.angle += 0.1

        self.speed -= 0.3

        if self.speed <= 0:
            self.alive = False

    def draw(self, surf, offset=[0, 0]):
        if self.alive:
            points = [
                [self.loc[0] + math.cos(self.angle) * self.speed * self.scale,self.loc[1] + math.sin(self.angle) * self.speed * self.scale],
                [self.loc[0] + math.cos(self.angle + math.pi / 2) * self.speed * self.scale * 0.3,+ self.loc[1] + math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                [self.loc[0] - math.cos(self.angle) * self.speed * self.scale * 3.5,self.loc[1] - math.sin(self.angle) * self.speed * self.scale * 3.5],
                [self.loc[0] + math.cos(self.angle - math.pi / 2) * self.speed * self.scale * 0.3,self.loc[1] - math.sin(self.angle + math.pi / 2) * self.speed * self.scale * 0.3],
                ]
            pygame.draw.polygon(surf, self.color, points)

class World(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.volumes = self.load_volume()
        self.all_sprites = CameraGroup(self)
        self.dependants = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.attacks = pygame.sprite.Group()
        self.mob_attacks = pygame.sprite.Group()
        self.mob_melee = pygame.sprite.Group()
        self.collision_tiles = pygame.sprite.Group()
        self.heart_img = pygame.image.load(path.join(self.game.assets_dir, "heart.png")).convert_alpha()
        self.half_heart_img = pygame.image.load(path.join(self.game.assets_dir, "half_heart.png")).convert_alpha()
        self.empty_heart_img = pygame.image.load(path.join(self.game.assets_dir, "empty_heart.png")).convert_alpha()
        self.create_tile_group()
        self.spawn_sprites()
        self.image = pygame.image.load(path.join(self.game.assets_dir, "forest.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.visible_rect = pygame.Rect(-50, -50, WIDTH+100, HEIGHT+100)
        self.leave_state = False
        self.sparks = []
        self.offset = [0, 0]
        self.game.sword_sounds["sh_parry"].set_volume(self.volumes["sounds"])
        self.game.sword_sounds["sw_parry"].set_volume(self.volumes["sounds"])
        self.game.sword_sounds["s_hit"].set_volume(self.volumes["sounds"])
        self.game.sword_sounds["n_hit"].set_volume(self.volumes["sounds"])
        pygame.mixer.music.load(path.join(self.game.aud_dir, 'Alexander-Ehlers-Twists.wav'))
        pygame.mixer.music.play(loops=-1)
        if round(self.volumes["music"]-.2) == 0:
            self.volumes["music"] = .3
        pygame.mixer.music.set_volume(self.volumes["music"]-.2)
        #print(self.all_sprites.sprites())
    
    def load_volume(self):
        with open(path.join(self.game.assets_dir, "volume.json"), 'r+') as file:
            volumes = json.load(file)
        return volumes

    def collide_hitbox(self, left, right):
        return left.hitbox.colliderect(right.hitbox)

    def collide_circle_hitbox(self, left, right):
        return left.hitbox.collide_circle(right.hitbox)
    
    def collide_rect_circle_hitbox(self, left, right):
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

    def create_tile_group(self):
        image = pygame.image.load(path.join(self.game.assets_dir, "tileset4.png")).convert_alpha()
        with open("map.ldtk", "r") as map_file:
            map_data = json.load(map_file)
        #tile_group = pygame.sprite.Group()
        level_data = map_data["levels"][0]["layerInstances"][1]["gridTiles"]
        for i in range(len(level_data)):
            pos = level_data[i]["px"]
            src = level_data[i]["src"]
            tile_id = level_data[i]["t"]
            flip = level_data[i]["f"]
            new_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), flags = SRCALPHA).convert_alpha()
            new_surf.blit(image, (0, 0), pygame.Rect(src[0], src[1], TILE_SIZE, TILE_SIZE))
            tile = StaticTile(tile_id, pos, flip, new_surf)
            #tile_group.add(tile)
            self.all_sprites.add(tile)
            if tile.id == 0 or tile.id == 6 or tile.id == 9 or tile.id == 4 or tile.id == 5:
                self.collision_tiles.add(tile)
            self.all_sprites.add()
        map_file.close()

    def handle_sparks(self, dt, display):
        for i, spark in sorted(enumerate(self.sparks), reverse=True):
            spark.move(dt)
            spark.draw(display)
            if not spark.alive:
                self.sparks.pop(i)

    def spawn_sprites(self):
        with open("map.ldtk", "r") as map_file:
            map_data = json.load(map_file)
        tile_group = pygame.sprite.Group()
        entity_data = map_data["levels"][0]["layerInstances"][0]["entityInstances"]
        for i in range(len(entity_data)):
            id = entity_data[i]["__identifier"]
            pos = entity_data[i]["px"]
            if id == "Player":
                self.player = Player(self, pos)
                self.dependants.add(self.player)
                self.all_sprites.add(self.player)
            elif id == "Gate":
                self.gate = Gate(self, pos)
                self.all_sprites.add(self.gate)
            else:
                if id == "Ninja":
                    path_points = entity_data[i]["fieldInstances"][0]["__value"]
                    sprite = Ninja(self, pos, path_points)
                elif id == "Samurai":
                    sprite = Samurai(self, pos)
                self.all_sprites.add(sprite)
                self.mobs.add(sprite)
        map_file.close()

    def update(self, dt, inputs):
        self.dt = dt
        if inputs["enter"]:
            new_state = PauseMenu(self.game, self)
            new_state.enter_state()
        self.dependants.update(self.dt, inputs, self.collision_tiles)
        self.mob_attacks.update(self.dt)
        self.mobs.update(self.dt, self.collision_tiles)
        sword_hits = pygame.sprite.groupcollide(self.mobs, self.attacks, False, False, self.collide_rect_circle_hitbox)
        for hit in sword_hits:
            if not hit.invincible:
                if type(hit) == Ninja:
                    self.game.sword_sounds["n_hit"].play()
                elif type(hit) == Samurai:
                    self.game.sword_sounds["s_hit"].play()
                #self.mobs.empty()
                hit.health -= 1
                hit.iframe()
                hit.attack_time = pygame.time.get_ticks()
                hit.should_attack = True
        #player_hits = pygame.sprite.spritecollide(self.player, self.mobs, False)
        mob_hits = pygame.sprite.spritecollide(self.player, self.mob_attacks, True, self.collide_hitbox)
        mob_melee_hits = pygame.sprite.spritecollide(self.player, self.mob_melee, True, self.collide_hitbox)
        if not self.player.invincible:
            for hit in mob_melee_hits:
                self.game.sword_sounds["n_hit"].play()
                self.player.health -= 2
                self.player.iframe(False)
            for hit in mob_hits:
                self.game.sword_sounds["n_hit"].play()
                self.player.health -= 1
                self.player.iframe(False)
        player_leave = self.collide_hitbox(self.player, self.gate)
        if player_leave and len(self.mobs) <= 0:
            if abs(self.player.hitbox.centerx - self.gate.hitbox.centerx) <= 10:
                self.prev_state.volumes = self.prev_state.load_volume()
                self.prev_state.player_win = True
                self.prev_state.player_dead = False
                self.prev_state.playing_song = False
                pygame.mixer.music.stop()
                self.exit_state()
        if len(self.player.groups()) == 1:
            now = pygame.time.get_ticks()
            if now-self.player.end_game>1000:
                self.prev_state.volumes = self.prev_state.load_volume()
                self.prev_state.player_dead = True
                self.prev_state.player_win = False
                self.prev_state.playing_song = False
                pygame.mixer.music.stop()
                self.exit_state()
        elif self.leave_state:
            self.prev_state.volumes = self.prev_state.load_volume()
            self.prev_state.player_dead = False
            self.prev_state.player_win = False
            self.prev_state.playing_song = False
            self.game.playing_music = False
            pygame.mixer.music.stop()
            self.exit_state()
        #print(bool(self.mobs))
        mx, my = pygame.mouse.get_pos()
        parry_hits = pygame.sprite.groupcollide(self.attacks, self.mob_attacks, False, True, pygame.sprite.collide_circle)
        for hit in parry_hits:
            self.game.sword_sounds["sh_parry"].play()
            self.player.iframe(True)
            if self.player.facing_left:
                self.offset[0] = hit.hitbox.x - self.all_sprites.offsetx
                self.offset[1] = 32 + hit.hitbox.y - self.all_sprites.offsety
            elif self.player.facing_right:
                self.offset[0] = 64 + hit.hitbox.x - self.all_sprites.offsetx
                self.offset[1] = 32 + hit.hitbox.y - self.all_sprites.offsety
            for i in range(10):    
                self.sparks.append(Spark([self.offset[0], self.offset[1]], math.radians(random.randint(0, 360)), random.randint(3, 6), (235, 130, 0), 2))
        mob_melee_parry = pygame.sprite.groupcollide(self.attacks, self.mob_melee, True, True, pygame.sprite.collide_circle)
        for hit in mob_melee_parry:
            self.game.sword_sounds["sw_parry"].play()
            self.player.iframe(True)
            if self.player.facing_left:
                self.offset[0] = hit.hitbox.x - self.all_sprites.offsetx
                self.offset[1] = 32 + hit.hitbox.y - self.all_sprites.offsety
            elif self.player.facing_right:
                self.offset[0] = 64 + hit.hitbox.x - self.all_sprites.offsetx
                self.offset[1] = 32 + hit.hitbox.y - self.all_sprites.offsety

            for i in range(20):    
                self.sparks.append(Spark([self.offset[0], self.offset[1]], math.radians(random.randint(0, 360)), random.randint(3, 6), (235, 130, 0), 2))

    def draw_health(self, display, x, y, health):
        
        for i in range(int(20/2)):
            if int(health/2)>i:
                heart_img = self.heart_img
            elif health/2-int(health/2)!=0 and int(health/2)==i:
                heart_img = self.half_heart_img
            elif health<=0:
                heart_img = self.empty_heart_img
            else:
                heart_img = self.empty_heart_img
            heart_rect = heart_img.get_rect()
            heart_rect.centerx = x+20*i
            heart_rect.centery = y
            display.blit(heart_img, heart_rect)

    def draw(self, display):
        display.blit(self.image, self.rect) # Erase screen/draw background
        #display.fill(WHITE)
        # *after* drawing everything, flip the display
        self.all_sprites.custom_draw(display, self.player)
        self.handle_sparks(self.game.dt, self.game.canvas)
        self.draw_health(display, 10, 10, self.player.health)