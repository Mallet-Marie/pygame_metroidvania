import time
import pygame as pg
from pygame.constants import *
from os import path
from states.title import Title
from settings import *

class Game():
    def __init__(self):
        pg.init()
        self.GAME_W, self.GAME_H = WIDTH, HEIGHT
        self.sizes = pg.display.get_desktop_sizes()
        self.SCREEN_W, self.SCREEN_H = self.sizes[0]
        self.game_canvas = pg.Surface((self.GAME_W, self.GAME_H))
        self.screen = pg.display.set_mode((self.SCREEN_W, self.SCREEN_H), pg.NOFRAME)
        #add noframe and change to fullscreen self.sizes[0]
        self.running, self.playing = True, True
        self.actions = {"left": False, "right": False, "up" : False, "down" : False, "action1" : False, "action2" : False, "start" : False}
        self.dt, self.prev_time = 0, 0
        self.state_stack = []
        self.load_assets()
        self.load_states()
        self.clock = pg.time.Clock()

    def game_loop(self):
        while self.playing:
            self.clock.tick(FPS)
            self.get_dt()
            self.get_events()
            self.update()
            self.render()

    def get_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing, self.running = False, False
            if event.type == pg.KEYDOWN:
                if event.key == K_ESCAPE:
                    self.playing, self.running = False, False
                if event.key == K_a:
                    self.actions['left'] = True
                if event.key == K_d:
                    self.actions['right'] = True
                if event.key == K_w:
                    self.actions['up'] = True
                if event.key == K_s:
                    self.actions['down'] = True
                if event.key == K_p:
                    self.actions['action1'] = True
                if event.key == K_o:
                    self.actions['action2'] = True
                if event.key == K_RETURN:
                    self.actions['start'] = True
            if event.type == pg.KEYUP:
                if event.key == K_a:
                    self.actions['left'] = False
                if event.key == K_d:
                    self.actions['right'] = False
                if event.key == K_w:
                    self.actions['up'] = False
                if event.key == K_s:
                    self.actions['down'] = False
                if event.key == K_p:
                    self.actions['action1'] = False
                if event.key == K_o:
                    self.actions['action2'] = False
                if event.key == K_RETURN:
                    self.actions['start'] = False
    
    def update(self):
        self.state_stack[-1].update(self.dt, self.actions)

    def render(self):
        self.state_stack[-1].render(self.game_canvas)
        self.screen.blit(pg.transform.scale(self.game_canvas, (self.SCREEN_W, self.SCREEN_H)), (0, 0))
        pg.display.flip()

    def get_dt(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now
    
    def draw_text(self, surface, text, size, colour, x, y):
        self.font = pg.font.Font(path.join(self.font_dir, "Minecraft.ttf"), size)
        text_surface = self.font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)
    
    def load_assets(self):
        self.assets_dir = path.join("assets")
        self.sprite_dir = path.join(self.assets_dir, "sprites")
        self.font_dir = path.join(self.assets_dir, "font")
    
    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        for action in self.actions:
            self.actions[action] = False
        
game = Game()
while game.running:
    game.game_loop()
pg.quit()