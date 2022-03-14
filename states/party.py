from settings import *
from states.state import State

class PartyMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game

    def update(self, dt, inputs):
        if inputs["back"]:
            self.exit_state()
        self.game.reset_keys()

    def draw(self, surface):
        surface.fill(WHITE)
        self.game.draw_text(surface, "PARTY MENU", 40, BLACK, WIDTH/2, HEIGHT/2)