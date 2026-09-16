import pygame
import random
from gale.state import BaseState
from gale.timer import Timer
import settings
from gale.text import render_text

class SimonSaysState(BaseState):
    def __init__(self, ui_stack, on_success=None, sanity_system=None):
        super().__init__(None)
        self.ui_stack = ui_stack
        self.on_success = on_success
        self.sanity_system = sanity_system
        
        self.bg_texture = settings.TEXTURES.get("simon_bg")
        self.btn_off_tex = settings.TEXTURES.get("simon_btn_off")
        self.btn_on_tex = settings.TEXTURES.get("simon_btn_on")
        
        # Dimensions 
        self.btn_w = 40
        self.btn_h = 30
        if self.btn_off_tex:
            self.btn_w = self.btn_off_tex.get_width() // 4
            self.btn_h = self.btn_off_tex.get_height() // 4
            
        self.quads = []
        for row in range(4):
            for col in range(4):
                self.quads.append(pygame.Rect(col * self.btn_w, row * self.btn_h, self.btn_w, self.btn_h))
                
        # group buttons
        self.spacing = 2
        total_w = (4 * self.btn_w) + (3 * self.spacing)
        total_h = (4 * self.btn_h) + (3 * self.spacing)
        
        self.start_x = settings.VIRTUAL_WIDTH - total_w - 15
        self.start_y = settings.VIRTUAL_HEIGHT - total_h - 15
        
        # Minigame variables
        self.sequence = []
        self.current_step = 0
        self.max_rounds = 5  
        
        # temp
        self.round_time = 10.0
        self.timer_active = False
        
        # fade variables
        self.fade_alpha = 255.0
        self.is_closing = False
        Timer.tween(0.8, [(self, {'fade_alpha': 0.0})])
        
        self.phase = "INSTRUCTION" # INSTRUCTION, STARTING, SHOWING, WAITING, WIN, FAIL, CLICKING
        self.lit_button = None
        
        # track input to prevent multiple rapid clicks
        self.mouse_was_pressed = False

    def next_round(self):
        if len(self.sequence) >= self.max_rounds:
            self.win()
            return
            
        self.sequence.append(random.randint(0, 15))
        self.current_step = 0
        self.phase = "SHOWING"
        
        Timer.after(0.5, lambda: self.show_sequence(0))

    def show_sequence(self, index):
        if index >= len(self.sequence):
            self.phase = "WAITING"
            self.round_time = 10.0
            self.timer_active = True
            return
            
        btn_idx = self.sequence[index]
        self.lit_button = btn_idx
        
        Timer.after(0.3, lambda: self.hide_sequence(index))

    def hide_sequence(self, index):
        self.lit_button = None
        Timer.after(0.1, lambda: self.show_sequence(index + 1))

    def update(self, dt: float) -> None:
        if self.timer_active:
            self.round_time -= dt
            if self.round_time <= 0:
                self.round_time = 0
                self.timer_active = False
                self.fail()

    def on_input(self, input_id: str, input_data) -> None:
        if self.is_closing or self.fade_alpha > 0:
            return
            
        if input_id == "quit" and input_data.pressed:
            self.trigger_close()
            return
            
        if self.phase == "INSTRUCTION" and input_data.pressed and (input_id == "confirm" or input_id == "interact"):
            self.phase = "STARTING"
            Timer.after(0.5, self.next_round)
            return

        # mouse down detection 
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        if mouse_pressed and not self.mouse_was_pressed:
            self.mouse_was_pressed = True
            
            if self.phase == "WAITING":
                mouse_x, mouse_y = self._get_virtual_mouse_pos()
                clicked_idx = self._get_clicked_button(mouse_x, mouse_y)
                if clicked_idx is not None:
                    self.process_click(clicked_idx)
        elif not mouse_pressed:
            self.mouse_was_pressed = False
                    
    def _get_virtual_mouse_pos(self):
        screen = pygame.display.get_surface()
        win_w, win_h = screen.get_size()
        
        mx, my = pygame.mouse.get_pos()
        scale_x = settings.VIRTUAL_WIDTH / win_w
        scale_y = settings.VIRTUAL_HEIGHT / win_h
        
        return mx * scale_x, my * scale_y

    def _get_clicked_button(self, mx, my):
        for i in range(16):
            row = i // 4
            col = i % 4
            bx = self.start_x + (col * (self.btn_w + self.spacing))
            by = self.start_y + (row * (self.btn_h + self.spacing))
            
            rect = pygame.Rect(bx, by, self.btn_w, self.btn_h)
            if rect.collidepoint(mx, my):
                return i
        return None

    def process_click(self, btn_idx):
        self.phase = "CLICKING"
        self.lit_button = btn_idx
        
        correct_idx = self.sequence[self.current_step]
        
        if btn_idx == correct_idx:
            # Correct
            self.current_step += 1
            if self.current_step >= len(self.sequence):
                self.timer_active = False # Detener temporizador
                Timer.after(0.3, self.finish_click_round)
            else:
                Timer.after(0.3, self.finish_click_step)
        else:
            # Wrong
            self.timer_active = False
            self.fail()

    def finish_click_step(self):
        self.lit_button = None
        self.phase = "WAITING"

    def finish_click_round(self):
        self.lit_button = None
        Timer.after(0.5, self.next_round)

    def fail(self):
        self.phase = "FAIL"
        Timer.after(1.0, self.reset_game)

    def reset_game(self):
        self.lit_button = None
        self.sequence = []
        self.phase = "STARTING"
        Timer.after(1.0, self.next_round)

    def win(self):
        self.phase = "WIN"
        self.lit_button = -1 
        Timer.after(1.5, self.trigger_close)
        
    def trigger_close(self):
        if not self.is_closing:
            self.is_closing = True
            Timer.tween(0.8, [(self, {'fade_alpha': 255.0})], on_finish=self.close_game)
        
    def close_game(self):
        if self.on_success:
            self.on_success()
        self.ui_stack.pop()

    def render(self, surface: pygame.Surface) -> None:

        if self.bg_texture:
            # Stretch background to virtual size
            surface.blit(pygame.transform.scale(self.bg_texture, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)), (0, 0))
        else:
            surface.fill((20, 20, 30))
            
        # darken background
        dark = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 160)) # Filtro oscuro semi-transparente
        surface.blit(dark, (0, 0))
            
        # draw buttonss
        for i in range(16):
            row = i // 4
            col = i % 4
            
            bx = self.start_x + (col * (self.btn_w + self.spacing))
            by = self.start_y + (row * (self.btn_h + self.spacing))
            
            is_lit = (self.lit_button == i) or (self.lit_button == -1)
            
            if self.phase == "FAIL" and self.lit_button == i:
                pygame.draw.rect(surface, (255, 0, 0), (bx - 2, by - 2, self.btn_w + 4, self.btn_h + 4))
            
            if is_lit and self.btn_on_tex:
                surface.blit(self.btn_on_tex, (bx, by), self.quads[i])
            elif not is_lit and self.btn_off_tex:
                surface.blit(self.btn_off_tex, (bx, by), self.quads[i])
            else:
                color = (0, 255, 0) if is_lit else (100, 100, 100)
                if self.phase == "FAIL" and self.lit_button == i: color = (255, 0, 0)
                pygame.draw.rect(surface, color, (bx, by, self.btn_w, self.btn_h))
                
        # temp
        if self.timer_active:
            timer_text = f"Tiempo: {self.round_time:.1f}s"
            color = (255, 50, 50) if self.round_time < 3.0 else (255, 255, 255)
            font = settings.FONTS["medium"]
            text_surf = font.render(timer_text, True, color)
            surface.blit(text_surf, (settings.VIRTUAL_WIDTH - text_surf.get_width() - 15, 15))

        # instructions
        if self.phase == "INSTRUCTION":

            box_w, box_h = 240, 80
            box_x = (settings.VIRTUAL_WIDTH - box_w) // 2
            box_y = (settings.VIRTUAL_HEIGHT - box_h) // 2
            
            # semi transparent box
            inst_bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            inst_bg.fill((20, 20, 20, 220))
            surface.blit(inst_bg, (box_x, box_y))
            pygame.draw.rect(surface, (200, 200, 200), (box_x, box_y, box_w, box_h), 1)
            
            render_text(surface, "Acertijo de Memoria", settings.FONTS["medium"], box_x + box_w//2, box_y + 15, (255,255,255), center=True)
            render_text(surface, "Repite el patrón de luces.", settings.FONTS["small"], box_x + box_w//2, box_y + 35, (200,200,200), center=True)
            render_text(surface, "Tienes 10 seg por ronda.", settings.FONTS["small"], box_x + box_w//2, box_y + 48, (200,200,200), center=True)
            
            # Flicker
            if int(pygame.time.get_ticks() / 500) % 2 == 0:
                render_text(surface, "Presiona ENTER para comenzar", settings.FONTS["small"], box_x + box_w//2, box_y + 65, (100,255,100), center=True)


        if self.sanity_system:
            self.sanity_system.render(surface)
            
        # transition Fade in/out
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, int(max(0, min(255, self.fade_alpha)))))
            surface.blit(fade_surf, (0, 0))
