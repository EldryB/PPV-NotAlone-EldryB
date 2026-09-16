import pygame
from src.entity.NPC import NPC

class Jezu(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, "Jezu", "jezu_intro")
        
     
        self.image.fill((100, 100, 255)) 
