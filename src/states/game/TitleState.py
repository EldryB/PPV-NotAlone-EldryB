import pygame
from gale.state import BaseState
from gale.text import render_text
from gale.input_handler import InputData
from gale.ui.manager import UIManager
from gale.ui.container import Container
from gale.ui.list_view import ListView
from gale.ui.theme import Theme
import settings

class CustomListView(ListView):
    def render(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.items:
            return

        bg = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg.fill(self.theme.background_color)
        surface.blit(bg, (self.x, self.y))

        font = self._font if self._font is not None else self.theme.font

        for index, (label, _) in enumerate(self.items):
            row_rect = self.row_rect(index)
            
            if index == self.selected_index:
                current_color = self.theme.focus_color
            else:
                current_color = self.theme.text_color

            from gale.text import Text
            text_obj = Text(
                label,
                font,
                row_rect.centerx,
                row_rect.centery,
                current_color,
                center=True,
            )
            text_obj.render(surface)

            if index == self.selected_index and self.cursor is not None:
                self.cursor.render(surface, (row_rect.x - 4, row_rect.centery))

class TitleState(BaseState):
    def enter(self, **kwargs) -> None:
        self.is_transitioning = False
        self.fade_alpha = 0.0
        
        def start_game():
            if not self.is_transitioning:
                self.is_transitioning = True
                from gale.timer import Timer
                Timer.tween(1.0, [(self, {'fade_alpha': 255.0})], on_finish=lambda: self.state_machine.change("intro"))
                
        def show_load_menu():
            import src.systems.SaveSystem as ss
            load_items = []
            for i in range(1, 4):
                info = ss.get_save_info(i)
                text = f"Slot {i}"
                if info:
                    text += f" ({info.get('map_name', 'Unknown')})"
                else:
                    text += " (Vacio)"
                
                def make_loader(slot):
                    def do_load():
                        if not self.is_transitioning:
                            info = ss.get_save_info(slot)
                            if info:
                                self.is_transitioning = True
                                from gale.timer import Timer
                                # Load directly into PlayState
                                def fade_to_play():
                                    self.state_machine.change("play", load_slot=slot, fade_in=True)
                                Timer.tween(1.0, [(self, {'fade_alpha': 255.0})], on_finish=fade_to_play)
                    return do_load
                
                load_items.append((text, make_loader(i)))
                
            def back_to_main():
                self.list_view.items = main_items
                self.list_view.selected_index = 0
            
            load_items.append(("Volver", back_to_main))
            self.list_view.items = load_items
            self.list_view.selected_index = 0
            
        def quit_game():
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            
        self.bg_img = settings.TEXTURES.get("title_img")
        if self.bg_img:
            self.bg_img = pygame.transform.scale(self.bg_img, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))

        menu_theme = Theme(
            font=settings.FONTS["medium"],
            text_color=pygame.Color(200, 200, 200),            # Texto normal
            focus_color=pygame.Color(255, 210, 50),
            background_color=pygame.Color(10, 10, 15, 180)     # Fondo negro semitransparente
        )

        menu_x = 24 * 16
        menu_y = 10 * 16
        
        main_items = [("Empezar Juego", start_game), ("Cargar", show_load_menu), ("Salir", quit_game)]
        self.list_view = CustomListView(
            menu_x,
            menu_y,
            300, 100,
            items=main_items,
            theme=menu_theme
        )
        menu = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT, children=[self.list_view])

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
        if self.bg_img:
            surface.blit(self.bg_img, (0, 0))
        else:
            surface.fill((10, 10, 15))
            
        self.ui.render(surface)
        
        if self.fade_alpha > 0:
            dark = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, int(max(0, min(255, self.fade_alpha)))))
            surface.blit(dark, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.ui.on_input(input_id, input_data)
