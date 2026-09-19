import pygame
from gale.state import BaseState
from gale.timer import Timer
from src.states.ui.DialogueState import DialogueState
import settings

class PhoneSceneState(BaseState):
    def __init__(self, ui_stack, message_data, on_complete=None):
        super().__init__(None)
        self.ui_stack = ui_stack
        self.message_data = message_data
        self.on_complete = on_complete
        
        self.phone_bg = settings.TEXTURES.get("phone_bg") # Placeholder for the first person phone
        if self.phone_bg:
            self.phone_bg = pygame.transform.scale(self.phone_bg, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
            
        self.photo_img = None
        if message_data.get('image'):
            self.photo_img = settings.TEXTURES.get(message_data['image'])
            
        self.fade_alpha = 255.0
        self.is_closing = False
        self.phase = "FADE_IN" 
        
        Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=self.start_dialogue)

    def start_dialogue(self):
        lines = self.message_data.get('dialogue', [])
        if lines:
            self.phase = "DIALOGUE"
            self.ui_stack.push(DialogueState(
                self.ui_stack, 
                lines=lines, 
                speaker="Andrea", 
                on_close=self.ready_to_exit
            ))
        else:
            self.ready_to_exit()

    def ready_to_exit(self):
        self.phase = "WAITING_EXIT"

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
        if self.phone_bg:
            surface.blit(self.phone_bg, (0, 0))
        else:
            # Fallback if phone_bg doesn't exist
            surface.fill((20, 20, 25))
            # Draw a fake phone frame
            cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
            pygame.draw.rect(surface, (10, 10, 10), (cx - 100, cy - 180, 200, 360), border_radius=15)
            pygame.draw.rect(surface, (200, 200, 200), (cx - 95, cy - 170, 190, 340))
            
        # Draw the photo overlay
        if self.photo_img:
            cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
            tw, th = self.photo_img.get_size()
            
            max_w, max_h = 180, 320
            if tw > max_w or th > max_h:
                scale = min(max_w/tw, max_h/th)
                tw, th = int(tw*scale), int(th*scale)
                scaled_img = pygame.transform.scale(self.photo_img, (tw, th))
                surface.blit(scaled_img, (cx - tw//2, cy - th//2 - 10))
            else:
                surface.blit(self.photo_img, (cx - tw//2, cy - th//2 - 10))
            
        if self.fade_alpha > 0:
            dark = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            clamped_alpha = int(max(0, min(255, self.fade_alpha)))
            dark.fill((0, 0, 0, clamped_alpha))
            surface.blit(dark, (0, 0))
            
        if self.phase == "WAITING_EXIT" and self.fade_alpha == 0:
            from gale.text import render_text
            prompt = "[E] Salir"
            render_text(surface, prompt, settings.FONTS["small"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 20, (255, 255, 255), center=True)
