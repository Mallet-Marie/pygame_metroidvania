import pygame as pg
from os import path
from states.state import State
from states.party import PartyMenu

class PauseMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.menu_img = pg.image.load(path.join(self.game.assets_dir, "map", "menu.png"))
        self.menu_rect = self.menu_img.get_rect()
        self.menu_rect.center = (self.game.GAME_W*.85, self.game.GAME_H*.4)
        self.menu_options = {0: "Party", 1: "Items", 2: "Magic", 3: "Exit"}
        self.index = 0
        
        self.cursor_img = pg.image.load(path.join(self.game.assets_dir, "map", "cursor.png"))
        self.cursor_rect = self.cursor_img.get_rect()
        self.cursor_posy = self.menu_rect.y + 38
        self.cursor_rect.x, self.cursor_rect.y = self.menu_rect.x + 10, self.cursor_posy

    def update(self, dt, actions):
        self.update_cursor(actions)
        if actions["action1"]:
            self.transition_state()
        if actions["action2"]:
            self.exit_state()
        self.game.reset_keys()

    def render(self, display):
        self.prev_state.render(display)
        display.blit(self.menu_img, self.menu_rect)
        display.blit(self.cursor_img, self.cursor_rect) 

    def update_cursor(self, actions):
        if actions["down"]:
            self.index = (self.index+1) % len(self.menu_options)
        elif actions["up"]:
            self.index = (self.index-1) % len(self.menu_options)
        self.cursor_rect.y = self.cursor_posy + (self.index*32)

    def transition_state(self):
        if self.menu_options[self.index] == "Party":
            new_state = PartyMenu(self.game)
            new_state.enter_state()
        elif self.menu_options[self.index] == "Items":
            pass
        elif self.menu_options[self.index] == "Magic":
            pass
        elif self.menu_options[self.index] == "Exit":
            while len(self.game.state_stack) > 1:
                self.game.state_stack.pop()