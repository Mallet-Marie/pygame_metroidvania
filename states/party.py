import pygame as pg
from os import path
from states.state import State
from settings import *

class PartyMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game

    def update(self, dt, actions):
        if actions["action2"]:
            self.exit_state()
        self.game.reset_keys()

    def render(self, surface):
        surface.fill(WHITE)
        self.game.draw_text(surface, "PARTY MENU", 40, BLACK, self.game.GAME_W/2, self.game.GAME_H/2)