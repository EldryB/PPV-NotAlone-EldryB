
import pygame
from gale.state import BaseState
from gale.text import render_text
from gale.input_handler import InputData
import settings

class GameOverState(BaseState):
    def enter(self, **kwargs) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((20, 0, 0))
        render_text(surface, "TE HAS QUEDADO SIN CORDURA", settings.FONTS["large"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 - 20, (200, 50, 50), center=True)
        render_text(surface, "[ENTER] Volver al Título", settings.FONTS["medium"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 + 20, (255, 255, 255), center=True)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "confirm" and input_data.pressed:
            self.state_machine.change("title")
