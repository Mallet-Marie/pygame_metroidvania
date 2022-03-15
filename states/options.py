import pygame 
from states.state import State
from settings import *

class Options(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
    
    def update(self, dt, inputs):
        if inputs["back"]:
            self.exit_state()
        self.game.reset_keys()
    
    def draw(self, display):
        display.fill(BLACK)
        self.game.draw_text(display, "Options", 40, WHITE, WIDTH/2, HEIGHT/2)