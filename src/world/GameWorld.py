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
    global_note_index = 0

    def __init__(self, map_name, on_map_change=None, on_puzzle_trigger=None, on_dialogue=None, on_note_proximity=None, on_note_interact=None):
        self.on_map_change = on_map_change
        self.on_puzzle_trigger = on_puzzle_trigger
        self.on_dialogue = on_dialogue
        self.on_note_proximity = on_note_proximity
        self.on_note_interact = on_note_interact
        self.tilemap = None
        self.player = None
        self.npcs = []
        self.interactables = []
        self.transitions = []
        self.decorations = []
        self.buildings = []
        self.collision_rects = []
        self.notes = []
        
        
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
        self.closet_decoration = None

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
                    obj_name = (obj.name or "").lower()
                    obj_type = getattr(obj, "class_", getattr(obj, "type", "")).lower()
                    layer_name_lower = layer_name.lower()
                    
                    if "player_spawn" in obj_name or "player_spawn" in obj_type or "player_spawn" in layer_name_lower:
                        spawn_point = (obj.x, obj.y)
                        print(f"[GameWorld] Encontrado player_spawn en {spawn_point} en layer {layer_name_lower}")
                        continue
                        
                    if layer_name_lower in ("door_outside", "door_out") or obj_name in ("door_outside", "door_out") or obj_type in ("door_outside", "door_out"):
                        self.interactables.append(Interactable(
                            obj.x, obj.y, obj.width, obj.height,
                            on_interact=lambda: self._trigger_transition("return", None)
                        ))
                        continue
                        
                    #Collisions
                    if is_collision_layer or obj_name == "collision":
                        self.collision_rects.append(
                            pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                        )
                        
                    #Notes
                    if layer_name.lower() == "note" or obj_name == "note" or obj_type == "note":
                        idx = int(obj.properties.get("index", 0)) if hasattr(obj, 'properties') and 'index' in obj.properties else 0
                        
                        texts = []
                        if hasattr(obj, 'properties') and 'texts' in obj.properties:
                            texts_data = obj.properties['texts']
                            if isinstance(texts_data, list):
                                for td in texts_data:
                                    if isinstance(td, dict) and 'value' in td:
                                        texts.append(td['value'].strip().strip('"'))
                                        
                        prox_texts = []
                        if hasattr(obj, 'properties') and 'proximity_texts' in obj.properties:
                            prox_data = obj.properties['proximity_texts']
                            if isinstance(prox_data, list):
                                for pd in prox_data:
                                    if isinstance(pd, dict) and 'value' in pd:
                                        prox_texts.append(pd['value'].strip().strip('"'))
                                        
                        self.notes.append({
                            'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                            'index': idx,
                            'texts': texts,
                            'proximity_texts': prox_texts,
                            'prox_triggered': False
                        })
                    
                    #Rooms
                    if is_rooms_layer or "room" in obj_name:
                        if hasattr(obj, 'properties') and 'room_index' in obj.properties:
                            idx = int(obj.properties['room_index'])
                            self.rooms[idx] = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                            self.room_alphas[idx] = 0.0 # Oscuridad total por defecto

                    # doors
                    if is_doors_layer or "door" in obj_name:
                        dest_map = None
                        if hasattr(obj, 'properties') and 'object_tag' in obj.properties:
                            tag = obj.properties['object_tag']
                            if tag == "amphitheater": dest_map = "amphitheater_map"
                            elif tag == "anatomy_building": dest_map = "anatomy_map"
                            elif tag == "embriology_building": dest_map = "embriology_map"
                            elif tag == "dr_office": dest_map = "dr_map"
                            else: dest_map = f"{tag}_map"
                        
                        if dest_map:
                            # calculate spawn point for destination
                            spawn_pt = (3 * 16, 14 * 16)
                            if dest_map == "dr_map":
                                spawn_pt = (19 * 16, 21 * 16)
                                
                            #transition map
                            self.interactables.append(Interactable(
                                obj.x, obj.y, obj.width, obj.height,
                                on_interact=lambda m=dest_map, sp=spawn_pt: self._trigger_transition(m, sp)
                            ))
                        else:
                            #Transition room
                            door_idx = 0
                            if hasattr(obj, 'properties') and 'index' in obj.properties:
                                door_idx = int(obj.properties['index'])
                            self.internal_doors.append({
                                'rect': pygame.Rect(obj.x, obj.y, obj.width, obj.height),
                                'index': door_idx
                            })
                            
                    # Random Message Objects
                    if hasattr(obj, 'properties') and 'messages' in obj.properties:
                        messages_data = obj.properties['messages']
                        if isinstance(messages_data, list):
                            parsed_messages = []
                            for msg_dict in messages_data:
                                if isinstance(msg_dict, dict) and 'value' in msg_dict:
                                    val = msg_dict['value'].strip().strip('"')
                                    parsed_messages.append(val)
                            
                            if parsed_messages:
                                def launch_random_message(msgs=parsed_messages):
                                    import random
                                    chosen = random.choice(msgs)
                                    if hasattr(self, 'on_dialogue') and self.on_dialogue:
                                        self.on_dialogue("random_msg", custom_lines=[chosen])
                                        
                                self.interactables.append(Interactable(
                                    obj.x, obj.y, obj.width, obj.height,
                                    on_interact=launch_random_message
                                ))
                                continue
                                
                    is_interactive = layer_name.lower() in ("interactive", "interactivo") or "interactive" in obj_name
                    is_graphics = "graphics" in layer_name.lower()
                    
                    if is_graphics:
                        name_tag = None
                        if hasattr(obj, 'properties') and 'name_tag' in obj.properties:
                            name_tag = str(obj.properties['name_tag'])
                        else:
                            name_tag = (obj.name or "").lower() or getattr(obj, "class_", getattr(obj, "type", "")).lower()
                        
                        if name_tag and name_tag in settings.TEXTURES:
                            dec = Decoration(obj.x, obj.y, settings.TEXTURES[name_tag])
                            if "marco" in name_tag or "puerta" in name_tag or "porton" in name_tag or "logo" in name_tag:
                                dec.hitbox = pygame.Rect(dec.x, dec.y, dec.width, 2500)
                            self.decorations.append(dec)
                            
                            if name_tag == "armario_cerrado":
                                self.closet_decoration = dec
                            elif name_tag == "coat":
                                self.coat_decoration = dec
                        elif name_tag and name_tag in settings.FRAMES:
                            pass
                        continue
                    
                    if is_interactive:
                        tag = None
                        if hasattr(obj, 'properties'):
                            if 'object_tag' in obj.properties: tag = obj.properties['object_tag']
                            elif 'object_type' in obj.properties: tag = obj.properties['object_type']
                            elif 'object_tipe' in obj.properties: tag = obj.properties['object_tipe']
                            
                        if not tag:
                            if "locker" in obj_name or "locker" in obj_type:
                                tag = "locker"
                            elif "closet" in obj_name or "closet" in obj_type:
                                tag = "closet"
                            elif "poster" in obj_name or "poster" in obj_type:
                                tag = "poster"
                            elif "watch" in obj_name or "watch" in obj_type:
                                tag = "watch"
                        
                        if tag:
                            def launch_interaction(interaction_tag=tag):
                                if hasattr(self, 'on_puzzle_trigger'):
                                    self.on_puzzle_trigger(interaction_tag)
                                    
                            self.interactables.append(Interactable(
                                obj.x, obj.y, obj.width, obj.height,
                                on_interact=launch_interaction
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
            if self.active_room is None:
                self.active_room = list(self.rooms.keys())[0] if self.rooms else None
                if self.active_room is not None:
                    self.room_alphas[self.active_room] = 255.0

        # Config camera
        self.camera.follow(self.player, rate=6.0)
        self.camera.x = self.player.x - (settings.VIRTUAL_WIDTH / 2)
        self.camera.y = self.player.y - (settings.VIRTUAL_HEIGHT / 2)
        
        if self.tilemap:
            map_w = self.tilemap.cols * self.tilemap.tile_width
            map_h = self.tilemap.rows * self.tilemap.tile_height
            self.camera.bounds = pygame.Rect(0, 0, map_w, map_h)
            # Enforce bounds immediately
            if self.camera.x < self.camera.bounds.left: self.camera.x = self.camera.bounds.left
            if self.camera.y < self.camera.bounds.top: self.camera.y = self.camera.bounds.top
            if self.camera.x + settings.VIRTUAL_WIDTH > self.camera.bounds.right: self.camera.x = self.camera.bounds.right - settings.VIRTUAL_WIDTH
            if self.camera.y + settings.VIRTUAL_HEIGHT > self.camera.bounds.bottom: self.camera.y = self.camera.bounds.bottom - settings.VIRTUAL_HEIGHT

        self._setup_entities(map_name)

    def _setup_entities(self, map_name):
        if map_name == "main_map":
            from src.entity.Jake import Jake
            self.npcs.append(Jake(19 * 16, 102 * 16))
            if not getattr(GameWorld, 'jezu_disabled', False):
                from src.entity.Jezu import Jezu
                self.npcs.append(Jezu(27 * 16, 68 * 16))
            
            # interactive buildings
            self.buildings.append(Building(
                14 * 16, 
                10 * 16, 
                settings.TEXTURES["edificio1"], 
                "Edificio de AnatomA-a", 
                self.player
            ))
            self.buildings.append(Building(
                63 * 16, 
                77 * 16, 
                settings.TEXTURES["edificio3"], 
                "Edificio de EmbriologA-a", 
                self.player
            ))
            self.buildings.append(Building(
                20 * 16, 
                39 * 16, 
                settings.TEXTURES["edificio5"], 
                "Anfiteatro de AnatomA-a", 
                self.player
            ))
            self.buildings.append(Building(
                1 * 16,
                46 * 16,
                settings.TEXTURES["edificio6"],
                "Oficina del Dr. Pepe",
                self.player
            ))
            
        elif map_name == "dr_map":
            if not getattr(GameWorld, 'dr_pepe_disabled', False):
                self.npcs.append(DrPepe(18 * 16, 3 * 16))
            
        elif map_name == "office":
            if not getattr(GameWorld, 'dr_pepe_disabled', False):
                self.npcs.append(DrPepe(150, 150))
            if not getattr(GameWorld, 'jezu_disabled', False):
                self.npcs.append(Jezu(80, 150))
            self.transitions.append(MapTransition(20, 150, 32, 32, "main_map", (200, 200), self._trigger_transition))
        elif map_name == "amphitheater":
            self.transitions.append(MapTransition(20, 150, 32, 32, "main_map", (200, 200), self._trigger_transition))
        elif map_name == "anatomy":
            self.transitions.append(MapTransition(20, 150, 32, 32, "main_map", (200, 200), self._trigger_transition))

    #Transitions
    
    def _trigger_room_transition(self, door_info):
        door = door_info['rect']
        door_index = door_info.get('index', 0)
        self.player.input_locked = True
        
        target_room = None
        
        if door_index == 0:
            # Vertical
            player_center_y = self.player.hitbox.centery
            door_center_y = door.centery
            
            if player_center_y > door_center_y:
                target_y = door.top - self.player.hitbox.height - 4
            else:
                target_y = door.bottom + 4
                
            test_rect = pygame.Rect(self.player.hitbox.x, target_y, self.player.hitbox.width, self.player.hitbox.height)
            
            offset_y = self.player.hitbox_offset_y
            real_target_y = target_y - offset_y
            real_target_x = door.centerx - (self.player.rect.width / 2)
        else:
            # Horizontal
            player_center_x = self.player.hitbox.centerx
            door_center_x = door.centerx
            
            if player_center_x > door_center_x:
                target_x = door.left - self.player.hitbox.width - 4
            else:
                target_x = door.right + 4
                
            test_rect = pygame.Rect(target_x, self.player.hitbox.y, self.player.hitbox.width, self.player.hitbox.height)
            
            offset_x = self.player.hitbox_offset_x
            real_target_x = target_x - offset_x
            real_target_y = door.centery - (self.player.hitbox.height / 2) - self.player.hitbox_offset_y

        for idx, room in self.rooms.items():
            if room.colliderect(test_rect):
                target_room = idx
                break
                
        if target_room is None or target_room == self.active_room:
            self.player.input_locked = False
            return
        
        # save it for interpolation
        self._fade_out_room = self.active_room
        self._fade_in_room = target_room
        self._fade_out_val = 255.0
        self._fade_in_val = 0.0
        
        self.active_room = target_room
        
        Timer.tween(
            0.9, 
            [
                (self.player, {'x': float(real_target_x), 'y': float(real_target_y)}),
                (self, {'_fade_out_val': 0.0, '_fade_in_val': 255.0})
            ],
            on_finish=lambda: setattr(self.player, 'input_locked', False)
        )

    def _trigger_transition(self, target_map, spawn_point):
        print(f"[GameWorld] Solicitando cambio a mapa: {target_map}")
        from src.systems.AudioManager import AudioManager
        AudioManager.play_sfx("puerta_short")
        if self.on_map_change:
            self.on_map_change(target_map, spawn_point)

    #Interaction

    def interact(self):
        interact_rect = self.player.hitbox.inflate(60, 60)
        for npc in self.npcs:
            if interact_rect.colliderect(npc.rect):
                npc.interact()
                if hasattr(self, 'on_dialogue'):
                    self.on_dialogue(npc.dialogue_key)
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
            door_triggered = False
            for door_info in self.internal_doors:
                if self.player.hitbox.colliderect(door_info['rect']):
                    self._trigger_room_transition(door_info)
                    door_triggered = True
                    break
            
            if not door_triggered and self.rooms:
                for idx, room_rect in self.rooms.items():
                    if idx != self.active_room and room_rect.collidepoint(self.player.hitbox.centerx, self.player.hitbox.centery):
                        self._fade_out_room = self.active_room
                        self._fade_in_room = idx
                        self._fade_out_val = self.room_alphas.get(self.active_room, 0.0)
                        self._fade_in_val = self.room_alphas.get(idx, 0.0)
                        self.active_room = idx
                        
                        from gale.timer import Timer
                        Timer.tween(
                            0.5, 
                            [
                                (self, {'_fade_out_val': 0.0, '_fade_in_val': 255.0})
                            ]
                        )
                        break
        
        # Apply fade values
        if hasattr(self, '_fade_out_room'):
            self.room_alphas[self._fade_out_room] = self._fade_out_val
            self.room_alphas[self._fade_in_room] = self._fade_in_val

        self.active_interactable = None
        interact_rect = self.player.hitbox.inflate(60, 60)
        
        for npc in self.npcs:
            npc.update(dt)
            if interact_rect.colliderect(npc.rect) and not self.active_interactable:
                self.active_interactable = npc

        for b in self.buildings:
            b.update(dt)

        for item in self.interactables:
            if interact_rect.colliderect(item.rect) and not self.active_interactable:
                self.active_interactable = item
                
        # Notes
        for note in self.notes:
            if note['index'] == GameWorld.global_note_index:
                if interact_rect.colliderect(note['rect']):
                    if note['proximity_texts'] and not note['prox_triggered']:
                        for n in self.notes:
                            if n['index'] == note['index']:
                                n['prox_triggered'] = True
                                
                        if hasattr(self, 'on_note_proximity') and self.on_note_proximity:
                            self.on_note_proximity(note['proximity_texts'])
                            
                    if not self.active_interactable:
                        class NoteInteract:
                            def __init__(self, gw, n):
                                self.gw = gw
                                self.n = n
                            def interact(self):
                                if hasattr(self.gw, 'on_note_interact') and self.gw.on_note_interact:
                                    self.gw.on_note_interact(self.n['texts'], self.n['index'])
                                GameWorld.global_note_index += 1
                        
                        self.active_interactable = NoteInteract(self, note)

        for transition in self.transitions:
            if self.player.hitbox.colliderect(transition.rect):
                transition.trigger()
                break

    def render(self, surface):
        surface.fill((30, 30, 30))

        if self.tilemap:
            self.tilemap.render(surface, self.camera)

        note_tex = settings.TEXTURES.get("note")
        active_notes = []
        if note_tex:
            for note in self.notes:
                if note['index'] == GameWorld.global_note_index:
                    class ActiveNote:
                        def __init__(self, rect, tex):
                            self.rect = rect
                            self.hitbox = rect
                            self.tex = tex
                        def render(self, surf, cam):
                            surf.blit(self.tex, cam.apply(self.rect))
                    active_notes.append(ActiveNote(note['rect'], note_tex))

        # Y sorting
        # combine all the entities that have depth
        entities = self.npcs + self.decorations + self.buildings + active_notes + [self.player]
        
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

