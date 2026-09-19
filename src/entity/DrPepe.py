import pygame
from src.entity.NPC import NPC

import settings

class DrPepe(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, "Dr. Pepe", "dr_pepe_intro")
        
        self.width = 48
        self.height = 48
        self.texture = settings.TEXTURES["dr_pepe"]
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height).inflate(64, 64)

    def render(self, surface, camera):
        screen_pos = camera.world_to_screen((self.x, self.y))
        surface.blit(self.texture, screen_pos)
