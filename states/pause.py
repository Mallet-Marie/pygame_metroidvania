import pygame
from os import path
from states.state import State
from states.options import Options
from settings import *

class PauseMenu(State):
    def __init__(self, game, world):
        State.__init__(self, game)
        self.game = game
        self.world = world
        self.index = 0
        self.buttons = pygame.sprite.Group()
        self.start_button = Button(self.game, WIDTH/5, 280, "continue.png","continue")
        #self.options_button = Button(self.game, WIDTH/2, 280, "options.png", "options")
        self.quit_button = Button(self.game, WIDTH/2, 280, "quit.png", "quit")
        self.buttons.add(self.start_button)
        #self.buttons.add(self.options_button)
        self.buttons.add(self.quit_button)
        self.mouse = Mouse(game)
        self.cursor_image = pygame.image.load(path.join(self.game.assets_dir, "cursor.png")).convert_alpha()
        self.cursor_rect = self.cursor_image.get_rect()
        self.cursor_rect.center = WIDTH/5, 230
        self.menu_options = ["option1", "option2"]
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.fade = pygame.Surface((self.rect.width, self.rect.height))
        self.fade.set_alpha(150)
        self.fade.fill(BLACK)
        self.hovered = None
    
    def move_cursor(self, inputs):
        if inputs["right"]:
            self.index = (self.index+1) % len(self.menu_options)
        elif inputs["left"]:
            self.index = (self.index-1) % len(self.menu_options)

        if not self.player_dead and not self.player_win:
            self.cursor_rect.centery = 230
        else:
            self.cursor_rect.centery = 280

        if self.index == 0:
            self.cursor_rect.centerx = WIDTH/5
        elif self.index == 1:
            self.cursor_rect.centerx = WIDTH/2
        """elif self.index == 2:
            self.cursor_rect.centerx = WIDTH-WIDTH/5"""
    
    def update(self, dt, inputs):
        self.mouse.update()
        self.move_cursor(inputs)
        if inputs["enter"]:
            if self.index == 0:
                self.exit_state()
            elif self.index == 1:
                self.world.leave_state = True
                self.exit_state()
            """elif self.index == 1:
                new_state = Options(self.game)
                new_state.enter_state()"""

        hovers = pygame.sprite.spritecollide(self.mouse, self.buttons, False)
        self.hovered = None
        for hover in hovers:
            self.hovered = hover
            if inputs["l_click"]:
                if hover.key == "continue":
                    self.exit_state()
                elif hover.key == "quit":
                    self.world.leave_state = True
                    self.exit_state()
                """
                elif hover.key == "options":
                    new_state = Options(self.game)
                    new_state.enter_state()"""
        self.game.reset_keys()

    def draw(self, display):
        self.prev_state.draw(display)
        display.blit(self.fade, self.rect)
        self.buttons.draw(display)
        if self.hovered:
            display.blit(self.hovered.fade, self.hovered.rect)
        display.blit(self.mouse.image, self.mouse.rect)
        display.blit(self.cursor_image, self.cursor_rect)
    
class Button(pygame.sprite.Sprite):
    def __init__(self, game, x, y, img, key):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.key = key
        self.image = pygame.image.load(path.join(self.game.assets_dir, img)).convert_alpha()
        self.fade = pygame.Surface((120, 60))
        self.fade.set_alpha(100)
        self.fade.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Mouse(pygame.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        pygame.mouse.set_visible(False)
        self.image = pygame.image.load(path.join(self.game.assets_dir, "kunai1.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        pygame.mouse.set_pos(WIDTH/2, HEIGHT/2)
        self.rect.center = (WIDTH/2, HEIGHT/2)
    
    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        if self.rect.centerx >= WIDTH:
            self.rect.centerx = WIDTH
        elif self.rect.centerx <= 0:
            self.rect.centerx = 0
        if self.rect.centery >= HEIGHT:
            self.rect.centery = HEIGHT
        elif self.rect.centery <= 0:
            self.rect.centery = 0