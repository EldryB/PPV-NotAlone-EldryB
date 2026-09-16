import pygame
from gale.state import BaseState
from gale.ui.window import Window
from gale.ui.label import Label
from gale.ui.button import Button
from gale.ui.manager import UIManager

class InventoryState(BaseState):
    def __init__(self, inventory, ui_stack):
        self.inventory = inventory
        self.stack = ui_stack
        
        self.ui_manager = UIManager()
        
        self.window = Window(
            x=60, 
            y=40, 
            width=200, 
            height=100,
            title="Inventory"
        )
        
        pills_count = getattr(self.inventory, 'pills', 0) if self.inventory else 0
        
        self.pills_label = Label(
            f"Pills: {pills_count}",
            x=20,
            y=30
        )
        self.window.add(self.pills_label)
        
        self.close_button = Button(
            "Close",
            x=130,
            y=70,
            width=60,
            height=20,
            on_click=self.close
        )
        self.window.add(self.close_button)
        
        self.ui_manager.add(self.window)

    def close(self):
        self.stack.pop()

    def update(self, dt):
        self.ui_manager.update(dt)

    def render(self, surface):
        # Draw a semi-transparent dark background
        bg = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        surface.blit(bg, (0, 0))
        
        self.ui_manager.render(surface)

    def on_input(self, input_id, input_data):
        self.ui_manager.on_input(input_id, input_data)
        
        if input_data.pressed and input_id in ("inventory", "escape"):
            self.close()
