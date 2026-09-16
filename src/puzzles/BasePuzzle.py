import pygame
from typing import Callable, Any

class BasePuzzle:
    def __init__(self, on_success: Callable[[], None] = None, on_fail: Callable[[], None] = None):
        self.is_active = False
        self.is_completed = False
        self.on_success = on_success
        self.on_fail = on_fail

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        pass

    def on_input(self, input_id: str, input_data: Any) -> None:
        pass

    def reset(self) -> None:

        self.is_active = True
        self.is_completed = False

    def _complete(self) -> None:
        self.is_active = False
        self.is_completed = True
        if self.on_success:
            self.on_success()

    def _fail(self) -> None:
        self.is_active = False
        if self.on_fail:
            self.on_fail()
