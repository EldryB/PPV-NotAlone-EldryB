import pygame
from gale.ui.progress_bar import ProgressBar

class SanitySystem:
    def __init__(self):
        self.sanity = 100.0
        self.max_sanity = 100.0
        
        # ProgressBar at (4,4) size(80,6)
        self.bar = ProgressBar(4, 4, 80, 6, value=self.sanity, max_value=self.max_sanity)
        
        # Decay rates
        self.normal_decay_rate = 1.0 # 1 point per second
        self.puzzle_drain_rate = 3.0 # Extra points per second during puzzles
        
        self.is_decaying = False
        self.puzzle_drain_active = False
        
        # Visual overlays for sanity effects
        self.vignette_surface = pygame.Surface((320, 180), pygame.SRCALPHA)
        self.vignette_surface.fill((0, 0, 0, 150)) # Semi-transparent black for vignette
        
        self.red_surface = pygame.Surface((320, 180), pygame.SRCALPHA)
        self.red_surface.fill((180, 0, 0, 100)) # Semi-transparent red tint

    def start_decay(self):
        self.is_decaying = True

    def start_puzzle_drain(self):
        self.puzzle_drain_active = True
        
    def stop_puzzle_drain(self):
        self.puzzle_drain_active = False
        
    def restore(self, amount):
        self.sanity = min(self.max_sanity, self.sanity + amount)
        self.bar.value = self.sanity
        
    def drain(self, amount):
        self.sanity = max(0.0, self.sanity - amount)
        self.bar.value = self.sanity
        
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
        if self.sanity < 50.0:
            surface.blit(self.vignette_surface, (0, 0))
            
        if self.sanity < 25.0:
            surface.blit(self.red_surface, (0, 0))
            
        self.bar.render(surface)
