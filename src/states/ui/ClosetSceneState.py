import pygame
from gale.state import BaseState
from gale.timer import Timer
from src.states.ui.DialogueState import DialogueState
import settings

class ClosetSceneState(BaseState):
    def __init__(self, ui_stack, on_complete=None):
        super().__init__(None)
        self.ui_stack = ui_stack
        self.on_complete = on_complete
        
        self.bg_img = settings.TEXTURES.get("closet_scene")
        if self.bg_img:
            self.bg_img = pygame.transform.scale(self.bg_img, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            
        self.fade_alpha = 255.0
        self.is_closing = False
        
        self.phase = "FADE_IN" 
        
        Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=self.start_dialogue_1)

    def start_dialogue_1(self):
        self.phase = "DIALOGUE_1"
        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["Otra vez el Dr. Basidas guardando craneos como si fueran de oro"],
            speaker="Andrea",
            on_close=self.start_dialogue_1_5
        ))
        
    def start_dialogue_1_5(self):
        self.phase = "DIALOGUE_1_5"
        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["Cual sera el codigo"],
            speaker="Andrea",
            on_close=self.start_dialogue_2
        ))
        
    def start_dialogue_2(self):
        self.phase = "DIALOGUE_2"
        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["Hay una nota aqui"],
            speaker="Andrea",
            on_close=self.start_dialogue_3
        ))
        
    def start_dialogue_3(self):
        self.phase = "DIALOGUE_3"
        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["Vamos a ver que dice"],
            speaker="Andrea",
            on_close=self.start_dialogue_4
        ))
        
    def start_dialogue_4(self):
        self.phase = "DIALOGUE_4"
        def on_final_close():
            self.phase = "WAITING_EXIT"
            
        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["7 LAS PAREDES HABLAN"],
            speaker="Nota",
            on_close=on_final_close
        ))

    def update(self, dt):
        pass

    def on_input(self, input_id, input_data):
        if self.phase == "WAITING_EXIT" and input_data.pressed and input_id in ("interact", "confirm", "cancel"):
            if not self.is_closing:
                self.is_closing = True
                self.phase = "FADE_OUT"
                Timer.tween(1.0, [(self, {'fade_alpha': 255.0})], on_finish=self.finish_scene)

    def finish_scene(self):
        self.ui_stack.pop()
        if self.on_complete:
            self.on_complete()

    def render(self, surface):
        if self.bg_img:
            surface.blit(self.bg_img, (0, 0))
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
