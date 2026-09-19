
import pygame
from pygame.math import Vector2
from gale.animation import Animation
from gale.timer import Timer
import settings

class Player:
    #sprite-sheet
    DIR_TO_ROW = {
        "right":      1,
        "left":       0,
        "up":         2,
        "down":       3,
        "up_left":    5,
        "up_right":   4,
        "down_left":  7,
        "down_right": 6,
    }

    def __init__(self, x, y, world=None):
        self.world = world
        self.width = 48
        self.height = 48

        self.x = float(x)
        self.y = float(y)

        #hitbox logic
        self.hitbox_w = 24 
        self.hitbox_h = 14  
        self.hitbox_offset_x = 12 
        self.hitbox_offset_y = 34 

        #Physics
        self.velocity = Vector2(0, 0)
        self.accel    = 800.0    
        self.friction = 1400.0  
        self.max_speed = 400.0   

        # Movement states
        self.direction = "down"
        self.state = "standing"  # "moving", "standing", "idle"
        self.time_standing = 0.0
        self.idle_trigger_time = 1.0

        self.timer = Timer()
        self.animations = self._build_animations()
        self.current_anim = self.animations[f"standing_{self.direction}"]

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    @property
    def hitbox(self):
        return pygame.Rect(
            round(self.x) + self.hitbox_offset_x,
            round(self.y) + self.hitbox_offset_y,
            self.hitbox_w,
            self.hitbox_h,
        )

    @property
    def position(self):
        return Vector2(self.x + self.width / 2, self.y + self.height / 2)

    def _build_animations(self):
        anims = {}
        for direction, row in self.DIR_TO_ROW.items():
            start = row * 4          # primer frame de esa fila
            walk_quads = settings.FRAMES["andrea_walking"][start : start + 4]
            idle_quads = settings.FRAMES["andrea_idle"][start : start + 4]

            # walk
            anims[f"moving_{direction}"] = Animation(walk_quads, time_interval=0.15)
            # Animation idle
            anims[f"idle_{direction}"]   = Animation(idle_quads, time_interval=0.25)
            # Standing
            anims[f"standing_{direction}"] = Animation([idle_quads[0]], time_interval=1.0)

        return anims

    def _change_state(self, state):
        if self.state != state:
            self.state = state
            self.current_anim = self.animations[f"{self.state}_{self.direction}"]
            self.current_anim.reset()

    def _change_direction(self, direction):
        if self.direction != direction:
            self.direction = direction
            self.current_anim = self.animations[f"{self.state}_{self.direction}"]

 

    def update(self, dt):
        self.timer.update(dt)
        
        if getattr(self, 'input_locked', False):
            prev_x, prev_y = getattr(self, '_prev_pos_x', self.x), getattr(self, '_prev_pos_y', self.y)
            if self.x != prev_x or self.y != prev_y:
                self._change_state("moving")
            else:
                self._change_state("standing")
            
            self._prev_pos_x = self.x
            self._prev_pos_y = self.y
            
            self.current_anim.update(dt)
            # hitbox follow character
            self.hitbox.x = round(self.x) + self.hitbox_offset_x
            self.hitbox.y = round(self.y) + self.hitbox_offset_y
            self.rect.x = round(self.x)
            self.rect.y = round(self.y)
            return

        self._handle_movement(dt)
        self._prev_pos_x = self.x
        self._prev_pos_y = self.y
        self.current_anim.update(dt)

    def _handle_movement(self, dt):
        keys = pygame.key.get_pressed()

        mx = 0
        my = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  mx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: mx =  1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    my = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  my =  1

        moving = (mx != 0 or my != 0)

        if moving:
            #looking direction
            if   mx >  0 and my >  0: self._change_direction("down_right")
            elif mx <  0 and my >  0: self._change_direction("down_left")
            elif mx >  0 and my <  0: self._change_direction("up_right")
            elif mx <  0 and my <  0: self._change_direction("up_left")
            elif mx >  0:             self._change_direction("right")
            elif mx <  0:             self._change_direction("left")
            elif my >  0:             self._change_direction("down")
            elif my <  0:             self._change_direction("up")

            # Aceleration
            input_vec = Vector2(mx, my)
            if input_vec.length() > 0:
                input_vec = input_vec.normalize()
            self.velocity += input_vec * self.accel * dt

            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)

            self._change_state("moving")
            self.time_standing = 0.0

            ratio = self.velocity.length() / self.max_speed
            self.current_anim.time_interval = max(0.06, 0.20 - 0.10 * ratio)

        else:
            # deceleration
            speed = self.velocity.length()
            if speed > 0:
                new_speed = max(0.0, speed - self.friction * dt)
                self.velocity.scale_to_length(new_speed) if new_speed > 0 else self.velocity.update(0, 0)

            # almost standing
            if self.velocity.length() < 4.0:
                self.velocity.update(0, 0)
                if self.state == "moving":
                    self._change_state("standing")
                    self.time_standing = 0.0

                if self.state == "standing":
                    self.time_standing += dt
                    if self.time_standing >= self.idle_trigger_time:
                        self._change_state("idle")

        #Integrate position wiht collisions
        if self.velocity.length() > 0:
            self._move_and_collide(self.velocity.x * dt, self.velocity.y * dt)

    def _move_and_collide(self, dx, dy):
        collision_rects = list(getattr(self.world, 'collision_rects', []))
        if hasattr(self.world, 'npcs'):
            for npc in self.world.npcs:
                collision_rects.append(getattr(npc, 'hitbox', npc.rect))

        self.x += dx
        hb = self.hitbox
        for rect in collision_rects:
            if hb.colliderect(rect):
                if dx > 0:
                    hb.right = rect.left
                else:
                    hb.left = rect.right
                self.x = hb.x - self.hitbox_offset_x
                self.velocity.x = 0

        self.y += dy
        hb = self.hitbox
        for rect in collision_rects:
            if hb.colliderect(rect):
                if dy > 0:  #collide bottom, stop
                    hb.bottom = rect.top
                else:       # collide top, visual efect
                    hb.top = rect.bottom
                self.y = hb.y - self.hitbox_offset_y
                self.velocity.y = 0
                
        # Screen / Map limits
        bounds_rect = getattr(self.world.camera, 'bounds', None)
        max_w = bounds_rect.width if bounds_rect else settings.VIRTUAL_WIDTH
        max_h = bounds_rect.height if bounds_rect else settings.VIRTUAL_HEIGHT
        
        if hb.left < 0:
            hb.left = 0
            self.x = hb.x - self.hitbox_offset_x
        elif hb.right > max_w:
            hb.right = max_w
            self.x = hb.x - self.hitbox_offset_x
            
        if hb.top < 0:
            hb.top = 0
            self.y = hb.y - self.hitbox_offset_y
        elif hb.bottom > max_h:
            hb.bottom = max_h
            self.y = hb.y - self.hitbox_offset_y

    def render(self, surface, camera):
        #Target caemra
        dest = camera.apply(self.rect)

        if getattr(self, 'is_fallen', False):
            texture = settings.TEXTURES.get("fall_andrea")
            if texture and "fall_andrea" in settings.FRAMES:
                frames = settings.FRAMES["fall_andrea"]
                frame_idx = getattr(self, 'fall_frame_index', 0)
                if frame_idx < len(frames):
                    frame_quad = frames[frame_idx]
                    surface.blit(texture, dest, frame_quad)
                else:
                    surface.blit(texture, dest, frames[-1])
            else:
                tex_key = "andrea_walking" if self.state == "moving" else "andrea_idle"
                texture  = settings.TEXTURES[tex_key]
                frame_quad = self.current_anim.get_current_frame()
                img = texture.subsurface(frame_quad).copy()
                img = pygame.transform.rotate(img, -90)
                fall_dest = dest.move(0, 10)
                surface.blit(img, fall_dest)
        else:
            tex_key = "andrea_walking" if self.state == "moving" else "andrea_idle"
            texture  = settings.TEXTURES[tex_key]
            frame_quad = self.current_anim.get_current_frame()
            surface.blit(texture, dest, frame_quad)

    def on_input(self, input_id, input_data):
        pass
