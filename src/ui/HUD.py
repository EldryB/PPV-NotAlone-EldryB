import pygame
import settings

class HUD:
    def __init__(self, sanity_system, quest_manager, phone_manager=None):
        self.sanity_system = sanity_system
        self.quest_manager = quest_manager
        self.phone_manager = phone_manager
        
        # Surface for the lens's semi transparent background
        self.objective_bg = pygame.Surface((260, 40), pygame.SRCALPHA)
        self.objective_bg.fill((0, 0, 0, 150)) # Negro transparente
        
        self.objective_rect = self.objective_bg.get_rect(
            topright=(settings.VIRTUAL_WIDTH - 4, 4)
        )

    def update(self, dt):
        pass

    def render(self, surface):
        # sanity bar
        self.sanity_system.render(surface)
        
        # objetive window
        surface.blit(self.objective_bg, self.objective_rect)
        
        pygame.draw.rect(surface, (200, 200, 200), self.objective_rect, 1, border_radius=2)
        
        font_small = settings.FONTS["small"]
        
        has_msg = self.phone_manager and self.phone_manager.has_messages()
        
        if has_msg:
            import time
            flash = (int(time.time() * 4) % 2) == 0
            color = (255, 50, 50) if flash else (255, 255, 50)
            
            title_surf = font_small.render("ALERTA:", True, color)
            surface.blit(title_surf, (self.objective_rect.x + 5, self.objective_rect.y + 5))
            
            text_surf = font_small.render("TIENES MENSAJES NUEVOS", True, color)
            surface.blit(text_surf, (self.objective_rect.x + 5, self.objective_rect.y + 20))
        else:
            title_surf = font_small.render("OBJETIVO ACTUAL:", True, (255, 200, 50))
            surface.blit(title_surf, (self.objective_rect.x + 5, self.objective_rect.y + 5))
            
            # dynamic text
            current_text = self.quest_manager.current_objective_text()
            if current_text:
                text_surf = font_small.render(current_text, True, (255, 255, 255))
                surface.blit(text_surf, (self.objective_rect.x + 5, self.objective_rect.y + 20))

    def render_interaction_prompt(self, surface):
        font_small = settings.FONTS["small"]
        text_surf = font_small.render("Presiona E para interactuar", True, (255, 255, 255))
        bg_surf = pygame.Surface((text_surf.get_width() + 6, text_surf.get_height() + 4), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 180))
        # under sanity bar
        surface.blit(bg_surf, (4, 15))
        surface.blit(text_surf, (7, 17))
