import pygame

class NPC:
    def __init__(self, x, y, name, dialogue_key):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.name = name
        self.dialogue_key = dialogue_key
        
        # Placeholder surface for NPC graphics
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 0, 255)) 
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def interact(self):
        # Trigger dialogue in cutscene
        print(f"Interacting with {self.name}, dialogue key: {self.dialogue_key}")
        
    def update(self, dt):
        pass
        
    def render(self, surface, camera):
        # Get screen position relative to camera
        screen_pos = camera.world_to_screen((self.x, self.y))
        surface.blit(self.image, screen_pos)
