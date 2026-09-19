import pygame
import random
import settings
from gale.state import BaseState
from gale.text import render_text

class DrDeadSceneState(BaseState):
    def __init__(self, ui_stack, on_close=None):
        super().__init__(None)
        self.ui_stack = ui_stack
        self.on_close = on_close
        
        self.bg_image = pygame.transform.scale(
            settings.TEXTURES.get("dr_dead_scene", pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))),
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        )
        
        self.phase = "WAIT_DIALOGUE_1"
        self.shake_intensity = 0
        self.you_are_not_alone_text = ""
        self.text_timer = 0
        self.target_text = "YOU ARE NOT ALONE"
        self.text_index = 0
        self.time_per_char = 0.5

    def enter(self, **kwargs):
        from src.systems.AudioManager import AudioManager
        AudioManager.play_sfx("horror")
        def after_dialogue():
            self.phase = "END_TEXT"
            
        from src.states.ui.DialogueState import DialogueState
        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["(...)", "(...)"],
            speaker="Andrea",
            on_close=after_dialogue
        ))

    def update(self, dt):
        if self.phase == "END_TEXT":
            self.text_timer += dt
            if self.text_timer >= self.time_per_char:
                self.text_timer = 0
                if self.text_index < len(self.target_text):
                    self.you_are_not_alone_text += self.target_text[self.text_index]
                    self.text_index += 1
            
            self.shake_intensity = 6

    def render(self, surface):
        surface.blit(self.bg_image, (0, 0))
        
        if self.phase == "END_TEXT":
            overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0,0))
            
            cx = settings.VIRTUAL_WIDTH // 2
            cy = settings.VIRTUAL_HEIGHT // 2
            
            box_w = 260
            box_h = 80
            pygame.draw.rect(surface, (20, 20, 20), (cx - box_w//2, cy - box_h//2, box_w, box_h))
            pygame.draw.rect(surface, (150, 150, 150), (cx - box_w//2, cy - box_h//2, box_w, box_h), 2)
            
            shake_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_y = random.randint(-self.shake_intensity, self.shake_intensity)
            
            render_text(surface, self.you_are_not_alone_text, settings.FONTS["large"], cx + shake_x, cy + shake_y, (255, 50, 50), center=True)
            
            if self.text_index >= len(self.target_text):
                render_text(surface, "[ENTER] Continuar", settings.FONTS["small"], cx, cy + 30, (200, 200, 200), center=True)

    def on_input(self, input_id, input_data):
        if input_data.pressed and input_id in ("confirm", "interact", "space", "return"):
            if self.phase == "END_TEXT" and self.text_index >= len(self.target_text):
                self.phase = "FADING"
                self.fade_alpha = 0.0
                from gale.timer import Timer
                def on_fade_done():
                    self.phase = "DEMO_END"
                Timer.tween(1.5, [(self, {'fade_alpha': 255.0})], on_finish=on_fade_done)
            elif self.phase == "DEMO_END":
                if self.on_close:
                    self.on_close()
        return True
