import pygame
import json
from pygame.constants import *
from os import path
from states.title import Title
from states.options import Options
from settings import *
import controls
import asyncio

class Game():
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            self.joysticks.append(pygame.joystick.Joystick(i))
        for joystick in self.joysticks:
            joystick.init()
        self.sizes = pygame.display.get_desktop_sizes()
        self.SCREEN_W, self.SCREEN_H = self.sizes[0]
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H), pygame.NOFRAME)
        self.running, self.playing = True, True
        self.inputs = {"left": False, "right": False, "up": False, "down": False, "attack": False, "enter": False, "back": False, "jump": False, "l_click": False}
        self.state_stack = []
        self.samurai_anims = {"l_walk": [], "r_walk": [], "l_attack": [], "r_attack": [], "l_idle": [], "r_idle": [], "l_hit": [], "r_hit": [], "l_kill": [], "r_kill": []}
        self.player_anims = {"l_walk": [], "r_walk": [], "l_attack": [], "r_attack": [], "l_idle": [], "r_idle": [], "l_hit": [], "r_hit": [], "l_kill": [], "r_kill": []}
        self.ninja_anims = {"l_walk": [], "r_walk": [], "l_attack": [], "r_attack": [], "l_idle": [], "r_idle": [], "l_hit": [], "r_hit": [], "l_kill": [], "r_kill": []}
        self.sword_sounds = {"sh_parry": None, "sw_parry": None, "n_hit": None, "s_hit": None}
        self.volumes = None
        self.load_assets()
        self.load_states()
        self.clock = pygame.time.Clock()
        pygame.mixer.music.load(path.join(self.aud_dir, 'Boss Battle #2 V2.wav'))
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(self.volumes["music"])
        self.playing_music = True
        new_save = {    
            "keyboard": {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s, 
                "attack": pygame.K_j, "enter": pygame.K_RETURN, "back": pygame.K_BACKSPACE, "jump": pygame.K_k},
            "gamepad": {"jump": 0, "enter": 1, "attack": 2, "back": 3},
            "type": 0
            }
        save = controls.load("controls.json", new_save)
        self.control_handler = controls.Controls_Handler(save, "keyboard", self)

    async def game_loop(self):
        while self.playing:
            await asyncio.sleep(0)
            self.get_dt()
            self.get_events()
            self.update()
            self.draw()

    def get_events(self):
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    self.playing = False
                if event.key == self.control_handler.k_controls['left']:
                    self.inputs['left'] = True
                if event.key == self.control_handler.k_controls['right']:
                    self.inputs['right'] = True
                if event.key == self.control_handler.k_controls['up']:
                    self.inputs['up'] = True
                if event.key == self.control_handler.k_controls['down']:
                    self.inputs['down'] = True
                if event.key == self.control_handler.k_controls["attack"]:
                    self.inputs["attack"] = True
                if event.key == self.control_handler.k_controls["enter"]:
                    self.inputs["enter"] = True
                if event.key == self.control_handler.k_controls["back"]:
                    self.inputs["back"] = True
                if event.key == self.control_handler.k_controls["jump"]:
                    self.inputs["jump"] = True
            if event.type == pygame.KEYUP:
                if event.key == self.control_handler.k_controls['left']:
                    self.inputs['left'] = False
                if event.key == self.control_handler.k_controls['right']:
                    self.inputs['right'] = False
                if event.key == self.control_handler.k_controls['up']:
                    self.inputs['up'] = False
                if event.key == self.control_handler.k_controls['down']:
                    self.inputs['down'] = False
                if event.key == self.control_handler.k_controls["attack"]:
                    self.inputs["attack"] = False
                if event.key == self.control_handler.k_controls["enter"]:
                    self.inputs["enter"] = False
                if event.key == self.control_handler.k_controls["back"]:
                    self.inputs["back"] = False
                if event.key == self.control_handler.k_controls["jump"]:
                    self.inputs["jump"] = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.inputs["l_click"] = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.inputs["l_click"] = False

            if event.type == pygame.JOYHATMOTION:
                if event.value[0] == 1:
                    self.inputs["right"] = True
                    self.inputs["left"] = False
                if event.value[0] == -1:
                    self.inputs["left"] = True
                    self.inputs["right"] = False
                if event.value[0] == 0:
                    self.inputs["right"] = False
                    self.inputs["left"] = False
                if event.value[1] == 1:
                    self.inputs["up"] = True
                    self.inputs["down"] = False
                if event.value[1] == -1:
                    self.inputs["down"] = True
                    self.inputs["up"] = False
                if event.value[1] == 0:
                    self.inputs["up"] = False
                    self.inputs["down"] = False

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == self.control_handler.g_controls["attack"]:
                    self.inputs["attack"] = True
                if event.button == self.control_handler.g_controls["enter"]:
                    self.inputs["enter"] = True
                if event.button == self.control_handler.g_controls["back"]:
                    self.inputs["back"] = True
                if event.button == self.control_handler.g_controls["jump"]:
                    self.inputs["jump"] = True
                if event.button == 11:
                    self.inputs["up"] = True
                if event.button == 12:
                    self.inputs["down"] = True
                if event.button == 13:
                    self.inputs["left"] = True
                if event.button == 14:
                    self.inputs["right"] = True
            if event.type == pygame.JOYBUTTONUP:
                if event.button == self.control_handler.g_controls["attack"]:
                    self.inputs["attack"] = False
                if event.button == self.control_handler.g_controls["enter"]:
                    self.inputs["enter"] = False
                if event.button == self.control_handler.g_controls["back"]:
                    self.inputs["back"] = False
                if event.button == self.control_handler.g_controls["jump"]:
                    self.inputs["jump"] = False
                if event.button == 11:
                    self.inputs["up"] = False
                if event.button == 12:
                    self.inputs["down"] = False
                if event.button == 13:
                    self.inputs["left"] = False
                if event.button == 14:
                    self.inputs["right"] = False
    
    def update(self):
        #self.control_handler.update(self.inputs)
        self.state_stack[-1].update(self.dt, self.inputs)

    def draw(self):
        self.state_stack[-1].draw(self.canvas)
        #self.control_handler.draw(self.canvas)
        self.screen.blit(pygame.transform.scale(self.canvas, (self.SCREEN_W, self.SCREEN_H)), (0, 0))
        pygame.display.flip()
    
    def load_samurai_anims(self):
        sprite_dir = path.join(self.sprite_dir, "samurai")

        l_walk_image = pygame.image.load(path.join(sprite_dir, "samurai_left_walk.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_left_walk.json")) as l_walk_file:
            l_walk = json.load(l_walk_file)
        frames = l_walk["frames"]
        for i in range(len(frames)):
            filename = 'samurai_walk {}.aseprite'.format(i)
            data = l_walk['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_walk_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["l_walk"].append(image)
        l_walk_file.close()

        r_walk_image = pygame.image.load(path.join(sprite_dir, "samurai_right_walk.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_right_walk.json")) as r_walk_file:
            r_walk = json.load(r_walk_file)
        frames = r_walk["frames"]
        for i in range(len(frames)):
            filename = 'samurai_walk {}.aseprite'.format(i)
            data = r_walk['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_walk_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["r_walk"].append(image)
        r_walk_file.close()

        l_attack_image = pygame.image.load(path.join(sprite_dir, "samurai_left_attack.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_left_attack.json")) as l_attack_file:
            l_attack = json.load(l_attack_file)
        frames = l_attack["frames"]
        for i in range(len(frames)):
            filename = 'samurai_attack {}.aseprite'.format(i)
            data = l_attack['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_attack_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["l_attack"].append(image)
        l_attack_file.close()

        r_attack_image = pygame.image.load(path.join(sprite_dir, "samurai_right_attack.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_right_attack.json")) as r_attack_file:
            r_attack = json.load(r_attack_file)
        frames = r_attack["frames"]
        for i in range(len(frames)):
            filename = 'samurai_attack {}.aseprite'.format(i)
            data = r_attack['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_attack_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["r_attack"].append(image)
        r_attack_file.close()

        l_idle_image = pygame.image.load(path.join(sprite_dir, "samurai_left_idle.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_left_idle.json")) as l_idle_file:
            l_idle = json.load(l_idle_file)
        frames = l_idle["frames"]
        for i in range(len(frames)):
            filename = 'samurai {}.aseprite'.format(i)
            data = l_idle['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_idle_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["l_idle"].append(image)
        l_idle_file.close()

        r_idle_image = pygame.image.load(path.join(sprite_dir, "samurai_right_idle.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_right_idle.json")) as r_idle_file:
            r_idle = json.load(r_idle_file)
        frames = r_idle["frames"]
        for i in range(len(frames)):
            filename = 'samurai {}.aseprite'.format(i)
            data = r_idle['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_idle_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["r_idle"].append(image)
        r_idle_file.close()

        l_hit_image = pygame.image.load(path.join(sprite_dir, "samurai_left_hit.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_left_hit.json")) as l_hit_file:
            l_hit = json.load(l_hit_file)
        frames = l_hit["frames"]
        for i in range(len(frames)):
            filename = 'samurai_hit {}.aseprite'.format(i)
            data = l_hit['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_hit_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["l_hit"].append(image)
        l_hit_file.close()

        r_hit_image = pygame.image.load(path.join(sprite_dir, "samurai_right_hit.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_right_hit.json")) as r_hit_file:
            r_hit = json.load(r_hit_file)
        frames = r_hit["frames"]
        for i in range(len(frames)):
            filename = 'samurai_hit {}.aseprite'.format(i)
            data = r_hit['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_hit_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["r_hit"].append(image)
        r_hit_file.close()

        l_kill_image = pygame.image.load(path.join(sprite_dir, "samurai_left_kill.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_left_kill.json")) as l_kill_file:
            l_kill = json.load(l_kill_file)
        frames = l_kill["frames"]
        for i in range(len(frames)):
            filename = 'samurai_kill {}.aseprite'.format(i)
            data = l_kill['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_kill_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["l_kill"].append(image)
        l_kill_file.close()

        r_kill_image = pygame.image.load(path.join(sprite_dir, "samurai_right_kill.png")).convert_alpha()
        with open(path.join(sprite_dir, "samurai_right_kill.json")) as r_kill_file:
            r_kill = json.load(r_kill_file)
        frames = r_kill["frames"]
        for i in range(len(frames)):
            filename = 'samurai_kill {}.aseprite'.format(i)
            data = r_kill['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_kill_image, (0, 0), pygame.Rect(x, y, w, h))
            self.samurai_anims["r_kill"].append(image)
        r_kill_file.close()

    def load_player_anims(self):
        sprite_dir = path.join(self.sprite_dir, "player")

        l_walk_image = pygame.image.load(path.join(sprite_dir, "player_left_walk.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_left_walk.json")) as l_walk_file:
            l_walk = json.load(l_walk_file)
        frames = l_walk["frames"]
        for i in range(len(frames)):
            filename = 'player_walk {}.aseprite'.format(i)
            data = l_walk['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_walk_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["l_walk"].append(image)
        l_walk_file.close()

        r_walk_image = pygame.image.load(path.join(sprite_dir, "player_right_walk.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_right_walk.json")) as r_walk_file:
            r_walk = json.load(r_walk_file)
        frames = r_walk["frames"]
        for i in range(len(frames)):
            filename = 'player_walk {}.aseprite'.format(i)
            data = r_walk['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_walk_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["r_walk"].append(image)
        r_walk_file.close()

        l_attack_image = pygame.image.load(path.join(sprite_dir, "player_left_attack.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_left_attack.json")) as l_attack_file:
            l_attack = json.load(l_attack_file)
        frames = l_attack["frames"]
        for i in range(len(frames)):
            filename = 'player_attack {}.aseprite'.format(i)
            data = l_attack['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_attack_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["l_attack"].append(image)
        l_attack_file.close()

        r_attack_image = pygame.image.load(path.join(sprite_dir, "player_right_attack.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_right_attack.json")) as r_attack_file:
            r_attack = json.load(r_attack_file)
        frames = r_attack["frames"]
        for i in range(len(frames)):
            filename = 'player_attack {}.aseprite'.format(i)
            data = r_attack['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_attack_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["r_attack"].append(image)
        r_attack_file.close()

        l_idle_image = pygame.image.load(path.join(sprite_dir, "player_left_idle.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_left_idle.json")) as l_idle_file:
            l_idle = json.load(l_idle_file)
        frames = l_idle["frames"]
        for i in range(len(frames)):
            filename = 'player {}.aseprite'.format(i)
            data = l_idle['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_idle_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["l_idle"].append(image)
        l_idle_file.close()

        r_idle_image = pygame.image.load(path.join(sprite_dir, "player_right_idle.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_right_idle.json")) as r_idle_file:
            r_idle = json.load(r_idle_file)
        frames = r_idle["frames"]
        for i in range(len(frames)):
            filename = 'player {}.aseprite'.format(i)
            data = r_idle['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_idle_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["r_idle"].append(image)
        r_idle_file.close()

        l_hit_image = pygame.image.load(path.join(sprite_dir, "player_left_hit.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_left_hit.json")) as l_hit_file:
            l_hit = json.load(l_hit_file)
        frames = l_hit["frames"]
        for i in range(len(frames)):
            filename = 'player_hit {}.aseprite'.format(i)
            data = l_hit['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_hit_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["l_hit"].append(image)
        l_hit_file.close()

        r_hit_image = pygame.image.load(path.join(sprite_dir, "player_right_hit.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_right_hit.json")) as r_hit_file:
            r_hit = json.load(r_hit_file)
        frames = r_hit["frames"]
        for i in range(len(frames)):
            filename = 'player_hit {}.aseprite'.format(i)
            data = r_hit['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_hit_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["r_hit"].append(image)
        r_hit_file.close()

        l_kill_image = pygame.image.load(path.join(sprite_dir, "player_left_kill.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_left_kill.json")) as l_kill_file:
            l_kill = json.load(l_kill_file)
        frames = l_kill["frames"]
        for i in range(len(frames)):
            filename = 'player_kill {}.aseprite'.format(i)
            data = l_kill['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_kill_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["l_kill"].append(image)
        l_kill_file.close()

        r_kill_image = pygame.image.load(path.join(sprite_dir, "player_right_kill.png")).convert_alpha()
        with open(path.join(sprite_dir, "player_right_kill.json")) as r_kill_file:
            r_kill = json.load(r_kill_file)
        frames = r_kill["frames"]
        for i in range(len(frames)):
            filename = 'player_kill {}.aseprite'.format(i)
            data = r_kill['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_kill_image, (0, 0), pygame.Rect(x, y, w, h))
            self.player_anims["r_kill"].append(image)
        r_kill_file.close()
    
    def load_ninja_anims(self):
        sprite_dir = path.join(self.sprite_dir, "ninja")
        self.l_walk, self.r_walk, self.l_attack, self.r_attack, self.l_idle, self.r_idle = [], [], [], [], [], []

        l_walk_image = pygame.image.load(path.join(sprite_dir, "ninja_left_walk.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_left_walk.json")) as l_walk_file:
            l_walk = json.load(l_walk_file)
        frames = l_walk["frames"]
        for i in range(len(frames)):
            filename = 'ninja_walk {}.aseprite'.format(i)
            data = l_walk['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_walk_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["l_walk"].append(image)
        l_walk_file.close()

        r_walk_image = pygame.image.load(path.join(sprite_dir, "ninja_right_walk.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_right_walk.json")) as r_walk_file:
            r_walk = json.load(r_walk_file)
        frames = r_walk["frames"]
        for i in range(len(frames)):
            filename = 'ninja_walk {}.aseprite'.format(i)
            data = r_walk['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_walk_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["r_walk"].append(image)
        r_walk_file.close()

        l_attack_image = pygame.image.load(path.join(sprite_dir, "ninja_left_throw.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_left_throw.json")) as l_attack_file:
            l_attack = json.load(l_attack_file)
        frames = l_attack["frames"]
        for i in range(len(frames)):
            filename = 'ninja_throw {}.aseprite'.format(i)
            data = l_attack['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_attack_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["l_attack"].append(image)
        l_attack_file.close()

        r_attack_image = pygame.image.load(path.join(sprite_dir, "ninja_right_throw.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_right_throw.json")) as r_attack_file:
            r_attack = json.load(r_attack_file)
        frames = r_attack["frames"]
        for i in range(len(frames)):
            filename = 'ninja_throw {}.aseprite'.format(i)
            data = r_attack['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_attack_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["r_attack"].append(image)
        r_attack_file.close()

        l_idle_image = pygame.image.load(path.join(sprite_dir, "ninja_left_idle.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_left_idle.json")) as l_idle_file:
            l_idle = json.load(l_idle_file)
        frames = l_idle["frames"]
        for i in range(len(frames)):
            filename = 'ninja {}.aseprite'.format(i)
            data = l_idle['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_idle_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["l_idle"].append(image)
        l_idle_file.close()

        r_idle_image = pygame.image.load(path.join(sprite_dir, "ninja_right_idle.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_right_idle.json")) as r_idle_file:
            r_idle = json.load(r_idle_file)
        frames = r_idle["frames"]
        for i in range(len(frames)):
            filename = 'ninja {}.aseprite'.format(i)
            data = r_idle['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_idle_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["r_idle"].append(image)
        r_idle_file.close()

        l_hit_image = pygame.image.load(path.join(sprite_dir, "ninja_left_hit.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_left_hit.json")) as l_hit_file:
            l_hit = json.load(l_hit_file)
        frames = l_hit["frames"]
        for i in range(len(frames)):
            filename = 'ninja_hit {}.aseprite'.format(i)
            data = l_hit['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_hit_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["l_hit"].append(image)
        l_hit_file.close()

        r_hit_image = pygame.image.load(path.join(sprite_dir, "ninja_right_hit.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_right_hit.json")) as r_hit_file:
            r_hit = json.load(r_hit_file)
        frames = r_hit["frames"]
        for i in range(len(frames)):
            filename = 'ninja_hit {}.aseprite'.format(i)
            data = r_hit['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_hit_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["r_hit"].append(image)
        r_hit_file.close()

        l_kill_image = pygame.image.load(path.join(sprite_dir, "ninja_left_kill.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_left_kill.json")) as l_kill_file:
            l_kill = json.load(l_kill_file)
        frames = l_kill["frames"]
        for i in range(len(frames)):
            filename = 'ninja_kill {}.aseprite'.format(i)
            data = l_kill['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(l_kill_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["l_kill"].append(image)
        l_kill_file.close()

        r_kill_image = pygame.image.load(path.join(sprite_dir, "ninja_right_kill.png")).convert_alpha()
        with open(path.join(sprite_dir, "ninja_right_kill.json")) as r_kill_file:
            r_kill = json.load(r_kill_file)
        frames = r_kill["frames"]
        for i in range(len(frames)):
            filename = 'ninja_kill {}.aseprite'.format(i)
            data = r_kill['frames'][filename]['frame']
            x, y, w, h = data['x'], data['y'], data['w'], data['h']
            image = pygame.Surface((w, h), flags = SRCALPHA).convert_alpha()
            image.blit(r_kill_image, (0, 0), pygame.Rect(x, y, w, h))
            self.ninja_anims["r_kill"].append(image)
        r_kill_file.close()

    def load_assets(self):
        self.assets_dir = path.join("assets")
        self.sprite_dir = path.join(self.assets_dir, "sprites")
        self.font_dir = path.join(self.assets_dir, "font")
        self.aud_dir = path.join(self.assets_dir, "audio")
        v_save = {
            "master": .5,
            "music": .5,
            "sounds": .5
        }
        self.volumes = controls.load("volume.json", v_save)

        self.sword_sounds["sh_parry"] = pygame.mixer.Sound(path.join(self.aud_dir, 'sword_clash_2.wav'))
        self.sword_sounds["sw_parry"] = pygame.mixer.Sound(path.join(self.aud_dir, 'sword_clash_1.wav'))
        self.sword_sounds["n_hit"] = pygame.mixer.Sound(path.join(self.aud_dir, 'sword-1a.wav'))
        self.sword_sounds["s_hit"] = pygame.mixer.Sound(path.join(self.aud_dir, 'sword-arm-2b.wav'))
        self.load_samurai_anims()
        self.load_player_anims()
        self.load_ninja_anims()

    def get_dt(self):
        self.dt = self.clock.tick(FPS) * 0.001 * 60
    
    def draw_text(self, surface, text, size, colour, x, y):
        self.font = pygame.font.Font(path.join(self.font_dir, "PixelTandysoft-0rJG.ttf"), size)
        text_surface = self.font.render(text, True, colour)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)
    
    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        for input in self.inputs:
            self.inputs[input] = False
        
game = Game()
async def main():
    while game.running:
        await asyncio.sleep(0)
        await game.game_loop()
asyncio.run(main())
#pygame.quit()