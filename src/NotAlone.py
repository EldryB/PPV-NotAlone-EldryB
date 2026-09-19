import pygame
from gale.game import Game
from gale.input_handler import InputData
from gale.state import StateMachine

import settings
from src.states.game.TitleState import TitleState
from src.states.game.IntroState import IntroState
from src.states.game.PlayState import PlayState
from src.states.game.GameOverState import GameOverState
from src.states.game.EndingState import EndingState

class NotAlone(Game):
    def init(self) -> None:
        self.state_machine = StateMachine({
            "title": TitleState,
            "intro": IntroState,
            "play": PlayState,
            "game_over": GameOverState,
            "ending": EndingState,
        })
        self.state_machine.change("title")

    def update(self, dt: float) -> None:
        self.state_machine.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.state_machine.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.state_machine.on_input(input_id, input_data)
