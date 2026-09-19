import pygame
from gale.state import BaseState
from gale.text import render_text
import settings

class SanityTutorialState(BaseState):
    def __init__(self, stack, on_close=None):
        super().__init__(None)
        self.stack = stack
        self.on_close = on_close

    def render(self, surface):
        cx = settings.VIRTUAL_WIDTH // 2
        cy = settings.VIRTUAL_HEIGHT // 2

        box_w, box_h = 300, 160
        box_x = cx - box_w // 2
        box_y = cy - box_h // 2

        inst_bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        inst_bg.fill((20, 20, 20, 230))
        surface.blit(inst_bg, (box_x, box_y))
        pygame.draw.rect(surface, (255, 200, 50), (box_x, box_y, box_w, box_h), 2)

        render_text(surface, "Tutorial: Cordura y Pastillas", settings.FONTS["medium"], cx, box_y + 18, (255, 220, 50), center=True)
        render_text(surface, "Si tu cordura baja demasiado, sufriras", settings.FONTS["small"], cx, box_y + 45, (255, 255, 255), center=True)
        render_text(surface, "alucinaciones. Si llega a cero, pierdes.", settings.FONTS["small"], cx, box_y + 60, (255, 255, 255), center=True)
        render_text(surface, "Tu cordura baja al fallar en los retos.", settings.FONTS["small"], cx, box_y + 85, (255, 100, 100), center=True)
        render_text(surface, "Abre el inventario y usa pastillas para recuperarla.", settings.FONTS["small"], cx, box_y + 110, (100, 255, 100), center=True)

        if int(pygame.time.get_ticks() / 500) % 2 == 0:
            render_text(surface, "Presiona ENTER para cerrar", settings.FONTS["small"], cx, box_y + 140, (100, 255, 100), center=True)

    def on_input(self, input_id, input_data):
        if input_data.pressed and input_id in ("confirm", "interact", "quit", "cancel"):
            self.stack.pop()
            if self.on_close:
                self.on_close()
        return True
