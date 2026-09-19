import pygame
from gale.timer import Timer
from gale.animation import Animation
from src.entity.NPC import NPC
import settings

class Jezu(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, "Jezu", "jezu_intro")
        
        # Override dimensions to match the 48x48 sprite
        self.width = 48
        self.height = 48
        
        # Expanded rectangular hitbox for easier interaction
        self.rect = pygame.Rect(self.x - 16, self.y - 16, 80, 80)
        
        self.texture = settings.TEXTURES["jezu_animation"]
        self.frames = settings.FRAMES["jezu_animation"]
        
        # Idle: frames 0 to 3
        self.animations = {
            "idle": Animation(self.frames[0:4], time_interval=0.2),
            "greeting": Animation(self.frames[4:13], time_interval=0.15, loops=1, on_finish=self._play_idle)
        }
        
        self.current_anim = self.animations["idle"]
        
        # Timer for the 6 second greeting cycle
        self.timer = Timer()
        self._schedule_greeting()
        
    def _schedule_greeting(self):
        if not getattr(self, 'has_talked', False):
            # Wait 6 seconds, then trigger greeting
            self.timer.after(6.0, self._play_greeting)
        
    def _play_greeting(self):
        if not getattr(self, 'has_talked', False):
            self.current_anim = self.animations["greeting"]
            self.current_anim.reset()
        
    def _play_idle(self):
        self.current_anim = self.animations["idle"]
        self.current_anim.reset()
        
        # Reschedule next greeting
        self._schedule_greeting()

    def interact(self):
        super().interact()
        self.has_talked = True
        self.timer.clear()
        self._play_idle()

    def update(self, dt):
        super().update(dt)
        self.timer.update(dt)
        self.current_anim.update(dt)
        
    def render(self, surface, camera):
        screen_pos = camera.world_to_screen((self.x, self.y))
        surface.blit(self.texture, screen_pos, self.current_anim.get_current_frame())
