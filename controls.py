from os import path
import json, pygame
from settings import *

assets_dir = path.join("assets")

def load_existing(savefile):
    with open(path.join(assets_dir, savefile), 'r+') as file:
        save = json.load(file)
    return save

def write_file(savefile, save):
    file = open(path.join(assets_dir, savefile), "w")
    json.dump(save, file, indent=4)

def load(savefile, save):
    try:
        save = load_existing(savefile)
    except:
        write_file(savefile, save)
    return save

def reset_keys(inputs):
    for input in inputs:
        inputs[input] = False
    return inputs

class Controls_Handler():
    def __init__(self, save, device, game):
        self.game = game
        self.save_file = save
        self.xbox_buttons = ["A", "B", "X", "Y", "LB", "RB", "BACK", "START", "L IN", "R IN", "GUIDE"]
        self.ps_buttons = ["CROSS", "CIRCLE", "SQUARE", "TRIANGLE", "L1", "R1", "OPTIONS", "START", "L3", "R3", "PS"]
        self.device = device
        self.type = self.save_file["type"]
        if self.type == 0:
            self.button_list = self.xbox_buttons
            self.g_name = "Xbox Controls" 
        elif self.type == 1:
            self.button_list = self.ps_buttons
            self.g_name = "Playstation Controls"
        self.k_controls = self.save_file["keyboard"]
        self.g_controls = self.save_file["gamepad"]
        self.setup()

    def update(self, inputs):
        if self.type == 0:
            self.button_list = self.xbox_buttons
            self.g_name = "<- Xbox Controls ->" 
        elif self.type == 1:
            self.button_list = self.ps_buttons
            self.g_name = "<- Playstation Controls ->"

        if self.k_selected or self.g_selected: 
            self.set_new_control()
        else: 
            self.navigate_menu(inputs)

    def draw(self, surface):
        if self.device == "keyboard":
            self.game.draw_text(surface, "Keyboard Controls ", 40, WHITE, WIDTH/2, HEIGHT/8)
            self.display_controls(surface, self.k_controls)
        elif self.device == "gamepad":
            self.game.draw_text(surface, self.g_name, 40, WHITE, WIDTH/2, HEIGHT/8)
            self.display_controls(surface, self.g_controls)

    def navigate_menu(self, inputs):
        # Move the cursor up and down
        if self.device == "keyboard":
            if inputs["down"]: 
                self.curr_index = (self.curr_index + 1) % (len(self.k_controls))
            if inputs["up"]: 
                self.curr_index = (self.curr_index - 1) % (len(self.k_controls))
        elif self.device == "gamepad":
            if inputs["down"]: 
                self.curr_index = (self.curr_index + 1) % (len(self.g_controls))
            if inputs["up"]: 
                self.curr_index = (self.curr_index - 1) % (len(self.g_controls))
            if inputs["left"]: 
                self.type = (self.type+1) %2
            if inputs["right"]: 
                self.type = (self.type-1) %2
        # Switch between profiles
        # Handle Selection
        if self.device == "keyboard":
            if inputs["enter"] or inputs["attack"]:
                self.k_selected = True
        if self.device == "gamepad":
            if inputs["attack"] or inputs["enter"]:
                self.g_selected = True

    def set_new_control(self):
        selected_control = self.cursor_dict[self.curr_index]
        done = False
        while not done:
            for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and self.device == "keyboard":
                        if event.key not in self.k_controls.values():
                            self.k_controls[selected_control] = event.key
                            write_file("controls.json", self.save_file)
                            self.k_selected = False
                            done = True
                        elif event.key == self.k_controls["back"]:
                            self.k_selected = False
                            done = True
                    elif event.type == pygame.JOYBUTTONDOWN and self.device == "gamepad":
                        if event.button not in self.g_controls.values() and event.button <= 10:
                            self.g_controls[selected_control] = event.button
                            write_file("controls.json", self.save_file)
                            self.g_selected = False
                            done = True
                        elif event.button == self.g_controls["back"]:
                            self.g_selected = False
                            done = True

    def display_controls(self,surface, controls):
        if self.k_selected or self.g_selected:
            color = RED
        else:
            color = WHITE
        pygame.draw.rect(surface, color, (WIDTH/4 , HEIGHT/4 - 10 + (self.curr_index*24), 324, 24), 2)
        i = 0
        for control in controls:
            if self.device == "keyboard":
                self.game.draw_text(surface, control + ' - ' + pygame.key.name(controls[control]), 24, WHITE, WIDTH/2, HEIGHT/4 + i)
            elif self.device == "gamepad":
                self.game.draw_text(surface, control + ' - ' + self.button_list[controls[control]], 24, WHITE, WIDTH/2, HEIGHT/4 + i)
            i += 24

    def setup(self):
        self.k_selected = False
        self.g_selected = False
        self.cursor_dict = {}
        self.curr_index = 0
        i = 0
        if self.device == "keyboard":
            for control in self.k_controls:
                self.cursor_dict[i] = control
                i += 1
            self.cursor_dict[i] = "Set"
        elif self.device == "gamepad":
            for control in self.g_controls:
                self.cursor_dict[i] = control
                i += 1
            self.cursor_dict[i] = "Set"