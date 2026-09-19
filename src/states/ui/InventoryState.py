import pygame
from gale.state import BaseState
from gale.text import render_text
import settings

class InventoryState(BaseState):
    def __init__(self, inventory, ui_stack, on_item_click=None):
        super().__init__(None)
        self.inventory = inventory
        self.stack = ui_stack
        self.on_item_click = on_item_click
        self.mouse_was_pressed = True # Prevent immediate click if holding mouse
        
        self.item_names = {
            "inv_llaves": "Llaves",
            "inv_pills": "Pildoras",
            "inv_craneo": "Craneo",
            "inv_coat": "Bata del Dr.",
            "inv_phone": "Telefono Movil"
        }

    def close(self):
        self.stack.pop()

    def update(self, dt):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed and not self.mouse_was_pressed:
            mx, my = pygame.mouse.get_pos()
            scale_x = settings.WINDOW_WIDTH / settings.VIRTUAL_WIDTH
            scale_y = settings.WINDOW_HEIGHT / settings.VIRTUAL_HEIGHT
            vmx = mx / scale_x
            vmy = my / scale_y
            
            cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
            panel_x = cx - 220
            panel_y = cy - 150
            start_x = panel_x + 40
            start_y = panel_y + 100
            
            for i, item_key in enumerate(self.inventory.items):
                row = i // 4
                col = i % 4
                x = start_x + col * 92
                y = start_y + row * 92
                
                if x <= vmx <= x + 72 and y <= vmy <= y + 72:
                    if self.on_item_click:
                        self.on_item_click(item_key)
                    break
        self.mouse_was_pressed = mouse_pressed

    def render(self, surface):
        # Draw a semi-transparent dark background
        bg = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        surface.blit(bg, (0, 0))
        
        # Draw panel
        cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
        panel_w = 440
        panel_h = 300
        panel_x = cx - panel_w // 2
        panel_y = cy - panel_h // 2
        
        pygame.draw.rect(surface, (30, 30, 40), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(surface, (150, 150, 200), (panel_x, panel_y, panel_w, panel_h), 2)
        
        # Title
        render_text(surface, "INVENTARIO", settings.FONTS["medium"], cx, panel_y + 20, (255, 255, 255), center=True)
        
        # Grid settings
        cols = 4
        slot_size = 72
        padding_x = 20
        padding_y = 20
        start_x = panel_x + 40
        start_y = panel_y + 100
        
        # Mouse Hover mapping
        mx, my = pygame.mouse.get_pos()
        scale_x = settings.WINDOW_WIDTH / settings.VIRTUAL_WIDTH
        scale_y = settings.WINDOW_HEIGHT / settings.VIRTUAL_HEIGHT
        vmx = mx / scale_x
        vmy = my / scale_y
        
        hovered_item_name = ""
        
        for i, item_key in enumerate(self.inventory.items):
            row = i // cols
            col = i % cols
            
            x = start_x + col * (slot_size + padding_x)
            y = start_y + row * (slot_size + padding_y)
            
            # Check hover
            if x <= vmx <= x + slot_size and y <= vmy <= y + slot_size:
                pygame.draw.rect(surface, (80, 80, 100), (x, y, slot_size, slot_size))
                hovered_item_name = self.item_names.get(item_key, item_key)
            else:
                pygame.draw.rect(surface, (50, 50, 60), (x, y, slot_size, slot_size))
                
            pygame.draw.rect(surface, (100, 100, 120), (x, y, slot_size, slot_size), 1)
            
            tex = settings.TEXTURES.get(item_key)
            if tex:
                tw, th = tex.get_size()
                surface.blit(tex, (x + (slot_size - tw)//2, y + (slot_size - th)//2))
                
            # If pills, draw count
            if item_key == "inv_pills":
                render_text(surface, f"x{self.inventory.pills}", settings.FONTS["medium"], x + slot_size - 15, y + slot_size - 15, (100, 255, 100), center=True)

        if hovered_item_name:
            render_text(surface, hovered_item_name, settings.FONTS["small"], cx, panel_y + 60, (255, 255, 100), center=True)
            
        render_text(surface, "[I] o [ESC] Cerrar", settings.FONTS["small"], cx, panel_y + panel_h - 20, (150, 150, 150), center=True)

    def on_input(self, input_id, input_data):
        if input_data.pressed and input_id in ("inventory", "cancel"):
            self.close()

