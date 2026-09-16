"""
El HUD (Head-Up Display) encapsula toda la interfaz que siempre está visible
durante el gameplay (como la salud, cordura, minimapas, y ventana de objetivos).
Esto mantiene a PlayState limpio.
"""
import pygame
import settings

class HUD:
    def __init__(self, sanity_system, quest_manager):
        self.sanity_system = sanity_system
        self.quest_manager = quest_manager
        
        # Surface for the lens's semi transparent background
        self.objective_bg = pygame.Surface((150, 40), pygame.SRCALPHA)
        self.objective_bg.fill((20, 20, 20, 200)) # Negro transparente
        
        self.objective_rect = self.objective_bg.get_rect(
            topright=(settings.VIRTUAL_WIDTH - 5, 5)
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
