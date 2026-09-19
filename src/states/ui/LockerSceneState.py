import pygame
from gale.state import BaseState
from gale.timer import Timer
from src.states.ui.DialogueState import DialogueState
import settings

class LockerSceneState(BaseState):
    def __init__(self, ui_stack, inventory=None, quest_manager=None, mode="store_things", on_complete=None):
        super().__init__(None)
        self.ui_stack = ui_stack
        self.inventory = inventory
        self.quest_manager = quest_manager
        self.on_complete = on_complete
        from src.systems.AudioManager import AudioManager
        AudioManager.play_sfx("puerta_short")
        self.mode = mode
        
        self.bg_img = settings.TEXTURES.get("locker_open")
        if self.bg_img:
            self.bg_img = pygame.transform.scale(self.bg_img, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            
        self.keys_img = settings.TEXTURES.get("keys")
        self.pills_img = settings.TEXTURES.get("scene_pills")
        
        self.fade_alpha = 255.0
        
        if self.mode == "store_things":
            self.show_keys = False
            self.show_pills = True
            self.phase = "FADE_IN" # FADE_IN, DIALOGUE_1, DIALOGUE_2, WAITING_EXIT, FADE_OUT
            Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=self.start_dialogue_1)
        elif self.mode == "retrieve_keys":
            self.show_keys = False
            self.show_pills = False
            self.phase = "FADE_IN"
            Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=self.start_keys_dialogue)
            
        self.is_closing = False

    def start_keys_dialogue(self):
        self.phase = "DIALOGUE_KEYS"
        def on_k4_close():
            if self.quest_manager:
                self.quest_manager.notify("find_keys")
            self.phase = "WAITING_EXIT"
            
        def on_k3_close():
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["Creo que algo no esta bien..."], speaker="Andrea", on_close=on_k4_close))
            
        def on_k2_close():
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["Desde que llegue me he sentido extrana..."], speaker="Andrea", on_close=on_k3_close))
            
        def on_k1_close():
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["En donde estan mis llaves??"], speaker="Andrea", on_close=on_k2_close))

        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["Que??"],
            speaker="Andrea",
            on_close=on_k1_close
        ))

    def start_dialogue_1(self):
        self.phase = "DIALOGUE_1"
        def on_d1_close():
            self.show_keys = True
            Timer.after(0.5, self.start_dialogue_2)

        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["Voy a dejar mis llaves aqui."],
            speaker="Andrea",
            on_close=on_d1_close
        ))

    def start_dialogue_2(self):
        self.phase = "DIALOGUE_2"
        def on_d2_close():
            self.show_pills = False
            if self.inventory:
                self.inventory.add_pills(2)
            self.phase = "WAITING_EXIT"
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["(+2 pildoras)"], speaker=""))

        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["Deberia llevarme las pildoras"],
            speaker="Andrea",
            on_close=on_d2_close
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
        
        if self.show_keys and self.keys_img:
            surface.blit(self.keys_img, (11 * 16, 19 * 16))
            
        if self.show_pills and self.pills_img:
            surface.blit(self.pills_img, (23 * 16, 6 * 16))
            
        if self.fade_alpha > 0:
            dark = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            clamped_alpha = int(max(0, min(255, self.fade_alpha)))
            dark.fill((0, 0, 0, clamped_alpha))
            surface.blit(dark, (0, 0))
            
        if self.phase == "WAITING_EXIT" and self.fade_alpha == 0:
            from gale.text import render_text
            prompt = "[E] Salir"
            render_text(surface, prompt, settings.FONTS["small"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 20, (255, 255, 255), center=True)

