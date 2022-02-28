from states.state import State
from states.world import World
from settings import *

class Title(State):
    def __init__(self, game):
        State.__init__(self, game)

    def update(self, dt, actions):
        if actions["start"]:
            new_state = World(self.game)
            new_state.enter_state()
        self.game.reset_keys()

    def render(self, display):
        display.fill(WHITE)
        self.game.draw_text(display, "Game States Demo", 40, BLACK, self.game.GAME_W/2, self.game.GAME_H/2)