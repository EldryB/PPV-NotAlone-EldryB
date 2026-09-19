import pygame
import os
import json
from gale.state import BaseState
from gale.text import render_text
import settings

class PauseState(BaseState):
    def __init__(self, play_state):
        super().__init__(None)
        self.play_state = play_state
        self.ui_stack = play_state.ui_stack
        
        self.options = ["Continuar", "Guardar", "Cargar", "Salir"]
        self.selected = 0
        
        self.phase = "MAIN" # MAIN, SAVE_SLOTS
        
        self.save_options = ["Slot 1", "Slot 2", "Slot 3", "Volver"]
        self.save_selected = 0
        
        self.save_messages = ["", "", ""]
        self.refresh_save_messages()

    def refresh_save_messages(self):
        import src.systems.SaveSystem as ss
        for i in range(1, 4):
            info = ss.get_save_info(i)
            if info:
                self.save_messages[i-1] = f"{info.get('map_name', 'Unknown')} - Cordura: {int(info.get('sanity', 0))}"
            else:
                self.save_messages[i-1] = "Vacio"

    def update(self, dt):
        pass

    def render(self, surface):
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        cx = settings.VIRTUAL_WIDTH // 2
        cy = settings.VIRTUAL_HEIGHT // 2
        
        render_text(surface, "PAUSA", settings.FONTS["large"], cx, 40, (255, 255, 255), center=True)
        
        if self.phase == "MAIN":
            for i, opt in enumerate(self.options):
                color = (255, 255, 100) if i == self.selected else (200, 200, 200)
                render_text(surface, opt, settings.FONTS["medium"], cx, cy - 40 + i * 40, color, center=True)
                
                if i == self.selected:
                    render_text(surface, ">", settings.FONTS["medium"], cx - 80, cy - 40 + i * 40, color, center=True)
                    render_text(surface, "<", settings.FONTS["medium"], cx + 80, cy - 40 + i * 40, color, center=True)
                    
        elif self.phase in ("SAVE_SLOTS", "LOAD_SLOTS"):
            title_text = "Selecciona un espacio para guardar:" if self.phase == "SAVE_SLOTS" else "Selecciona una partida para cargar:"
            render_text(surface, title_text, settings.FONTS["small"], cx, cy - 80, (200, 200, 200), center=True)
            for i, opt in enumerate(self.save_options):
                color = (255, 255, 100) if i == self.save_selected else (200, 200, 200)
                
                text = opt
                if i < 3:
                    text += f" ({self.save_messages[i]})"
                    
                render_text(surface, text, settings.FONTS["medium"], cx, cy - 40 + i * 40, color, center=True)
                
                if i == self.save_selected:
                    render_text(surface, ">", settings.FONTS["medium"], cx - 140, cy - 40 + i * 40, color, center=True)

    def on_input(self, input_id, input_data):
        if input_data.pressed:
            if input_id == "move_up":
                if self.phase == "MAIN":
                    self.selected = (self.selected - 1) % len(self.options)
                else:
                    self.save_selected = (self.save_selected - 1) % len(self.save_options)
            elif input_id == "move_down":
                if self.phase == "MAIN":
                    self.selected = (self.selected + 1) % len(self.options)
                else:
                    self.save_selected = (self.save_selected + 1) % len(self.save_options)
            elif input_id in ("confirm", "interact"):
                if self.phase == "MAIN":
                    if self.selected == 0: # Continuar
                        self.ui_stack.pop()
                    elif self.selected == 1: # Guardar
                        self.phase = "SAVE_SLOTS"
                        self.save_selected = 0
                    elif self.selected == 2: # Cargar
                        self.phase = "LOAD_SLOTS"
                        self.save_selected = 0
                    elif self.selected == 3: # Salir al menu
                        self.ui_stack.clear()
                        self.play_state.state_machine.change("title")
                elif self.phase == "LOAD_SLOTS":
                    if self.save_selected == 3: # Volver
                        self.phase = "MAIN"
                        self.selected = 2
                    else:
                        import src.systems.SaveSystem as ss
                        info = ss.get_save_info(self.save_selected + 1)
                        if info:
                            self.play_state.state_machine.change("play", fade_in=True, load_slot=self.save_selected + 1)
                elif self.phase == "SAVE_SLOTS":
                    if self.save_selected == 3: # Volver
                        self.phase = "MAIN"
                        self.selected = 1
                    else:
                        import src.systems.SaveSystem as ss
                        ss.save_game(self.save_selected + 1, self.play_state)
                        self.refresh_save_messages()
            elif input_id in ("cancel", "pause"):
                if self.phase == "MAIN":
                    self.ui_stack.pop()
                else:
                    self.phase = "MAIN"
