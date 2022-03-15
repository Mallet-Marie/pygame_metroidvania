import pygame
from pygame.constants import *
from os import path
from states.title import Title
from settings import *

class Game():
    def __init__(self):
        pygame.init()
        self.sizes = pygame.display.get_desktop_sizes()
        self.SCREEN_W, self.SCREEN_H = WIDTH, HEIGHT
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H), pygame.NOFRAME)
        self.running, self.playing = True, True
        self.inputs = {"left": False, "right": False, "up": False, "down": False, "space": False, "enter": False, "back": False}
        self.state_stack = []
        self.load_assets()
        self.load_states()
        self.clock = pygame.time.Clock()

    def game_loop(self):
        while self.playing:
            self.get_dt()
            self.get_events()
            self.update()
            self.draw()

    def get_events(self):
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    self.playing = False
                if event.key == K_d:
                    self.inputs["right"] = True
                if event.key == K_a:
                    self.inputs["left"] = True
                if event.key == K_w:
                    self.inputs["up"] = True
                if event.key == K_s:
                    self.inputs["down"] = True
                if event.key == K_SPACE:
                    self.inputs["space"] = True
                if event.key == K_RETURN:
                    self.inputs["enter"] = True
                if event.key == K_BACKSPACE:
                    self.inputs["back"] = True
            if event.type == pygame.KEYUP:
                if event.key == K_d:
                    self.inputs["right"] = False
                if event.key == K_a:
                    self.inputs["left"] = False
                if event.key == K_w:
                    self.inputs["up"] = False
                if event.key == K_s:
                    self.inputs["down"] = False
                if event.key == K_SPACE:
                    self.inputs["space"] = False
                if event.key == K_RETURN:
                    self.inputs["enter"] = False
                if event.key == K_BACKSPACE:
                    self.inputs["back"] = False
    
    def update(self):
        self.state_stack[-1].update(self.dt, self.inputs)

    def draw(self):
        self.state_stack[-1].draw(self.canvas)
        self.screen.blit(pygame.transform.scale(self.canvas, (self.SCREEN_W, self.SCREEN_H)), (0, 0))
        pygame.display.flip()

    def load_assets(self):
        self.assets_dir = path.join("assets")
        self.font_dir = path.join(self.assets_dir, "font")

    def get_dt(self):
        self.dt = self.clock.tick(FPS) * 0.001 * FPS
    
    def draw_text(self, surface, text, size, colour, x, y):
        self.font = pygame.font.Font(path.join(self.font_dir, "Minecraft.ttf"), size)
        text_surface = self.font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)
    
    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        for input in self.inputs:
            self.inputs[input] = False
        
game = Game()
while game.running:
    game.game_loop()
pygame.quit()