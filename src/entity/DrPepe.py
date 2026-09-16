import pygame
from src.entity.NPC import NPC

class DrPepe(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, "Dr. Pepe", "dr_pepe_intro")
        
        self.image.fill((255, 100, 100)) 
