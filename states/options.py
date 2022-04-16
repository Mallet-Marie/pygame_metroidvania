import pygame 
from states.state import State
from settings import *
from os import path
import json

class Options(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.volumes = None
        self.load()
        self.image = pygame.image.load(path.join(self.game.assets_dir, "Retribution_Title.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.fade = pygame.Surface((self.rect.width, self.rect.height))
        self.fade.set_alpha(200)
        self.fade.fill(BLACK)
        self.mouse = Mouse(game)
        self.master = Volume(WIDTH/5, 128, "Master:", self.game, self.volumes["master"])
        self.music = Volume(WIDTH/5, 192, "Music:", self.game, self.volumes["music"])
        self.sounds = Volume(WIDTH/5, 256, "Sounds:", self.game, self.volumes["sounds"])
        self.buttons = [self.master, self.music, self.sounds]
    
    def load_existing(self):
        with open(path.join(self.game.assets_dir, "volume.json"), 'r+') as file:
            volumes = json.load(file)
        return volumes

    def create_file(self):
        save = {
            "master": .5,
            "music": .5,
            "sounds": .5
        }
        file = open(path.join(self.game.assets_dir, "volume.json"), "w")
        json.dump(save, file)
        return save
    
    def write_file(self):
        save = self.volumes
        file = open(path.join(self.game.assets_dir, "volume.json"), "w")
        json.dump(save, file)
    
    def load(self):
        try:
            save = self.load_existing()
        except:
            save = self.create_file()
        self.volumes = save

    def update(self, dt, inputs):
        for button in self.buttons:
            hover = pygame.sprite.collide_rect(self.mouse, button.plus)
            if hover:
                if inputs["l_click"]:
                    if round(button.volume, 1) < 1:
                        button.volume += .1
        for button in self.buttons:
            hover = pygame.sprite.collide_rect(self.mouse, button.minus)
            if hover:
                if inputs["l_click"]:
                    if round(button.volume, 1) > 0:
                        button.volume -= .1

        self.volumes["master"] = round(self.master.volume, 1)
        self.volumes["music"] = round(self.music.volume, 1)
        self.volumes["sounds"] = round(self.sounds.volume, 1)
        self.mouse.update()
        if inputs["back"]:
            if self.volumes["master"] < self.volumes["music"] or self.volumes["master"] < self.volumes["sounds"]:
                self.volumes["music"] = self.volumes["master"]
                self.volumes["sounds"] = self.volumes["master"]
            self.write_file()
            self.prev_state.volumes = self.prev_state.load_volume()
            self.exit_state()
        self.game.reset_keys()
    
    def draw(self, display):
        display.blit(self.image, self.rect)
        display.blit(self.fade, self.rect)
        self.game.draw_text(display, "Audio", 40, WHITE, WIDTH/2, 64)
        self.master.draw(display, self.volumes["master"])
        self.music.draw(display, self.volumes["music"])
        self.sounds.draw(display, self.volumes["sounds"])
        display.blit(self.mouse.image, self.mouse.rect)

class Volume():
    def __init__(self, x, y, text, game, volume):
        self.game = game
        self.plus = Plus(self.game, x+384, y)
        self.minus = Minus(self.game, x+128, y)
        self.volume = volume
        self.text = text
        self.x = x
        self.y = y
    
    def draw_bar(self, display, x, y, pct):
        if pct < 0:
            pct = 0
        fill = (pct/10) * 192
        fill_rect = pygame.Rect(x, y, fill, 8)
        pygame.draw.rect(display, WHITE, fill_rect)
    
    def draw(self, display, volume):
        self.draw_bar(display, self.x+160, self.y-4, int(volume*10))
        display.blit(self.plus.image, self.plus.rect)
        display.blit(self.minus.image, self.minus.rect)
        self.game.draw_text(display, self.text, 24, WHITE, self.x, self.y)
        self.game.draw_text(display, str(int(volume*10)), 24, WHITE, self.x+64, self.y)
    
class Plus(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.assets_dir, "plus.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
class Minus(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.assets_dir, "minus.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Mouse(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        pygame.mouse.set_visible(False)
        self.image = pygame.image.load(path.join(self.game.assets_dir, "kunai1.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        pygame.mouse.set_pos(WIDTH/2, HEIGHT/2)
        self.rect.center = (WIDTH/2, HEIGHT/2)
    
    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        if self.rect.centerx >= WIDTH:
            self.rect.centerx = WIDTH
        elif self.rect.centerx <= 0:
            self.rect.centerx = 0
        if self.rect.centery >= HEIGHT:
            self.rect.centery = HEIGHT
        elif self.rect.centery <= 0:
            self.rect.centery = 0