
import pygame
from gale.state import BaseState
from gale.text import render_text
from gale.input_handler import InputData
from gale.ui.manager import UIManager
from gale.ui.container import Container
from gale.ui.list_view import ListView
import settings

class TitleState(BaseState):
    def enter(self, **kwargs) -> None:
        def start_game():
            self.state_machine.change("play")
            
        def quit_game():
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        menu = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, children=[
            ListView(
                settings.VIRTUAL_WIDTH // 2 - 50,
                settings.VIRTUAL_HEIGHT // 2,
                100, 60,
                items=[("Empezar Juego", start_game), ("Salir", quit_game)]
            )
        ])

        self.ui = UIManager(
            menu,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT,
            confirm_action="confirm",
            navigate_actions={"move_up": (0, -1), "move_down": (0, 1)}
        )

    def update(self, dt: float) -> None:
        self.ui.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 10, 15))
        render_text(surface, "Not Alone", settings.FONTS["large"], settings.VIRTUAL_WIDTH // 2, 40, (200, 200, 200), center=True)
        self.ui.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.ui.on_input(input_id, input_data)
