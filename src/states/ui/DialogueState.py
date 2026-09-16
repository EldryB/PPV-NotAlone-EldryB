"""
Estado de UI para la ventana de Diálogo.
Pausa el juego en segundo plano e intercepta el input.
"""
import pygame
from gale.state import BaseState
import settings

class DialogueState(BaseState):
    def __init__(self, ui_stack, lines=None, speaker="Desconocido"):
        super().__init__(None) # BaseState exige una state_machine, pasamos None
        self.ui_stack = ui_stack
        self.lines = lines if lines else ["..."]
        self.speaker = speaker
        self.current_line_index = 0
        
        # bottom box
        margin = 10
        self.height = 60
        self.rect = pygame.Rect(
            margin, 
            settings.VIRTUAL_HEIGHT - self.height - margin, 
            settings.VIRTUAL_WIDTH - (margin * 2), 
            self.height
        )
        
        #background
        self.bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.bg_surface.fill((10, 10, 20, 220)) # Azul muy oscuro transparente

    def enter(self, **kwargs):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        # Main boc
        surface.blit(self.bg_surface, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1, border_radius=3)
        
        # character name
        speaker_surf = settings.FONTS["medium"].render(self.speaker, True, (100, 200, 255))
        surface.blit(speaker_surf, (self.rect.x + 8, self.rect.y + 5))
        
        # text
        text = self.lines[self.current_line_index]
        text_surf = settings.FONTS["small"].render(text, True, (255, 255, 255))
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 25))
        
        # to continue
        indicator = settings.FONTS["small"].render("Espacio/Enter >", True, (150, 150, 150))
        surface.blit(
            indicator, 
            (self.rect.right - indicator.get_width() - 5, self.rect.bottom - indicator.get_height() - 5)
        )

    def on_input(self, input_id, input_data):
        if input_data.pressed:
            if input_id in ("interact", "confirm"):
                self.current_line_index += 1
                if self.current_line_index >= len(self.lines):
                    self.ui_stack.pop()
