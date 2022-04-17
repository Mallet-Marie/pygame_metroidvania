import pygame
from states.state import State
from states.world import World
from states.options import Options
from settings import *
from os import path
import json

class MainMenu(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        self.index = 0
        self.volumes = self.load_volume()
        self.buttons = pygame.sprite.Group()
        self.dead_buttons = pygame.sprite.Group()
        self.replay_buttons = pygame.sprite.Group()
        self.start_button = Button(self.game, WIDTH/5, 280, "start.png","start")
        self.options_button = Button(self.game, WIDTH/2, 280, "options.png", "options")
        self.quit_button = Button(self.game, WIDTH - WIDTH/5, 280, "quit.png", "quit")
        self.retry_button = Button(self.game, WIDTH/5, 320, "retry.png", "retry")
        self.retmenu_button = Button(self.game, WIDTH/2, 320, "retmenu.png", "retmenu")
        self.quitdesk_button = Button(self.game, WIDTH - WIDTH/5, 320, "quitdesk.png", "quitdesk")
        self.replay_button = Button(self.game, WIDTH/5, 320, "replay.png", "replay")
        self.dead_image = pygame.image.load(path.join(self.game.assets_dir, "death_screen.png")).convert()
        self.win_image = pygame.image.load(path.join(self.game.assets_dir, "win_screen.png")).convert()
        self.dead_rect = self.dead_image.get_rect()
        self.buttons.add(self.start_button)
        self.buttons.add(self.options_button)
        self.buttons.add(self.quit_button)
        self.dead_buttons.add(self.retry_button)
        self.dead_buttons.add(self.retmenu_button)
        self.dead_buttons.add(self.quitdesk_button)
        self.replay_buttons.add(self.replay_button)
        self.replay_buttons.add(self.retmenu_button)
        self.replay_buttons.add(self.quitdesk_button)
        self.mouse = Mouse(game)
        self.playing_song = False
        self.prev_state = self.game.title_screen
        self.hovered = None
    
    def load_volume(self):
        with open(path.join(self.game.assets_dir, "volume.json"), 'r+') as file:
            volumes = json.load(file)
        return volumes
    
    def update(self, dt, inputs):
        self.mouse.update()
        if not self.player_dead and not self.player_win:
            if not self.playing_song and not self.game.playing_music:
                pygame.mixer.music.load(path.join(self.game.aud_dir, 'Boss Battle #2 V2.wav'))
                pygame.mixer.music.play(loops=-1)
                pygame.mixer.music.set_volume(self.volumes["music"])
                self.playing_song = True
            hovers = pygame.sprite.spritecollide(self.mouse, self.buttons, False)
            self.hovered = None
            for hover in hovers:
                self.hovered = hover
                if inputs["l_click"]:
                    if hover.key == "start":
                        pygame.mixer.music.stop()
                        new_state = World(self.game)
                        new_state.enter_state()
                    elif hover.key == "options":
                        new_state = Options(self.game)
                        new_state.enter_state()
                    elif hover.key == "quit":
                        pygame.mixer.music.stop()
                        self.game.running = False
                        self.game.playing = False
        
        elif self.player_dead and not self.player_win:
            if not self.playing_song:
                pygame.mixer.music.load(path.join(self.game.aud_dir, 'Death-of-a-Ninja-_Game-Over_.wav'))
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(self.volumes["music"])
                self.playing_song = True
            hovers = pygame.sprite.spritecollide(self.mouse, self.dead_buttons, False)
            self.hovered = None
            for hover in hovers:
                self.hovered = hover
                if inputs["l_click"]:
                    pygame.mixer.music.stop()
                    if hover.key == "retry":
                        new_state = World(self.game)
                        new_state.enter_state()
                    elif hover.key == "retmenu":
                        self.player_win = False
                        self.player_dead = False
                    elif hover.key == "quitdesk":
                        self.game.running = False
                        self.game.playing = False
        
        elif not self.player_dead and self.player_win:
            if not self.playing_song:
                pygame.mixer.music.load(path.join(self.game.aud_dir, 'endingv2.wav'))
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(self.volumes["music"])
                self.playing_song = True
            hovers = pygame.sprite.spritecollide(self.mouse, self.replay_buttons, False)
            self.hovered = None
            for hover in hovers:
                self.hovered = hover
                if inputs["l_click"]:
                    pygame.mixer.music.stop()
                    if hover.key == "replay":
                        new_state = World(self.game)
                        new_state.enter_state()
                    elif hover.key == "retmenu":
                        self.player_win = False
                        self.player_dead = False
                    elif hover.key == "quitdesk":
                        self.game.running = False
                        self.game.playing = False

        self.game.reset_keys()


    def draw(self, display):
        if not self.player_dead and not self.player_win:
            self.prev_state.draw(display)
            self.buttons.draw(display)
        elif self.player_dead and not self.player_win:
            display.blit(self.dead_image, self.dead_rect)
            self.dead_buttons.draw(display)
        elif self.player_win and not self.player_dead:
            display.blit(self.win_image, self.dead_rect)
            self.replay_buttons.draw(display)

        if self.hovered:
            display.blit(self.hovered.fade, self.hovered.rect)
        display.blit(self.mouse.image, self.mouse.rect)
    
class Button(pygame.sprite.Sprite):
    def __init__(self, game, x, y, img, key):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.key = key
        self.image = pygame.image.load(path.join(self.game.assets_dir, img)).convert_alpha()
        self.rect = self.image.get_rect()
        self.fade = pygame.Surface((self.rect.width, self.rect.height))
        self.fade.set_alpha(100)
        self.fade.fill(BLACK)
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