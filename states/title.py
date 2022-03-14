from states.menu import MainMenu
from states.state import State
from states.world import World
from settings import *

class Title(State):
    def __init__(self, game):
        State.__init__(self, game)

    def update(self, dt, inputs):
        if inputs["enter"]:
            #new_state = World(self.game)
            new_state = MainMenu(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def draw(self, display):
        display.fill(WHITE)
        self.game.draw_text(display, "Placeholder", 40, BLACK, WIDTH/2, HEIGHT/2)