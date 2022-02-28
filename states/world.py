import pygame as pg
from os import path
from states.state import State
from settings import *
from states.pause import PauseMenu
from sprites import *

class World(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.grass_img = pg.image.load(path.join(self.game.assets_dir, "map", "landscape1.png"))
        self.player = Player(self.game)
        self.floor = Floor(self.game)

    def update(self, dt, actions):
        if actions["start"]:
            new_state = PauseMenu(self.game)
            new_state.enter_state()
        self.player.update(dt, actions)
        floor_hit = pg.sprite.collide_rect(self.player, self.floor)
        if floor_hit:
            self.player.dy = 0
            self.player.falling = False
        else:
            self.player.falling = True

    def render(self, display):
        display.blit(self.grass_img, (0, 0))
        self.player.render(display)
        self.floor.render(display)