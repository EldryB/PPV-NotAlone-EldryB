import pygame
from gale.state import BaseState
from gale.timer import Timer
import settings

class AnimatedPhoneSceneState(BaseState):
    def __init__(self, ui_stack, on_complete=None, overlay_key="foto1"):
        super().__init__(None)
        self.ui_stack = ui_stack
        self.on_complete = on_complete
        
        self.frames = []
        for i in range(1, 17):
            tex = settings.TEXTURES.get(f"phone_anim_{i}")
            if tex:
                tex = pygame.transform.scale(tex, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
                self.frames.append(tex)
                
        overlay_img = settings.TEXTURES.get(overlay_key)
        if self.frames and overlay_img:
            frame_17 = self.frames[-1].copy()
            frame_17.blit(overlay_img, (335, 43))
            self.frames.append(frame_17)
                
        self.current_frame_idx = 0
        self.fps = 4.0
        self.timer = 0.0
        self.is_done = False
        
        self.fade_alpha = 255.0
        self.is_closing = False
        
        self.phase = "FADE_IN" # FADE_IN, PLAYING, WAITING_EXIT, FADE_OUT
        
        Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=self.start_animation)

    def start_animation(self):
        self.phase = "PLAYING"

    def update(self, dt):
        if self.phase == "PLAYING" and self.frames:
            self.timer += dt
            if self.timer >= (1.0 / self.fps):
                self.timer = 0.0
                if self.current_frame_idx < len(self.frames) - 1:
                    self.current_frame_idx += 1
                    if self.current_frame_idx == len(self.frames) - 1:
                        from src.systems.AudioManager import AudioManager
                        AudioManager.play_sfx("horror")
                else:
                    self.phase = "WAITING_EXIT"

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
        if self.frames:
            surface.blit(self.frames[self.current_frame_idx], (0, 0))
        else:
            surface.fill((30, 30, 40))
            from gale.text import render_text
            render_text(surface, "ERROR: Phone Animation Missing", settings.FONTS["medium"], settings.VIRTUAL_WIDTH//2, settings.VIRTUAL_HEIGHT//2, (255,50,50), center=True)
            
        if self.fade_alpha > 0:
            dark = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            clamped_alpha = int(max(0, min(255, self.fade_alpha)))
            dark.fill((0, 0, 0, clamped_alpha))
            surface.blit(dark, (0, 0))
            
        if self.phase == "WAITING_EXIT" and self.fade_alpha == 0:
            from gale.text import render_text
            prompt = "[E] Salir"
            render_text(surface, prompt, settings.FONTS["small"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 20, (255, 255, 255), center=True)
