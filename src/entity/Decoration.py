import pygame

class Decoration:
    def __init__(self, x, y, texture):
        self.x = float(x)
        self.y = float(y)
        self.texture = texture
        self.width = texture.get_width()
        self.height = texture.get_height()
        
    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)
        
    def update(self, dt):
        pass 
        
    def render(self, surface, camera):
        surface.blit(self.texture, camera.apply(self.rect))
