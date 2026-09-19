import pygame
import random
import math
from gale.timer import Timer
from gale.input_handler import InputData
from src.puzzles.BasePuzzle import BasePuzzle
from gale.text import render_text
import settings

class MemoryPuzzle(BasePuzzle):
    def __init__(self, on_success, on_fail):
        super().__init__(on_success, on_fail)
        self.fails = 0
        self.max_fails = 3
        self.sanity_system = None
        self.digits = [0, 0, 0, 0, 0]
        self.selected = 0
        self.timer = Timer()
        self.time_limit = 14.0
        self.time_left = 14.0
        self.countdown = 3.0
        
        self.phase = "INTRO" # INTRO, COUNTDOWN, SHOWING, INPUT, ERROR, SUCCESS
        self.error_text = ""
        self.target_code = ""

    def start_countdown(self):
        self.phase = "COUNTDOWN"
        self.countdown = 3.0

    def setup_round(self):
        self.target_code = "".join(str(random.randint(0, 9)) for _ in range(5))
        self.digits = [0, 0, 0, 0, 0]
        self.selected = 0
        self.phase = "SHOWING"
        self.timer.after(3.0, self.start_input) # Show for 3 seconds
        
    def start_input(self):
        self.phase = "INPUT"
        self.time_left = self.time_limit

    def update(self, dt: float) -> None:
        self.timer.update(dt)
        if self.phase == "COUNTDOWN":
            self.countdown -= dt
            if self.countdown <= 0:
                self.setup_round()
        elif self.phase == "INPUT":
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.show_error("TIEMPO AGOTADO")

    def show_error(self, text):
        self.phase = "ERROR"
        self.error_text = text
        self.fails += 1
        if self.sanity_system:
            self.sanity_system.drain(25.0)
        self.timer.after(1.5, self.start_countdown)

    def _check_code(self):
        code_str = "".join(str(d) for d in self.digits)
        if code_str == self.target_code:
            self.phase = "SUCCESS"
            self.timer.after(1.0, self._complete)
        else:
            self.show_error("INCORRECTO")

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
        
        if self.phase == "INTRO":
            pygame.draw.rect(surface, (30, 30, 30), (cx - 150, cy - 80, 300, 160))
            pygame.draw.rect(surface, (150, 150, 150), (cx - 150, cy - 80, 300, 160), 2)
            render_text(surface, "Reto: Codigo de Memoria", settings.FONTS["medium"], cx, cy - 65, (255, 255, 100), center=True)
            render_text(surface, "Memoriza el codigo que parpadeara", settings.FONTS["small"], cx, cy - 40, (255, 255, 255), center=True)
            render_text(surface, "brevemente en la pantalla.", settings.FONTS["small"], cx, cy - 25, (255, 255, 255), center=True)
            render_text(surface, "Usa flechas para escribir y Enter para confirmar.", settings.FONTS["small"], cx, cy - 5, (200, 200, 200), center=True)
            render_text(surface, "Tienes un maximo de 3 errores.", settings.FONTS["small"], cx, cy + 15, (200, 200, 200), center=True)
            render_text(surface, "Cada fallo resta 25% de cordura.", settings.FONTS["small"], cx, cy + 35, (255, 100, 100), center=True)
            if int(pygame.time.get_ticks() / 500) % 2 == 0:
                render_text(surface, "[ENTER] para comenzar", settings.FONTS["small"], cx, cy + 60, (100, 255, 100), center=True)
            return
            
        if self.phase == "COUNTDOWN":
            render_text(surface, "PREPARATE", settings.FONTS["medium"], cx, cy - 20, (255, 255, 100), center=True)
            count_val = max(1, math.ceil(self.countdown))
            render_text(surface, str(count_val), settings.FONTS["large"], cx, cy + 20, (255, 255, 255), center=True)
            return

        if self.phase == "SHOWING":
            render_text(surface, "Memoriza:", settings.FONTS["medium"], cx, cy - 40, (255, 255, 255), center=True)
            render_text(surface, self.target_code, settings.FONTS["large"], cx, cy + 10, (100, 255, 100), center=True)
            render_text(surface, "", settings.FONTS["small"], cx, cy + 40, (255, 100, 100), center=True)
            return

        pygame.draw.rect(surface, (30, 30, 30), (cx - 130, cy - 60, 260, 120))
        pygame.draw.rect(surface, (150, 150, 150), (cx - 130, cy - 60, 260, 120), 2)
        
        if self.phase == "ERROR":
            render_text(surface, self.error_text, settings.FONTS["medium"], cx, cy - 45, (255, 50, 50), center=True)
        elif self.phase == "SUCCESS":
            render_text(surface, "CORRECTO!", settings.FONTS["medium"], cx, cy - 45, (50, 255, 50), center=True)
        else:
            render_text(surface, f"Tiempo: {max(0, self.time_left):.1f}s", settings.FONTS["medium"], cx, cy - 45, (255, 255, 255), center=True)
            
        render_text(surface, f"Errores: {self.fails}/{self.max_fails}", settings.FONTS["small"], 4, 63, (255, 100, 100), center=False)
        
        for i in range(5):
            dx = cx - 100 + i * 50
            color = (255, 255, 100) if (i == self.selected and self.phase == "INPUT") else (200, 200, 200)
            pygame.draw.rect(surface, (50, 50, 50), (dx - 20, cy - 20, 40, 50))
            pygame.draw.rect(surface, color, (dx - 20, cy - 20, 40, 50), 2)
            render_text(surface, str(self.digits[i]), settings.FONTS["large"], dx, cy, color, center=True)
            
            if i == self.selected and self.phase == "INPUT":
                render_text(surface, "^", settings.FONTS["small"], dx, cy - 25, color, center=True)
                render_text(surface, "v", settings.FONTS["small"], dx, cy + 35, color, center=True)

        if self.phase == "INPUT":
            render_text(surface, "[ENTER] Confirmar   [ESC] Salir", settings.FONTS["small"], cx, cy + 50, (200, 200, 200), center=True)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.phase == "INTRO":
            if input_data.pressed and input_id == "confirm":
                self.start_countdown()
            return
            
        if self.phase != "INPUT" or not input_data.pressed:
            return
            
        if input_id == "move_left":
            self.selected = max(0, self.selected - 1)
        elif input_id == "move_right":
            self.selected = min(4, self.selected + 1)
        elif input_id == "move_up":
            self.digits[self.selected] = (self.digits[self.selected] + 1) % 10
        elif input_id == "move_down":
            self.digits[self.selected] = (self.digits[self.selected] - 1) % 10
        elif input_id == "confirm":
            self._check_code()
