import pygame
from gale.ui.progress_bar import ProgressBar
import settings

class SanitySystem:
    def __init__(self):
        self.sanity = 100.0
        self.max_sanity = 100.0
        
        # Load Brain Texture
        self.brain_texture = settings.TEXTURES.get("brains")
        if not self.brain_texture:
            try:
                self.brain_texture = pygame.image.load(settings.BASE_DIR / 'assets' / 'graphics' / 'tilesets' / 'brains.png').convert_alpha()
            except:
                self.brain_texture = None
                
        self.brain_frames = []
        if self.brain_texture:
            width = self.brain_texture.get_width()
            frame_w = width / 5.0
            for i in range(5):
                rect = pygame.Rect(int(i * frame_w), 0, int((i+1)*frame_w) - int(i * frame_w), self.brain_texture.get_height())
                self.brain_frames.append(self.brain_texture.subsurface(rect))
                
        self.bar = ProgressBar(76, 24, 120, 10, value=max(0.0, self.sanity - 40.0), max_value=60.0, color=(255, 105, 180))
        
        # Decay rates
        self.normal_decay_rate = 0.0 
        self.puzzle_drain_rate = 3.0 
        
        self.is_decaying = False
        self.puzzle_drain_active = False

    def start_decay(self):
        self.is_decaying = True

    def start_puzzle_drain(self):
        self.puzzle_drain_active = True
        
    def stop_puzzle_drain(self):
        self.puzzle_drain_active = False
        
    def restore(self, amount):
        self.sanity = min(self.max_sanity, self.sanity + amount)
        self.bar.value = max(0.0, self.sanity - 40.0)
        
    def drain(self, amount):
        self.sanity = max(0.0, self.sanity - amount)
        self.bar.value = max(0.0, self.sanity - 40.0)
        
    def is_dead(self):
        return self.sanity <= 0.0
        
    def update(self, dt):
        if self.is_decaying:
            total_decay = self.normal_decay_rate
            if self.puzzle_drain_active:
                total_decay += self.puzzle_drain_rate
                
            self.drain(total_decay * dt)
            
        if hasattr(self.bar, 'update'):
            self.bar.update(dt)

    def render(self, surface):
        if self.brain_frames:
            # Brain is the bottom 40 points
            brain_sanity = min(self.sanity, 40.0)
            ratio = brain_sanity / 40.0
            
            frame_idx = 3
            if ratio > 0.75:
                frame_idx = 0
            elif ratio > 0.50:
                frame_idx = 1
            elif ratio > 0.25:
                frame_idx = 2
                
            # Render brain on the left
            surface.blit(self.brain_frames[frame_idx], (4, 4))
            
        # Render the bar
        self.bar.render(surface)
