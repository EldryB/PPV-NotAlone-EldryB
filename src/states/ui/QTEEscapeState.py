import pygame
import random
import settings
from gale.state import BaseState
from gale.text import render_text

class QTEEscapeState(BaseState):
    def __init__(self, world, ui_stack, on_complete, on_fail):
        super().__init__(None)
        self.world = world
        self.ui_stack = ui_stack
        self.on_complete = on_complete
        self.on_fail = on_fail
        
        # 0.8 sec per arrow reaction time
        self.key_time_limit = 0.8
        self.key_timer = self.key_time_limit
        
        # Physics / Acceleration
        self.current_speed = 0.0
        self.max_speed = 220.0
        self.burst_speed = 42.3
        self.friction = 80.0
        
        self.target_x = 1440.0
        self.target_y = 960.0
        
        # Initial position
        self.world.player.x = 48.0
        self.world.player.y = 912.0
        self.world.player.hitbox.center = (self.world.player.x, self.world.player.y)
        if hasattr(self.world.player, '_change_direction'):
            self.world.player._change_direction("right")
            
        self.directions = ["move_up", "move_down", "move_left", "move_right"]
        self.dir_symbols = {"move_up": "ARRIBA", "move_down": "ABAJO", "move_left": "IZQUIERDA", "move_right": "DERECHA"}
        self.current_target = random.choice(self.directions)
        
        self.status = "INTRO"
        self.fall_anim_timer = 0.0
        self.fall_recovery_presses = 0
        self.fails = 0
        self.max_fails = 15
        
        self.world.player.input_locked = True
        
        self.zoom_factor = 1.8
        self.zoom_w = int(settings.VIRTUAL_WIDTH / self.zoom_factor)
        self.zoom_h = int(settings.VIRTUAL_HEIGHT / self.zoom_factor)
        self.zoom_surf = pygame.Surface((self.zoom_w, self.zoom_h))
        
        from gale.camera import Camera
        self.custom_camera = Camera(self.zoom_w, self.zoom_h)
        self.custom_camera.bounds = self.world.camera.bounds

        # Generate vignette
        small_v = pygame.Surface((64, 36), pygame.SRCALPHA)
        for y in range(36):
            for x in range(64):
                dx = x - 32
                dy = y - 18
                dist = (dx*dx + dy*dy)**0.5
                alpha = int(min(255, max(0, ((dist / 36.7) ** 1.3) * 255)))
                small_v.set_at((x, y), (0, 0, 0, alpha))
        self.vignette = pygame.transform.smoothscale(small_v, (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))

    def update(self, dt):
        if self.status == "INTRO":
            return
            
        if self.status == "RUNNING":
            # Reaction timer
            self.key_timer -= dt
            if self.key_timer <= 0:
                self.trigger_fall()
                
            # Physics
            if self.current_speed > 0:
                self.current_speed = max(0, self.current_speed - self.friction * dt)
                
                # Apply movement
                if self.world.player.x < 1440.0:
                    self.world.player.x += self.current_speed * dt
                    if hasattr(self.world.player, '_change_direction'):
                        self.world.player._change_direction("right")
                    if self.world.player.x > 1440.0:
                        self.world.player.x = 1440.0
                elif self.world.player.y < 960.0:
                    self.world.player.y += self.current_speed * dt
                    if hasattr(self.world.player, '_change_direction'):
                        self.world.player._change_direction("down")
                    if self.world.player.y >= 960.0:
                        self.world.player.y = 960.0
                        self.win()
                        
        elif self.status == "FALLING":
            self.current_speed = 0.0
            self.fall_anim_timer += dt
            idx = int(self.fall_anim_timer / 0.08)
            if idx > 8:
                self.status = "FALLEN"
                self.world.player.fall_frame_index = 8
            else:
                self.world.player.fall_frame_index = idx
                
        elif self.status == "FALLEN":
            self.current_speed = 0.0
            
        # Manually update player so animations advance
        self.world.player.update(dt)
        
        self.custom_camera.follow(self.world.player, rate=10.0)
        self.custom_camera.update(dt)

    def trigger_fall(self):
        self.fails += 1
        if self.fails >= self.max_fails:
            # Restart
            if hasattr(self.ui_stack.states[0], 'sanity_system') and self.ui_stack.states[0].sanity_system:
                self.ui_stack.states[0].sanity_system.drain(25.0)
            self.reset_qte()
            return
            
        self.status = "FALLING"
        self.fall_anim_timer = 0.0
        self.fall_recovery_presses = 0
        self.world.player.is_fallen = True
        self.world.player.fall_frame_index = 0
        self.current_speed = 0.0
        
    def reset_qte(self):
        self.world.player.x = 48.0
        self.world.player.y = 912.0
        self.world.player.hitbox.center = (self.world.player.x, self.world.player.y)
        self.world.player.is_fallen = False
        self.fails = 0
        self.current_speed = 0.0
        self.status = "INTRO"

    def win(self):
        def after_dialogue():
            self.ui_stack.pop()
            self.world.player.input_locked = False
            self.world.player.is_fallen = False
            self.world.player.state = "idle"
            if self.on_complete: self.on_complete()
            
        from src.states.ui.DialogueState import DialogueState
        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=["(+1 pildora en el inventario)"],
            speaker="",
            on_close=after_dialogue
        ))

    def render(self, surface):
        self.zoom_surf.fill((0,0,0))
        original_camera = self.world.camera
        self.world.camera = self.custom_camera
        
        self.world.render(self.zoom_surf)
        self.world.camera = original_camera
        
        scale_w = settings.VIRTUAL_WIDTH + 12
        scale_h = settings.VIRTUAL_HEIGHT + 12
        scaled = pygame.transform.scale(self.zoom_surf, (scale_w, scale_h))
        
        shake_x = -6
        shake_y = -6
        if self.status in ("FALLING", "FALLEN"):
            shake_x += random.randint(-4, 4)
            shake_y += random.randint(-4, 4)
            
        surface.blit(scaled, (shake_x, shake_y))
        
        # Apply vignette over the world
        surface.blit(self.vignette, (0, 0))
        
        if self.status == "INTRO":
            overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))
            
            cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
            pygame.draw.rect(surface, (30, 30, 30), (cx - 150, cy - 80, 300, 160))
            pygame.draw.rect(surface, (150, 150, 150), (cx - 150, cy - 80, 300, 160), 2)
            
            render_text(surface, "Reto: Escape Mortal", settings.FONTS["medium"], cx, cy - 65, (255, 100, 100), center=True)
            render_text(surface, "Oprime la flecha correcta antes de 0.8s.", settings.FONTS["small"], cx, cy - 40, (255, 255, 255), center=True)
            render_text(surface, "Si fallas, tropiezas y sumas un error.", settings.FONTS["small"], cx, cy - 20, (200, 200, 200), center=True)
            render_text(surface, "Pulsa ESPACIO para levantarte y seguir.", settings.FONTS["small"], cx, cy, (200, 200, 200), center=True)
            render_text(surface, "Con 15 errores pierdes 25% de cordura", settings.FONTS["small"], cx, cy + 20, (255, 100, 100), center=True)
            render_text(surface, "y el reto se reinicia.", settings.FONTS["small"], cx, cy + 35, (255, 100, 100), center=True)
            render_text(surface, "Presiona ENTER para iniciar", settings.FONTS["small"], cx, cy + 60, (255, 255, 100), center=True)
            return

        if self.status in ("FALLING", "FALLEN"):
            overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((200, 0, 0, 100))
            surface.blit(overlay, (0,0))
            
            if self.status == "FALLEN":
                text = settings.FONTS["medium"].render("¡PRESIONA ESPACIO RAPIDO PARA LEVANTARTE!", True, (255, 255, 255))
                surface.blit(text, (settings.VIRTUAL_WIDTH // 2 - text.get_width() // 2, settings.VIRTUAL_HEIGHT // 2 - 30))
                
                pygame.draw.rect(surface, (100, 100, 100), (settings.VIRTUAL_WIDTH//2 - 50, settings.VIRTUAL_HEIGHT//2, 100, 10))
                fill_w = int((self.fall_recovery_presses / 15.0) * 100)
                pygame.draw.rect(surface, (0, 255, 0), (settings.VIRTUAL_WIDTH//2 - 50, settings.VIRTUAL_HEIGHT//2, fill_w, 10))
                
        elif self.status == "RUNNING":
            x = settings.VIRTUAL_WIDTH // 2
            y = 45
            s = 15
            if self.current_target == "move_up":
                pts = [(x, y-s), (x-s, y), (x-s//2, y), (x-s//2, y+s), (x+s//2, y+s), (x+s//2, y), (x+s, y)]
            elif self.current_target == "move_down":
                pts = [(x, y+s), (x-s, y), (x-s//2, y), (x-s//2, y-s), (x+s//2, y-s), (x+s//2, y), (x+s, y)]
            elif self.current_target == "move_left":
                pts = [(x-s, y), (x, y-s), (x, y-s//2), (x+s, y-s//2), (x+s, y+s//2), (x, y+s//2), (x, y+s)]
            else: # right
                pts = [(x+s, y), (x, y-s), (x, y-s//2), (x-s, y-s//2), (x-s, y+s//2), (x, y+s//2), (x, y+s)]
                
            pygame.draw.polygon(surface, (255, 255, 0), pts)
            pygame.draw.polygon(surface, (0, 0, 0), pts, 2) # outline
            
            time_ratio = max(0, self.key_timer / self.key_time_limit)
            pygame.draw.rect(surface, (255, 0, 0), (settings.VIRTUAL_WIDTH//2 - 50, 70, 100, 5))
            pygame.draw.rect(surface, (0, 255, 0), (settings.VIRTUAL_WIDTH//2 - 50, 70, int(100 * time_ratio), 5))
            
        dist_total = (1440.0 - 48.0) + (960.0 - 912.0)
        dist_current = (self.world.player.x - 48.0) + (self.world.player.y - 912.0)
        prog_text = settings.FONTS["small"].render(f"Progreso: {int(dist_current/dist_total*100)}%", True, (255, 255, 255))
        surface.blit(prog_text, (10, 10))
        err_text = settings.FONTS["small"].render(f"Errores: {self.fails}/{self.max_fails}", True, (255, 100, 100))
        surface.blit(err_text, (10, 73))

    def on_input(self, input_id, input_data):
        if not input_data.pressed:
            return True
            
        if self.status == "INTRO":
            if input_id in ("confirm", "space"):
                self.status = "RUNNING"
                self.key_timer = self.key_time_limit
            return True
            
        if self.status == "FALLEN":
            if input_id in ("confirm", "interact", "space"):
                self.fall_recovery_presses += 1
                self.world.player.fall_frame_index = 8 + self.fall_recovery_presses
                
                if self.fall_recovery_presses >= 15:
                    self.status = "RUNNING"
                    self.world.player.is_fallen = False
                    self.key_timer = self.key_time_limit
                    self.current_target = random.choice(self.directions)
            return True
            
        if self.status == "RUNNING":
            if input_id in self.directions:
                if input_id == self.current_target:
                    # Accelerate
                    self.current_speed = min(self.max_speed, self.current_speed + self.burst_speed)
                    self.key_timer = self.key_time_limit
                    self.current_target = random.choice(self.directions)
                else:
                    self.trigger_fall()
                    
        return True
