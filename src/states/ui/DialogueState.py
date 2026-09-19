import pygame
from gale.state import BaseState
import settings

class DialogueState(BaseState):
    def __init__(self, ui_stack, lines=None, speaker="Desconocido", on_close=None):
        super().__init__(None) # BaseState exige una state_machine, pasamos None
        self.ui_stack = ui_stack
        self.lines = lines if lines else ["..."]
        self.speaker = speaker
        self.on_close = on_close
        self.current_line_index = 0
        
        # bottom box
        margin = 10
        self.height = 60
        self.rect = pygame.Rect(
            margin, 
            settings.VIRTUAL_HEIGHT - self.height - margin, 
            settings.VIRTUAL_WIDTH - (margin * 2), 
            self.height
        )
        
        #background
        self.bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        self.bg_surface.fill((10, 10, 20, 220)) # Azul muy oscuro transparente
        
        self.font = settings.FONTS["small"]
        
        self._start_line()

    def _start_line(self):
        self.visible_chars = 0
        self.char_timer = 0.0
        self.char_speed = 10.0 if getattr(settings, 'SLOW_DIALOGUE', False) else 30.0 # Caracteres por segundo
        
        text = self.lines[self.current_line_index]
        self.total_chars = len(text)
        
        words = text.replace('\n', ' ').split(' ')
        self.wrapped_lines = []
        current_line = ""
        max_width = self.rect.width - 20
        
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                self.wrapped_lines.append(current_line)
                current_line = word + " "
        self.wrapped_lines.append(current_line)
        
        from src.systems.AudioManager import AudioManager
        gender = "boy" if self.speaker in ("Dr. Pepe", "Jezu", "Dr Pepe") else "girl"
        AudioManager.start_voice(gender)

    def update(self, dt):
        if self.visible_chars < self.total_chars:
            self.char_timer += dt
            if self.char_timer >= 1.0 / self.char_speed:
                chars_to_add = int(self.char_timer / (1.0 / self.char_speed))
                self.visible_chars += chars_to_add
                self.char_timer -= chars_to_add * (1.0 / self.char_speed)
                
                if self.visible_chars > self.total_chars:
                    self.visible_chars = self.total_chars
                if self.visible_chars >= self.total_chars:
                    from src.systems.AudioManager import AudioManager
                    AudioManager.stop_voice()

    def render(self, surface):
        # Main box
        surface.blit(self.bg_surface, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1, border_radius=3)
        
        # character name
        speaker_surf = settings.FONTS["medium"].render(self.speaker, True, (100, 200, 255))
        surface.blit(speaker_surf, (self.rect.x + 8, self.rect.y + 5))
        
        # text
        chars_left_to_draw = int(self.visible_chars)
        y_offset = self.rect.y + 25
        
        for line in self.wrapped_lines:
            if chars_left_to_draw <= 0:
                break
                
            line_to_draw = line[:chars_left_to_draw]
            text_surf = self.font.render(line_to_draw, True, (255, 255, 255))
            surface.blit(text_surf, (self.rect.x + 10, y_offset))
            
            y_offset += 15
            chars_left_to_draw -= len(line)
        
        if self.visible_chars >= self.total_chars:
            indicator = settings.FONTS["small"].render("Espacio/Enter >", True, (150, 150, 150))
            surface.blit(
                indicator, 
                (self.rect.right - indicator.get_width() - 5, self.rect.bottom - indicator.get_height() - 5)
            )

    def on_input(self, input_id, input_data):
        if input_data.pressed:
            if input_id in ("interact", "confirm"):
                if self.visible_chars < self.total_chars:
                    self.visible_chars = self.total_chars
                    from src.systems.AudioManager import AudioManager
                    AudioManager.stop_voice()
                else:
                    self.current_line_index += 1
                    if self.current_line_index >= len(self.lines):
                        self.ui_stack.pop()
                        if self.on_close:
                            self.on_close()
                    else:
                        self._start_line()

