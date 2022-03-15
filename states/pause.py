import pygame
from os import path
from states.state import State
from states.options import Options
from settings import *

class PauseMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.index = 0
        self.buttons = pygame.sprite.Group()
        self.start_button = Button(self.game, WIDTH/4, 80, "continue.png","continue")
        self.options_button = Button(self.game, WIDTH/4, 180, "options.png", "options")
        self.quit_button = Button(self.game, WIDTH/4, 280, "quit.png", "quit")
        self.buttons.add(self.start_button)
        self.buttons.add(self.options_button)
        self.buttons.add(self.quit_button)
        self.mouse = Mouse(game)
        self.hovered = None
    
    def update(self, dt, inputs):
        self.mouse.update()
        hovers = pygame.sprite.spritecollide(self.mouse, self.buttons, False)
        self.hovered = None
        for hover in hovers:
            self.hovered = hover
            pressed = pygame.mouse.get_pressed()
            if pressed[0]:
                if hover.key == "continue":
                    self.exit_state()
                elif hover.key == "options":
                    new_state = Options(self.game)
                    new_state.enter_state()
                elif hover.key == "quit":
                    self.game.running = False
                    self.game.playing = False
        self.game.reset_keys()


    def draw(self, display):
        self.prev_state.draw(display)
        self.buttons.draw(display)
        if self.hovered:
            display.blit(self.hovered.fade, self.hovered.rect)
        display.blit(self.mouse.image, self.mouse.rect)
    
class Button(pygame.sprite.Sprite):
    def __init__(self, game, x, y, img, key):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.key = key
        self.image = pygame.image.load(path.join(self.game.assets_dir, img)).convert()
        self.fade = pygame.Surface((120, 60))
        self.fade.set_alpha(100)
        self.fade.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Mouse(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        pygame.mouse.set_visible(False)
        self.image = pygame.image.load(path.join(self.game.assets_dir, "kunai.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        pygame.mouse.set_pos(WIDTH/2, HEIGHT/2)
        self.rect.center = (WIDTH/2, HEIGHT/2)
    
    def update(self):
        self.rect.center = pygame.mouse.get_pos()