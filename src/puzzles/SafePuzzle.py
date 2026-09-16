
import pygame
from gale.timer import Timer
from gale.input_handler import InputData
from src.puzzles.BasePuzzle import BasePuzzle
from gale.text import render_text
import settings

class SafePuzzle(BasePuzzle):
    def __init__(self, on_complete, on_fail):
        super().__init__(on_complete, on_fail)
        self.digits = [0, 0, 0]
        self.selected = 0
        self.timer = Timer()
        self.show_error = False

    def update(self, dt: float) -> None:
        self.timer.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        # Panel
        cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
        pygame.draw.rect(surface, (30, 30, 30), (cx - 100, cy - 60, 200, 120))
        pygame.draw.rect(surface, (150, 150, 150), (cx - 100, cy - 60, 200, 120), 2)
        
        title = "Codigo de la caja" if not self.show_error else "INCORRECTO"
        t_color = (255, 50, 50) if self.show_error else (255, 255, 255)
        render_text(surface, title, settings.FONTS["medium"], cx, cy - 45, t_color, center=True)
        
        for i in range(3):
            dx = cx - 60 + i * 60
            color = (255, 255, 100) if i == self.selected else (200, 200, 200)
            pygame.draw.rect(surface, (50, 50, 50), (dx - 20, cy - 20, 40, 50))
            pygame.draw.rect(surface, color, (dx - 20, cy - 20, 40, 50), 2)
            render_text(surface, str(self.digits[i]), settings.FONTS["large"], dx, cy, color, center=True)
            
            if i == self.selected:
                render_text(surface, "^", settings.FONTS["small"], dx, cy - 25, color, center=True)
                render_text(surface, "v", settings.FONTS["small"], dx, cy + 35, color, center=True)

        render_text(surface, "[ENTER] Confirmar", settings.FONTS["small"], cx, cy + 50, (200, 200, 200), center=True)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.show_error or not input_data.pressed:
            return
            
        if input_id == "move_left":
            self.selected = max(0, self.selected - 1)
        elif input_id == "move_right":
            self.selected = min(2, self.selected + 1)
        elif input_id == "move_up":
            self.digits[self.selected] = (self.digits[self.selected] + 1) % 10
        elif input_id == "move_down":
            self.digits[self.selected] = (self.digits[self.selected] - 1) % 10
        elif input_id == "confirm":
            self._check_code()

    def _check_code(self):
        code_str = "".join(str(d) for d in self.digits)
        if code_str == settings.safe_code_correct:
            self._complete()
        else:
            self.show_error = True
            self.timer.after(1.0, self._hide_error)
            
    def _hide_error(self):
        self.show_error = False
        self._fail() 
