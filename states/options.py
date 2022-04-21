import pygame 
from pygame.constants import *
from states.state import State
from settings import *
from os import path
import controls

class Options(State):
    def __init__(self, game):
        State.__init__(self, game)
        self.game = game
        c_save = {    
            "keyboard": {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s, 
                "attack": pygame.K_j, "enter": pygame.K_RETURN, "back": pygame.K_BACKSPACE, "jump": pygame.K_k},
            "gamepad": {"jump": 0, "enter": 1, "attack": 2, "back": 3},
            "type": 0
            }
        v_save = {
            "master": .5,
            "music": .5,
            "sounds": .5
        }
        self.c_save = controls.load("controls.json", c_save)
        self.volumes = controls.load("volume.json", v_save)
        self.image = pygame.image.load(path.join(self.game.assets_dir, "Retribution_Title.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.fade = pygame.Surface((self.rect.width, self.rect.height))
        self.fade.set_alpha(200)
        self.fade.fill(BLACK)
        self.mouse = Mouse(game)
        self.master = Volume(WIDTH/5, 128, "Master:", self.game, self.volumes["master"])
        self.music = Volume(WIDTH/5, 192, "Music:", self.game, self.volumes["music"])
        self.sounds = Volume(WIDTH/5, 256, "Sounds:", self.game, self.volumes["sounds"])
        self.buttons = [self.master, self.music, self.sounds]
        self.edit_audio = False
        self.edit_gamepad = False
        self.edit_keyboard = False
        self.edit_controls = False
        self.cursor_image = pygame.transform.rotate(pygame.image.load(path.join(self.game.assets_dir, "cursor.png")).convert_alpha(), 90)
        self.cursor_rect = self.cursor_image.get_rect()
        self.cursor_rect.center = WIDTH/2-96, 140
        self.m_buttons = pygame.sprite.Group()
        self.audio_button = Button(self.game, WIDTH/2, 140, "audio.png","audio")
        self.gamepad_button = Button(self.game, WIDTH/2, 220, "gamepad1.png","gamepad")
        self.keyboard_button = Button(self.game, WIDTH/2, 300, "keyboard.png","keyboard")
        self.m_buttons.add(self.audio_button)
        self.m_buttons.add(self.gamepad_button)
        self.m_buttons.add(self.keyboard_button)
        self.hovered = None
        self.index = 0
        self.control_handler = controls.Controls_Handler(self.c_save, "keyboard", self.game)
    
    def move_cursor(self, inputs):
        if inputs["down"]:
            self.index = (self.index-1) % 3
        elif inputs["up"]:
            self.index = (self.index+1) % 3

        if self.edit_audio:
            if self.index == 0:
                self.cursor_rect.centery = 128
            elif self.index == 1:
                self.cursor_rect.centery = 192
            elif self.index == 2:
                self.cursor_rect.centery = 256
        else:
            if self.index == 0:
                self.cursor_rect.centery = 140
            elif self.index == 1:
                self.cursor_rect.centery = 220
            elif self.index == 2:
                self.cursor_rect.centery = 300

    def update(self, dt, inputs):
        self.mouse.update()
        self.move_cursor(inputs)
        if not self.edit_audio and not self.edit_gamepad and not self.edit_keyboard:
            self.move_cursor(inputs)
            if inputs["back"]:
                self.exit_state()

            if inputs["enter"]:
                self.game.reset_keys()
                if self.index == 0:
                    self.edit_audio = True
                elif self.index == 1:
                    self.edit_gamepad = True
                elif self.index == 2:
                    self.edit_keyboard = True

            hovers = pygame.sprite.spritecollide(self.mouse, self.m_buttons, False)
            self.hovered = None
            for hover in hovers:
                self.hovered = hover
                if inputs["l_click"]:
                    if hover.key == "audio":
                        self.edit_audio = True
                    elif hover.key == "gamepad":
                        self.edit_gamepad = True
                    elif hover.key == "keyboard":
                        self.edit_keyboard = True

        if self.edit_audio:
            self.cursor_rect.centerx = 40
            self.move_cursor(inputs)
            for button in self.buttons:
                hover = pygame.sprite.collide_rect(self.mouse, button.plus)
                if hover:
                    if inputs["l_click"]:
                        if round(button.volume, 1) < 1:
                            button.volume += .1
            for button in self.buttons:
                hover = pygame.sprite.collide_rect(self.mouse, button.minus)
                if hover:
                    if inputs["l_click"]:
                        if round(button.volume, 1) > 0:
                            button.volume -= .1

            if self.index == 0:
                if inputs["left"]:
                    if round(self.master.volume, 1) > 0:
                        self.master.volume -= .1
                elif inputs["right"]:
                    if round(self.master.volume, 1) < 1:
                        self.master.volume += .1

            elif self.index == 1:
                if inputs["left"]:
                    if round(self.music.volume, 1) > 0:
                        self.music.volume -= .1
                elif inputs["right"]:
                    if round(self.music.volume, 1) < 1:
                        self.music.volume += .1

            elif self.index == 2:
                if inputs["left"]:
                    if round(self.sounds.volume, 1) > 0:
                        self.sounds.volume -= .1
                elif inputs["right"]:
                    if round(self.sounds.volume, 1) < 1:
                        self.sounds.volume += .1

            self.volumes["master"] = round(self.master.volume, 1)
            self.volumes["music"] = round(self.music.volume, 1)
            self.volumes["sounds"] = round(self.sounds.volume, 1)
            if inputs["back"]:
                if self.volumes["master"] < self.volumes["music"] or self.volumes["master"] < self.volumes["sounds"]:
                    self.volumes["music"] = self.volumes["master"]
                    self.volumes["sounds"] = self.volumes["master"]
                controls.write_file("volume.json", self.volumes)
                #self.prev_state.volumes = self.prev_state.load_volume()
                self.exit_state()
        elif self.edit_gamepad and not self.edit_controls:
            self.control_handler = controls.Controls_Handler(self.c_save, "gamepad", self.game)
            self.edit_controls = True
        elif self.edit_keyboard and not self.edit_controls:
            self.control_handler = controls.Controls_Handler(self.c_save, "keyboard", self.game)
            self.edit_controls = True
        
        if self.edit_controls:
            self.control_handler.update(inputs)
            if inputs["back"]:
                self.game.control_handler.k_controls = self.control_handler.k_controls
                self.game.control_handler.g_controls = self.control_handler.g_controls
                self.exit_state()
        self.game.reset_keys()
    
    def draw(self, display):
        display.blit(self.image, self.rect)
        display.blit(self.fade, self.rect)
        if not self.edit_audio and not self.edit_gamepad and not self.edit_keyboard:
            self.game.draw_text(display, "Options", 40, WHITE, WIDTH/2, 64)
            self.m_buttons.draw(display)
            display.blit(self.cursor_image, self.cursor_rect)
            if self.hovered:
                display.blit(self.hovered.fade, self.hovered.rect)
        elif self.edit_audio:
            self.game.draw_text(display, "Audio", 40, WHITE, WIDTH/2, 64)
            self.master.draw(display, self.volumes["master"])
            self.music.draw(display, self.volumes["music"])
            self.sounds.draw(display, self.volumes["sounds"])
            display.blit(self.cursor_image, self.cursor_rect)
        elif self.edit_gamepad or self.edit_keyboard:
            self.control_handler.draw(display)

        display.blit(self.mouse.image, self.mouse.rect)

class Volume():
    def __init__(self, x, y, text, game, volume):
        self.game = game
        self.plus = Plus(self.game, x+384, y)
        self.minus = Minus(self.game, x+128, y)
        self.volume = volume
        self.text = text
        self.x = x
        self.y = y
    
    def draw_bar(self, display, x, y, pct):
        if pct < 0:
            pct = 0
        fill = (pct/10) * 192
        fill_rect = pygame.Rect(x, y, fill, 8)
        pygame.draw.rect(display, WHITE, fill_rect)
    
    def draw(self, display, volume):
        self.draw_bar(display, self.x+160, self.y-4, int(volume*10))
        display.blit(self.plus.image, self.plus.rect)
        display.blit(self.minus.image, self.minus.rect)
        self.game.draw_text(display, self.text, 24, WHITE, self.x, self.y)
        self.game.draw_text(display, str(int(volume*10)), 24, WHITE, self.x+64, self.y)
    
class Plus(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.assets_dir, "plus.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
class Minus(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(self.game.assets_dir, "minus.png")).convert_alpha()
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