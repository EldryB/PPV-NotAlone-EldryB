import pygame
from gale.state import BaseState
from gale.timer import Timer
from gale.input_handler import InputData
from gale.text import render_text
import settings

class IntroState(BaseState):
    def enter(self, **kwargs) -> None:
        self.text_alpha = 0.0
        self.prompt_alpha = 0.0
        self.phase = "FADE_IN_TEXT"
        self.is_transitioning = False
        
        self.lines = [
            "Eres una estudiante",
            "universitaria, estas",
            "comenzando el tercer año",
            "de medicina, tienes dias",
            "sin dormir bien debido",
            "a tus examenes...",
            "pero sientes que hay",
            "alguien... o algo...",
            "que no te deja sola..."
        ]
        self.prompt = "(presiona enter para comenzar)"
        
        # Intermediate surfaces to handle alpha correctly
        self.text_surf = pygame.Surface((settings.VIRTUAL_WIDTH, 220), pygame.SRCALPHA)
        self.prompt_surf = pygame.Surface((settings.VIRTUAL_WIDTH, 50), pygame.SRCALPHA)
        
        Timer.tween(2.0, [(self, {'text_alpha': 255.0})], on_finish=self.show_prompt)

    def show_prompt(self):
        self.phase = "WAITING_INPUT"
        # Fade in the prompt slightly faster
        Timer.tween(1.0, [(self, {'prompt_alpha': 255.0})])

    def update(self, dt: float) -> None:
        pass

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.phase == "WAITING_INPUT" and input_data.pressed and input_id in ("confirm", "interact"):
            if not self.is_transitioning:
                self.is_transitioning = True
                self.phase = "FADE_OUT_TEXT"
                # Fade both text and prompt to 0
                Timer.tween(1.0, [(self, {'text_alpha': 0.0}), (self, {'prompt_alpha': 0.0})], on_finish=self.go_to_play)

    def go_to_play(self):
        self.state_machine.change("play", fade_in=True)

    def render(self, surface: pygame.Surface) -> None:
        # Background is completely black
        surface.fill((0, 0, 0))
        
        # Render text with alpha
        if self.text_alpha > 0:
            self.text_surf.fill((0, 0, 0, 0))
            
            # Render each line with a vertical offset
            y_offset = 10
            for line in self.lines:
                render_text(self.text_surf, line, settings.FONTS["medium"], settings.VIRTUAL_WIDTH // 2, y_offset, (255, 255, 255), center=True)
                y_offset += 20
                
            self.text_surf.set_alpha(int(max(0, min(255, self.text_alpha))))
            surface.blit(self.text_surf, (0, settings.VIRTUAL_HEIGHT // 2 - 110))
            
        if self.prompt_alpha > 0:
            self.prompt_surf.fill((0, 0, 0, 0))
            render_text(self.prompt_surf, self.prompt, settings.FONTS["small"], settings.VIRTUAL_WIDTH // 2, 25, (200, 200, 200), center=True)
            self.prompt_surf.set_alpha(int(max(0, min(255, self.prompt_alpha))))
            surface.blit(self.prompt_surf, (0, settings.VIRTUAL_HEIGHT - 60))
