from states.menu import MainMenu
from states.state import State
from states.world import World
import pygame
from os import path
from settings import *

class Title(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.image = pygame.image.load(path.join(self.game.assets_dir, "Retribution_Title.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.show_text = True

    def update(self, dt, inputs):
        if inputs["enter"]:
            #new_state = World(self.game)
            self.show_text = False
            new_state = MainMenu(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def draw(self, display):
        display.blit(self.image, self.rect) # Erase screen/draw background
        if self.show_text:
            self.game.draw_text(display, "Press Enter to Continue", 24, WHITE, WIDTH/2, HEIGHT-128)