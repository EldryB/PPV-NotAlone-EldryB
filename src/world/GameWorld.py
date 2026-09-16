"""
Not Alone — Mundo del Juego
"""
import pygame
from pathlib import Path
from gale.tilemap import load_tiled_map
from gale.camera import Camera

from src.entity.Player import Player
from src.world.Interactable import MapTransition, Interactable
from src.entity.DrPepe import DrPepe
from src.entity.Jezu import Jezu
from src.entity.Decoration import Decoration
from src.entity.Building import Building
from gale.timer import Timer
import settings
from src.states.ui.SimonSaysState import SimonSaysState


class GameWorld:
    def __init__(self, map_name, on_map_change=None, on_puzzle_trigger=None):
        self.on_map_change = on_map_change
        self.on_puzzle_trigger = on_puzzle_trigger
        self.tilemap = None
        self.player = None
        self.npcs = []
        self.interactables = []
        self.transitions = []
        self.decorations = []
        self.buildings = []
        self.collision_rects = []
        
        
        self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)

        self.load_map(map_name)


    def load_map(self, map_name, spawn_point=(200, 200)):
        self.map_name = map_name
        self.npcs.clear()
        self.interactables.clear()
        self.transitions.clear()
        self.decorations.clear()
        self.buildings.clear()
        self.collision_rects = []
        self.internal_doors = []
        self.rooms = {}
        self.room_alphas = {}
        self.active_room = None
        self.active_interactable = None

        #Load map
        map_path = Path(f"assets/maps/{map_name}.json")
        try:
            self.tilemap = load_tiled_map(str(map_path))
            print(f"[GameWorld] Mapa '{map_name}' cargado.")
        except Exception as e:
            print(f"[GameWorld] No se pudo cargar '{map_name}': {e}")
            self.tilemap = None

        #Parse tiled objects
        if self.tilemap and hasattr(self.tilemap, 'object_layers'):
            for layer_name, obj_layer in self.tilemap.object_layers.items():
                is_collision_layer = layer_name.lower() in ["collisions", "colisiones", "collision"]
                is_doors_layer = "door" in layer_name.lower()
                is_rooms_layer = "room" in layer_name.lower()
                
                for obj in obj_layer:
                    #Collisions
                    if is_collision_layer or (obj.name and obj.name.lower() == "collision"):
                        self.collision_rects.append(
                            pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        )
                    
                    #Rooms
                    if is_rooms_layer or (obj.name and "room" in obj.name.lower()):
                        if hasattr(obj, 'properties') and 'room_index' in obj.properties:
                            idx = int(obj.properties['room_index'])
                            self.rooms[idx] = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            self.room_alphas[idx] = 0.0 # Oscuridad total por defecto

                    # doors
                    if is_doors_layer or (obj.name and "door" in obj.name.lower()):
                        dest_map = None
                        if hasattr(obj, 'properties') and 'object_tag' in obj.properties:
                            tag = obj.properties['object_tag']
                            if tag == "amphitheater": dest_map = "amphitheater_map"
                            elif tag == "anatomy_building": dest_map = "anatomy_map"
                            elif tag == "embriology_building": dest_map = "embriology_map"
                            elif tag == "dr_office": dest_map = "dr_map"
                            else: dest_map = f"{tag}_map"
                        
                        if dest_map:
                            #transition map
                            self.interactables.append(Interactable(
                                obj.x, obj.y, obj.width, obj.height,
                                on_interact=lambda m=dest_map: self._trigger_transition(m, (3 * 16, 14 * 16))
                            ))
                        else:
                            #Transition room
                            self.internal_doors.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                            
                    # Locker puzzle
                    is_locker_layer = "locker" in layer_name.lower()
                    if is_locker_layer or (obj.name and "locker" in obj.name.lower()):
                        # Almacenamos su callback para lanzar el puzle
                        def launch_simon_says():

                            # We assume that PlayState is active and pass its ui_stack
                            # Since GameWorld has no direct reference to the ui_stack, use a callback
                            if hasattr(self, 'on_puzzle_trigger'):
                                self.on_puzzle_trigger("simon_says")
                                
                        self.interactables.append(Interactable(
                            obj.x, obj.y, obj.width, obj.height,
                            on_interact=launch_simon_says
                        ))
                        
            print(f"[GameWorld] {len(self.collision_rects)} rects de colisión cargados.")
            print(f"[GameWorld] {len(self.rooms)} habitaciones cargadas.")

        #Create player
        if not self.player:
            self.player = Player(spawn_point[0], spawn_point[1], self)
        else:
            self.player.x = float(spawn_point[0])
            self.player.y = float(spawn_point[1])
            self.player.velocity.update(0, 0)

        # check current room
        if self.rooms:
            for idx, r in self.rooms.items():
                if r.collidepoint(self.player.x, self.player.y):
                    self.active_room = idx
                    self.room_alphas[idx] = 255.0
                    break
            # if it dont spawn within an exact rectangle, light up room 1
            if self.active_room is None:
                self.active_room = list(self.rooms.keys())[0] if self.rooms else None
                if self.active_room is not None:
                    self.room_alphas[self.active_room] = 255.0

        # Config camera
        self.camera.follow(self.player, rate=6.0)
        if self.tilemap:
            map_w = self.tilemap.cols * self.tilemap.tile_width
            map_h = self.tilemap.rows * self.tilemap.tile_height
            self.camera.bounds = pygame.Rect(0, 0, map_w, map_h)

        self._setup_entities(map_name)

    def _setup_entities(self, map_name):
        if map_name == "main_map":
            # interactive buildings
            self.buildings.append(Building(
                14 * 16, 
                10 * 16, 
                settings.TEXTURES["edificio1"], 
                "Edificio de Anatomía", 
                self.player
            ))
            self.buildings.append(Building(
                63 * 16, 
                77 * 16, 
                settings.TEXTURES["edificio3"], 
                "Edificio de Embriología", 
                self.player
            ))
            self.buildings.append(Building(
                20 * 16, 
                39 * 16, 
                settings.TEXTURES["edificio5"], 
                "Anfiteatro de Anatomía", 
                self.player
            ))
            self.buildings.append(Building(
                1 * 16,
                46 * 16,
                settings.TEXTURES["edificio6"],
                "Oficina del Dr. Pepe",
                self.player
            ))
            
            # No interactive Buildings
            self.decorations.append(Decoration(32 * 16, 7 * 16, settings.TEXTURES["edificio2"]))
            self.decorations.append(Decoration(3 * 16, 9 * 16, settings.TEXTURES["edificio4"]))
            
            #Decorations
            self.decorations.append(Decoration(12 * 16, 62 * 16, settings.TEXTURES["faro"]))
            self.decorations.append(Decoration(57 * 16, 67 * 16, settings.TEXTURES["faro"]))
            self.decorations.append(Decoration(98 * 16, 81 * 16, settings.TEXTURES["faro"]))
            
           
            self.decorations.append(Decoration(43 * 16, 53 * 16, settings.TEXTURES["arbol1"]))
            self.decorations.append(Decoration(22 * 16, 72 * 16, settings.TEXTURES["arbol1"]))
            self.decorations.append(Decoration(124 * 16, 67 * 16, settings.TEXTURES["arbol1"]))
            
          
            self.decorations.append(Decoration(62 * 16, 36 * 16, settings.TEXTURES["toldo"]))
            self.decorations.append(Decoration(81 * 16, 36 * 16, settings.TEXTURES["toldo"]))
            
            
            self.decorations.append(Decoration(63 * 16, 68 * 16, settings.TEXTURES["fence_madera"]))
            
            
            self.decorations.append(Decoration(12 * 16, 24 * 16, settings.TEXTURES["arbusto"]))
            self.decorations.append(Decoration(34 * 16, 27 * 16, settings.TEXTURES["arbusto"]))
            self.decorations.append(Decoration(12 * 16, 36 * 16, settings.TEXTURES["arbusto"]))
            self.decorations.append(Decoration(57 * 16, 19 * 16, settings.TEXTURES["arbusto"]))
            self.decorations.append(Decoration(25 * 16, 59 * 16, settings.TEXTURES["arbusto"]))
            self.decorations.append(Decoration(46 * 16, 80 * 16, settings.TEXTURES["arbusto"]))
            
            
            self.decorations.append(Decoration(15 * 16, 85 * 16, settings.TEXTURES["carros"]))
            self.decorations.append(Decoration(0 * 16, 39 * 16, settings.TEXTURES["carros"]))
            
            
            self.decorations.append(Decoration(64 * 16, 46 * 16, settings.TEXTURES["dulces"]))
            self.decorations.append(Decoration(72 * 16, 46 * 16, settings.TEXTURES["dulces"]))
            self.decorations.append(Decoration(84 * 16, 46 * 16, settings.TEXTURES["dulces"]))
            
            # fence
            fence_width = 352
            fence_y = 1744
            
            # Logos (force the bottom edge of the rectangle to overlap the fence)
            logo1 = Decoration(4 * 16, 109 * 16, settings.TEXTURES["logo"])
            logo1.hitbox = pygame.Rect(logo1.x, logo1.y, logo1.width, 2000 - logo1.y)
            self.decorations.append(logo1)
            
            logo2 = Decoration(139 * 16, 109 * 16, settings.TEXTURES["logo"])
            logo2.hitbox = pygame.Rect(logo2.x, logo2.y, logo2.width, 2000 - logo2.y)
            self.decorations.append(logo2)

            # fence paterns
            self.decorations.append(Decoration(0, fence_y, settings.TEXTURES["valla_horizontal"]))
            self.decorations.append(Decoration(fence_width, fence_y, settings.TEXTURES["valla_horizontal"]))
            
            # Gate
            Gate_x = fence_width * 2
            Gate_y = fence_y - 16
            Gate_width = 192 # 12 tiles exactos de ancho
            self.decorations.append(Decoration(Gate_x, Gate_y, settings.TEXTURES["porton"]))
            
            # fence
            fence_2_x = Gate_x + Gate_width
            self.decorations.append(Decoration(fence_2_x, fence_y, settings.TEXTURES["valla_horizontal"]))
            self.decorations.append(Decoration(fence_2_x + fence_width, fence_y, settings.TEXTURES["valla_horizontal"]))
            
            #Door between fences
            door_x = fence_2_x + (fence_width * 2)
            self.decorations.append(Decoration(door_x, Gate_y, settings.TEXTURES["puerta"]))
            
            #Fence
            door_gap = settings.TEXTURES["puerta"].get_width()
            current_x = door_x + door_gap
            while current_x < 2400:
                self.decorations.append(Decoration(current_x, fence_y, settings.TEXTURES["valla_horizontal"]))
                current_x += fence_width
                
        elif map_name == "amphitheater_map":
            # Door frames with a giant logical lower bound so that the player always passes underneath them 
            marco1 = Decoration(18 * 16, 26 * 16, settings.TEXTURES["marco_superior"])
            marco1.hitbox = pygame.Rect(marco1.x, marco1.y, marco1.width, 2500)
            self.decorations.append(marco1)
            
            marco2 = Decoration(76 * 16, 26 * 16, settings.TEXTURES["marco_superior"])
            marco2.hitbox = pygame.Rect(marco2.x, marco2.y, marco2.width, 2500)
            self.decorations.append(marco2)
            
        elif map_name == "office":
            self.npcs.append(DrPepe(150, 150))
            self.npcs.append(Jezu(80, 150))
            self.transitions.append(MapTransition(20, 150, 32, 32, "main_map", (200, 200), self._trigger_transition))
        elif map_name == "amphitheater":
            self.transitions.append(MapTransition(20, 150, 32, 32, "main_map", (200, 200), self._trigger_transition))
        elif map_name == "anatomy":
            self.transitions.append(MapTransition(20, 150, 32, 32, "main_map", (200, 200), self._trigger_transition))

    #Transitions
    
    def _trigger_room_transition(self, door):
        self.player.input_locked = True
        
        player_center_y = self.player.hitbox.centery
        door_center_y = door.centery
        
        # Y target
        if player_center_y > door_center_y:
            # going up
            target_y = door.top - self.player.hitbox.height - 4
        else:
            # going down
            target_y = door.bottom + 4
            
        # check new room
        test_rect = pygame.Rect(self.player.hitbox.x, target_y, self.player.hitbox.width, self.player.hitbox.height)
        target_room = None
        for idx, room in self.rooms.items():
            if room.colliderect(test_rect):
                target_room = idx
                break
                
        if target_room is None or target_room == self.active_room:
            self.player.input_locked = False
            return
            
        # Actual target coordinates of the player (because player.y refers to the sprite)
        offset_y = self.player.hitbox_offset_y
        real_target_y = target_y - offset_y
        
        # Aling center x
        real_target_x = door.centerx - (self.player.rect.width / 2)
        
        # save it for interpolation
        self._fade_out_room = self.active_room
        self._fade_in_room = target_room
        self._fade_out_val = 255.0
        self._fade_in_val = 0.0
        
        self.active_room = target_room
        
        Timer.tween(
            1.2, 
            [
                (self.player, {'x': float(real_target_x), 'y': float(real_target_y)}),
                (self, {'_fade_out_val': 0.0, '_fade_in_val': 255.0})
            ],
            on_finish=lambda: setattr(self.player, 'input_locked', False)
        )

    def _trigger_transition(self, target_map, spawn_point):
        print(f"[GameWorld] Solicitando cambio a mapa: {target_map}")
        # Delegate the map change entirely to PlayState so that it handles the stack correctly
        if self.on_map_change:
            self.on_map_change(target_map, spawn_point)

    #Interaction

    def interact(self):
        interact_rect = self.player.hitbox.inflate(20, 20)
        for npc in self.npcs:
            if interact_rect.colliderect(npc.rect):
                npc.interact()
                return
        for item in self.interactables:
            if interact_rect.colliderect(item.rect):
                item.trigger()
                return


    def update(self, dt):
        self.player.update(dt)
        self.camera.update(dt)
        
        # Internal transition
        if not getattr(self.player, 'input_locked', False):
            for door in self.internal_doors:
                if self.player.hitbox.colliderect(door):
                    self._trigger_room_transition(door)
                    break
        
        # Apply fade values
        if hasattr(self, '_fade_out_room'):
            self.room_alphas[self._fade_out_room] = self._fade_out_val
            self.room_alphas[self._fade_in_room] = self._fade_in_val

        self.active_interactable = None
        interact_rect = self.player.hitbox.inflate(20, 20)
        
        for npc in self.npcs:
            npc.update(dt)
            if interact_rect.colliderect(npc.rect) and not self.active_interactable:
                self.active_interactable = npc

        for b in self.buildings:
            b.update(dt)

        for item in self.interactables:
            if interact_rect.colliderect(item.rect) and not self.active_interactable:
                self.active_interactable = item

        for transition in self.transitions:
            if self.player.hitbox.colliderect(transition.rect):
                transition.trigger()
                break


    def render(self, surface):
        #Render using the world's internal camera with Y sorting
        surface.fill((30, 30, 30))

        if self.tilemap:
            self.tilemap.render(surface, self.camera)

        # Y sorting
        # combine all the entities that have depth
        entities = self.npcs + self.decorations + self.buildings + [self.player]
        
        # Sort the bottom border of the sprite
        entities.sort(key=lambda e: getattr(e, 'hitbox', e.rect).bottom)
        
        # render in order
        for entity in entities:
            entity.render(surface, self.camera)
            
        #Dark Effect by Room
        if self.rooms:

            dark_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            dark_surf.fill((0, 0, 0, 255))
            
            # dim the lights in the open rooms
            for idx, room_rect in self.rooms.items():
                visibility = self.room_alphas.get(idx, 0)
                if visibility > 0:
                    screen_rect = self.camera.apply(room_rect)
                    
                    hole = pygame.Surface((screen_rect.width, screen_rect.height), pygame.SRCALPHA)
                    # BLEND_RGBA_MIN take minor value. 
                    hole.fill((255, 255, 255, max(0, min(255, 255 - int(visibility)))))
                    
                    dark_surf.blit(hole, screen_rect, special_flags=pygame.BLEND_RGBA_MIN)
                    
            # Draw darkness on the map and entities
            surface.blit(dark_surf, (0, 0))

        # Debug, dibujar collision_rects
        # for r in self.collision_rects:
        #     pygame.draw.rect(surface, (255,0,0), self.camera.apply(r), 1)
