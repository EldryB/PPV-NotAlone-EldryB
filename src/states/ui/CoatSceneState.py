import pygame
from gale.state import BaseState
from gale.timer import Timer
from src.states.ui.DialogueState import DialogueState
import settings

class CoatSceneState(BaseState):
    def __init__(self, ui_stack, inventory=None, quest_manager=None, on_complete=None):
        super().__init__(None)
        self.ui_stack = ui_stack
        self.inventory = inventory
        self.quest_manager = quest_manager
        self.on_complete = on_complete
        
        self.coat_img = settings.TEXTURES.get("coat_scene")
        self.no_coat_img = settings.TEXTURES.get("no_coat_scene")
        
        if self.coat_img:
            self.coat_img = pygame.transform.scale(self.coat_img, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        if self.no_coat_img:
            self.no_coat_img = pygame.transform.scale(self.no_coat_img, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            
        self.current_img = self.coat_img
        
        self.fade_alpha = 255.0
        self.is_closing = False
        
        self.phase = "FADE_IN" 
        
        Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=self.start_dialogue)

    def start_dialogue(self):
        self.phase = "DIALOGUE"
        lines = [
            "Es la bata del Dr. Pepe, voy a llevarsela"
        ]
        self.ui_stack.push(DialogueState(
            self.ui_stack, 
            lines=lines, 
            speaker="Andrea", 
            on_close=self.after_dialogue
        ))

    def after_dialogue(self):
        self.current_img = self.no_coat_img
        self.phase = "WAITING_EXIT"

    def update(self, dt):
        pass

    def on_input(self, input_id, input_data):
        if self.phase == "WAITING_EXIT" and input_data.pressed and input_id in ("interact", "confirm", "cancel"):
            if not self.is_closing:
                self.is_closing = True
                self.phase = "FADE_OUT"
                if self.inventory:
                    self.inventory.add_item("inv_coat")
                if self.quest_manager:
                    self.quest_manager.notify("get_coat")
                Timer.tween(1.0, [(self, {'fade_alpha': 255.0})], on_finish=self.finish_scene)

    def finish_scene(self):
        self.ui_stack.pop()
        if self.on_complete:
            self.on_complete()

    def render(self, surface):
        if self.current_img:
            surface.blit(self.current_img, (0, 0))
        else:
            surface.fill((30, 30, 40))
            
        if self.fade_alpha > 0:
            dark = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            clamped_alpha = int(max(0, min(255, self.fade_alpha)))
            dark.fill((0, 0, 0, clamped_alpha))
            surface.blit(dark, (0, 0))
            
        if self.phase == "WAITING_EXIT" and self.fade_alpha == 0:
            from gale.text import render_text
            prompt = "[E] Salir"
            render_text(surface, prompt, settings.FONTS["small"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 20, (255, 255, 255), center=True)
