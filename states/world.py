import pygame
import json
from os import path
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
    def __init__(self, id, pos, surface):
        Tile.__init__(self, id, pos)
        #self.image = surface

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.offsetx, self.offsety = 100, 300
        self.half_w, self.half_h = WIDTH//2, HEIGHT//2
        self.cam_left = 200
        self.cam_top = 300
        self.cam_width = WIDTH - 400
        self.cam_height = HEIGHT - 300
        self.camera_rect = pygame.Rect(self.cam_left, self.cam_top, self.cam_width, self.cam_height)

    def custom_draw(self, display, player):
        self.offsetx, self.offsety = self.camera_rect.left - 200, self.camera_rect.top - 300
        #player.rect.centerx - self.half_w, player.rect.centery - self.half_h
        
        if player.rect.left < self.camera_rect.left:
            self.camera_rect.left = player.rect.left
        if player.rect.right > self.camera_rect.right:
            self.camera_rect.right = player.rect.right
        
        for sprite in self.sprites():
            offset_x = sprite.rect.x - self.offsetx
            offset_y = sprite.rect.y - self.offsety
            display.blit(sprite.image, (offset_x, offset_y))

class World(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.all_sprites = CameraGroup()
        self.dependants = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.attacks = pygame.sprite.Group()
        self.mob_attacks = pygame.sprite.Group()
        self.mob_melee = pygame.sprite.Group()
        self.collision_tiles = pygame.sprite.Group()
        self.create_tile_group()
        self.spawn_sprites()
        self.image = pygame.image.load(path.join(self.game.assets_dir, "fores.png")).convert_alpha()
        self.rect = self.image.get_rect()
        #print(self.all_sprites.sprites())

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

    def create_tile_group(self):
        image = pygame.image.load(path.join(self.game.assets_dir, "tileset3.png")).convert_alpha()
        with open("map4.ldtk", "r") as map_file:
            map_data = json.load(map_file)
        #tile_group = pygame.sprite.Group()
        level_data = map_data["levels"][0]["layerInstances"][1]["gridTiles"]
        for i in range(len(level_data)):
            pos = level_data[i]["px"]
            src = level_data[i]["src"]
            tile_id = level_data[i]["t"]
            new_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            new_surf.blit(image, (0, 0), pygame.Rect(src[0], src[1], TILE_SIZE, TILE_SIZE))
            tile = StaticTile(tile_id, pos, new_surf)
            #tile_group.add(tile)
            self.all_sprites.add(tile)
            if tile.id == 4 or tile.id == 0 or tile.id == 7:
                self.collision_tiles.add(tile)
            self.all_sprites.add()

    def spawn_sprites(self):
        with open("map4.ldtk", "r") as map_file:
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
            else:
                if id == "Ninja":
                    path_points = entity_data[i]["fieldInstances"][0]["__value"]
                    sprite = Ninja(self, 0, pos, path_points)
                elif id == "Samurai":
                    sprite = Samurai(self, pos)
                self.all_sprites.add(sprite)
                self.mobs.add(sprite)

    def update(self, dt, inputs):
        self.dt = dt
        if inputs["enter"]:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        self.dependants.update(self.dt, inputs, self.collision_tiles)
        self.mob_attacks.update(self.dt)
        self.mobs.update(self.dt, self.collision_tiles)
        #self.tile_sprites.update(self.dt)
        sword_hits = pygame.sprite.groupcollide(self.mobs, self.attacks, False, False)
        for hit in sword_hits:
            if not hit.invincible:
                hit.fleeing = True
                hit.health -= 1
                hit.iframe()
        player_hits = pygame.sprite.spritecollide(self.player, self.mobs, False)
        mob_hits = pygame.sprite.spritecollide(self.player, self.mob_attacks, True)
        mob_melee_hits = pygame.sprite.spritecollide(self.player, self.mob_melee, True)
        if not self.player.invincible:
            for hit in mob_melee_hits:
                self.player.health -= 1
                self.player.iframe()
            for hit in mob_hits:
                self.player.health -= 1
                self.player.iframe()
            if player_hits:
                self.player.health -= 1
                self.player.iframe()

            if self.player.health <= 0 or self.player.rect.bottom >= HEIGHT:
                self.exit_state()
                #self.player.kill()
                #self.game.playing = False
                #self.game.running = False

        parry_hits = pygame.sprite.groupcollide(self.attacks, self.mob_attacks, False, True, pygame.sprite.collide_circle)
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
        #display.blit(self.image, self.rect) # Erase screen/draw background
        display.fill(WHITE)
        # *after* drawing everything, flip the display
        self.draw_health(display, 10, 10, self.player.health)
        #self.tile_sprites.draw(display)
        self.all_sprites.custom_draw(display, self.player)