import pygame
import settings

class Building:
    def __init__(self, x, y, texture, name, player):
        self.x = float(x)
        self.y = float(y)
        self.texture = texture
        self.width = texture.get_width()
        self.height = texture.get_height()
        
        self.name = name
        self.player = player
        
        #state of floating animation
        self.text_alpha = 0.0
        self.text_offset = 0.0 
        
        self.font = settings.FONTS["small"]
        self.text_surf = self.font.render(self.name, True, (255, 255, 255))
        
        # background semitransparent
        self.bg_surf = pygame.Surface((self.text_surf.get_width() + 10, self.text_surf.get_height() + 4), pygame.SRCALPHA)
        self.bg_surf.fill((0, 0, 0, 180))
        
    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)
        
    def update(self, dt):
        
        proximity_rect = self.rect.inflate(40, 40)
        
        target_is_near = proximity_rect.colliderect(self.player.rect)
        
        # animation
        if target_is_near:
            self.text_alpha = min(255.0, self.text_alpha + 800 * dt)
            self.text_offset = max(-16.0, self.text_offset - 50 * dt)
        else:
            self.text_alpha = max(0.0, self.text_alpha - 800 * dt)
            self.text_offset = min(0.0, self.text_offset + 50 * dt)

    def render(self, surface, camera):
        surface.blit(self.texture, camera.apply(self.rect))
        
        if self.text_alpha > 0:
            alpha = int(self.text_alpha)
            self.bg_surf.set_alpha(alpha)
            self.text_surf.set_alpha(alpha)
            
            center_x = self.x + (self.width / 2)
            center_y = self.y + (self.height * (2/3)) + self.text_offset
            
            draw_x = center_x - (self.bg_surf.get_width() / 2)
            draw_y = center_y - (self.bg_surf.get_height() / 2)
            
            # config camera
            screen_pos = camera.apply(pygame.Rect(draw_x, draw_y, 1, 1))
            
            surface.blit(self.bg_surf, (screen_pos.x, screen_pos.y))
            surface.blit(self.text_surf, (screen_pos.x + 5, screen_pos.y + 2))
