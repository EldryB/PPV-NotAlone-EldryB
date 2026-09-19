import pygame
import random
import math
from src.entity.NPC import NPC
import settings

class Jake(NPC):
    def __init__(self, x, y):
        super().__init__(x, y, "Jake", "jake_interact")
        self.width = 48
        self.height = 48
        
        self.hitbox_offset_x = 8
        self.hitbox_offset_y = 16
        self.hitbox_w = 32
        self.hitbox_h = 32
        
        tex = pygame.image.load(settings.BASE_DIR / "assets" / "graphics" / "characters" / "jake_animation.png").convert_alpha()
        
        all_frames = []
        for row in range(10):
            for col in range(4):
                surf = pygame.Surface((48, 48), pygame.SRCALPHA)
                surf.blit(tex, (0, 0), (col * 48, row * 48, 48, 48))
                all_frames.append(surf)
                
        # Split according to user specs
        
        self.animations = {
            "idle": all_frames[0:8],
            "walk_right": all_frames[8:16],
            "walk_left": all_frames[16:24],
            "walk_up": all_frames[24:32],
            "walk_down": all_frames[32:40]
        }
        
        self.current_frame = 0
        self.animation_timer = 0.0
        self.state = "idle"
        self.facing = "right" # right, left, up, down
        
        self.speed = 30.0
        self.move_dir = pygame.math.Vector2(0, 0)
        self.decide_timer = 0.0
        self.decide_duration = random.uniform(1.0, 3.0)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height).inflate(32, 32)
        
    @rect.setter
    def rect(self, value):
        pass

    @property
    def hitbox(self):
        return pygame.Rect(
            self.x + self.hitbox_offset_x,
            self.y + self.hitbox_offset_y,
            self.hitbox_w,
            self.hitbox_h
        )
        
    @hitbox.setter
    def hitbox(self, value):
        pass
        
    def interact(self):
        if "ladrando" in settings.SOUNDS:
            settings.SOUNDS["ladrando"].play()
        
    def update(self, dt):
        self.decide_timer += dt
        if self.decide_timer >= self.decide_duration:
            self.decide_timer = 0.0
            if self.state == "idle":
                self.state = "walk"
                self.current_frame = 0
                self.decide_duration = random.uniform(2.0, 5.0)
                
                # Orthogonal movement only
                choices = [
                    (pygame.math.Vector2(1, 0), "right"),
                    (pygame.math.Vector2(-1, 0), "left"),
                    (pygame.math.Vector2(0, -1), "up"),
                    (pygame.math.Vector2(0, 1), "down")
                ]
                self.move_dir, self.facing = random.choice(choices)
            else:
                self.state = "idle"
                self.current_frame = 0
                self.decide_duration = random.uniform(1.0, 4.0)
                self.move_dir = pygame.math.Vector2(0, 0)
                
        if self.state == "walk":
            self.x += self.move_dir.x * self.speed * dt
            self.y += self.move_dir.y * self.speed * dt
            
            # Bounds checking
            if self.x < 100 or self.x > 800:
                self.move_dir.x *= -1
                self.facing = "right" if self.move_dir.x > 0 else "left"
            if self.y < 500 or self.y > 2000:
                self.move_dir.y *= -1
                self.facing = "down" if self.move_dir.y > 0 else "up"
        
        # Animation
        self.animation_timer += dt
        if self.animation_timer >= 0.1:
            self.animation_timer = 0.0
            
            anim_key = "idle" if self.state == "idle" else f"walk_{self.facing}"
            anim_list = self.animations[anim_key]
            
            self.current_frame = (self.current_frame + 1) % len(anim_list)

    def render(self, surface, camera):
        screen_pos = camera.world_to_screen((self.x, self.y))
        
        anim_key = "idle" if self.state == "idle" else f"walk_{self.facing}"
        frame = self.animations[anim_key][self.current_frame]
        
        surface.blit(frame, screen_pos)
