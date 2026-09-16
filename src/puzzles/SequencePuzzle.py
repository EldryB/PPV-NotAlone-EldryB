
import pygame
import random
from gale.timer import Timer
from gale.input_handler import InputData
from src.puzzles.BasePuzzle import BasePuzzle
from gale.text import render_text
import settings

class SequencePuzzle(BasePuzzle):
    def __init__(self, on_complete, on_fail):
        super().__init__(on_complete, on_fail)
        self.sequence = [random.randint(0, 3) for _ in range(4)]
        self.current_show_idx = 0
        self.current_input_idx = 0
        self.phase = "showing"
        self.timer = Timer()
        self.highlighted = -1
        
        self.colors = settings.SEQUENCE_COLORS
        self.bright_colors = settings.SEQUENCE_BRIGHT_COLORS
        
        cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
        self.buttons = [
            pygame.Rect(cx - 55, cy - 45, 50, 50), # Top-Left
            pygame.Rect(cx + 5, cy - 45, 50, 50),  # Top-Right
            pygame.Rect(cx - 55, cy + 15, 50, 50),  # Bottom-Left
            pygame.Rect(cx + 5, cy + 15, 50, 50)    # Bottom-Right
        ]
        
        self.timer.after(1.0, self._show_next)

    def _show_next(self):
        if self.current_show_idx < len(self.sequence):
            self.highlighted = self.sequence[self.current_show_idx]
            self.timer.after(0.5, self._dim)
        else:
            self.phase = "input"

    def _dim(self):
        self.highlighted = -1
        self.current_show_idx += 1
        self.timer.after(0.2, self._show_next)
        
    def update(self, dt: float) -> None:
        self.timer.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        pygame.draw.rect(surface, (40, 40, 40), (40, 10, 240, 160))
        pygame.draw.rect(surface, (200, 200, 200), (40, 10, 240, 160), 2)
        
        title = "Memoriza el patron..." if self.phase == "showing" else "Tu turno"
        render_text(surface, title, settings.FONTS["medium"], settings.VIRTUAL_WIDTH // 2, 25, (255, 255, 255), center=True)
        
        for i, rect in enumerate(self.buttons):
            color = self.bright_colors[i] if i == self.highlighted else self.colors[i]
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.phase != "input":
            return
            
        btn_idx = -1
        if input_id == "click" and input_data.pressed:
            mx, my = input_data.position
            vx = mx * settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH
            vy = my * settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT
            for i, rect in enumerate(self.buttons):
                if rect.collidepoint(vx, vy):
                    btn_idx = i
                    break
                    
        if input_data.pressed:
            if input_id == "move_left": btn_idx = 0
            elif input_id == "move_right": btn_idx = 1
            elif input_id == "move_up": btn_idx = 2
            elif input_id == "move_down": btn_idx = 3

        if btn_idx != -1:
            if btn_idx == self.sequence[self.current_input_idx]:
                self.highlighted = btn_idx
                self.timer.after(0.2, lambda: setattr(self, "highlighted", -1))
                self.current_input_idx += 1
                if self.current_input_idx >= len(self.sequence):
                    self._complete()
            else:
                self._fail()
