import pygame

class Interactable:
    def __init__(self, x, y, w, h, on_interact=None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.rect = pygame.Rect(x, y, w, h)
        self.on_interact = on_interact
        
    def interact(self):
        if self.on_interact:
            self.on_interact()

class MapTransition(Interactable):
    def __init__(self, x, y, w, h, target_map, spawn_point, on_transition=None):
        super().__init__(x, y, w, h)
        self.target_map = target_map
        self.spawn_point = spawn_point
        self.on_transition = on_transition
        
    def trigger(self):
        if self.on_transition:
            self.on_transition(self.target_map, self.spawn_point)
