import pygame
from gale.timer import Timer
from gale.input_handler import InputData
from src.puzzles.BasePuzzle import BasePuzzle
from gale.text import render_text
import settings

class SafePuzzle(BasePuzzle):
    def __init__(self, on_complete, on_fail, sanity_system=None):
        super().__init__(on_complete, on_fail)
        self.sanity_system = sanity_system
        self.digits = [0, 0, 0]
        self.selected = 0
        self.timer = Timer()
        self.show_error = False
        
        self.fails = 0
        self.phase = "INSTRUCTION"
        self.can_exit = True # INSTRUCTION -> INPUT

    def reset(self) -> None:
        super().reset()
        self.digits = [0, 0, 0]
        self.selected = 0
        self.show_error = False
        self.fails = 0
        self.phase = "INSTRUCTION"
        self.can_exit = True

    def update(self, dt: float) -> None:
        self.timer.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
        
        if self.phase == "INSTRUCTION":
            box_w, box_h = 300, 160
            box_x = cx - box_w//2
            box_y = cy - box_h//2
            
            inst_bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            inst_bg.fill((20, 20, 20, 220))
            surface.blit(inst_bg, (box_x, box_y))
            pygame.draw.rect(surface, (200, 200, 200), (box_x, box_y, box_w, box_h), 1)
            
            render_text(surface, "Caja Fuerte", settings.FONTS["medium"], cx, box_y + 15, (255,255,255), center=True)
            render_text(surface, "Encuentra la combinacion explorando", settings.FONTS["small"], cx, box_y + 40, (200,200,200), center=True)
            render_text(surface, "la universidad.", settings.FONTS["small"], cx, box_y + 55, (200,200,200), center=True)
            render_text(surface, "Usa las flechas para escribir y Enter para confirmar.", settings.FONTS["small"], cx, box_y + 75, (200,200,200), center=True)
            render_text(surface, "Puedes pulsar ESC para salir y explorar.", settings.FONTS["small"], cx, box_y + 95, (200,200,255), center=True)
            render_text(surface, "Codigos erroneos te quitan 25% de cordura.", settings.FONTS["small"], cx, box_y + 115, (255,100,100), center=True)
            
            if int(pygame.time.get_ticks() / 500) % 2 == 0:
                render_text(surface, "Presiona ENTER para comenzar", settings.FONTS["small"], cx, box_y + 140, (100,255,100), center=True)
            return

        # Panel
        pygame.draw.rect(surface, (30, 30, 30), (cx - 130, cy - 60, 260, 120))
        pygame.draw.rect(surface, (150, 150, 150), (cx - 130, cy - 60, 260, 120), 2)
        
        title = "Codigo de la caja" if not self.show_error else "INCORRECTO"
        t_color = (255, 50, 50) if self.show_error else (255, 255, 255)
        render_text(surface, title, settings.FONTS["medium"], cx, cy - 45, t_color, center=True)
        
        render_text(surface, f"Errores: {self.fails}", settings.FONTS["small"], 4, 63, (255, 100, 100))
        
        for i in range(3):
            dx = cx - 60 + i * 60
            color = (255, 255, 100) if i == self.selected else (200, 200, 200)
            pygame.draw.rect(surface, (50, 50, 50), (dx - 20, cy - 20, 40, 50))
            pygame.draw.rect(surface, color, (dx - 20, cy - 20, 40, 50), 2)
            render_text(surface, str(self.digits[i]), settings.FONTS["large"], dx, cy, color, center=True)
            
            if i == self.selected and not self.show_error:
                render_text(surface, "^", settings.FONTS["small"], dx, cy - 25, color, center=True)
                render_text(surface, "v", settings.FONTS["small"], dx, cy + 35, color, center=True)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return
            
        if self.phase == "INSTRUCTION":
            if input_id == "confirm":
                self.phase = "INPUT"
            return
            
        if self.show_error:
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
            self._handle_fail("INCORRECTO")
            
    def _handle_fail(self, msg):
        self.show_error = True
        self.fails += 1
        if self.sanity_system:
            self.sanity_system.drain(25.0)
            
        def reset_round():
            self.show_error = False
            self.time_left = self.time_limit
            self.digits = [0, 0, 0]
            self.selected = 0
            
        self.timer.after(1.0, reset_round)
