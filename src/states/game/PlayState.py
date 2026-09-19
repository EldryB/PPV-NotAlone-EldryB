
import pygame
from gale.state import BaseState, StateStack
from gale.timer import Timer

from src.world.GameWorld import GameWorld
from src.systems.SanitySystem import SanitySystem
from src.systems.Inventory import Inventory
from src.systems.QuestManager import QuestManager
from src.states.ui.InventoryState import InventoryState
from src.states.ui.DialogueState import DialogueState
from src.states.ui.SimonSaysState import SimonSaysState
from src.ui.HUD import HUD
import settings

class PlayState(BaseState):
    def enter(self, **kwargs) -> None:
        from src.systems.PhoneManager import PhoneManager
        self.sanity_system = SanitySystem()
        self.inventory = Inventory(self.sanity_system)
        self.quest_manager = QuestManager()
        self.phone_manager = PhoneManager()
        
        from src.systems.AudioManager import AudioManager
        if not AudioManager.get_instance():
            self.audio_manager = AudioManager(self)
        else:
            self.audio_manager = AudioManager.get_instance()
            self.audio_manager.play_state = self
            self.audio_manager.stop_lost()
            self.audio_manager.stop_challenge_music()
        
        self.ui_stack = StateStack()
        self.world_stack = []
        self.completed_puzzles = set()
        
        self.is_transitioning = False
        
        self.global_shake_timer = 0.0
        self.is_shaking = False
        self.shake_duration = 0.0
        self.shake_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        
        if kwargs.get("fade_in", False):
            self.fade_alpha = 255.0
        else:
            self.fade_alpha = 0.0
            
        self.fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        self.fade_surface.fill((0, 0, 0))

        load_slot = kwargs.get("load_slot")
        if load_slot is not None:
            import src.systems.SaveSystem as ss
            ss.load_game(load_slot, self)
            
            if kwargs.get("fade_in", False):
                from gale.timer import Timer
                Timer.tween(1.0, [(self, {'fade_alpha': 0.0})])
        else:
            self.world = GameWorld("main_map", on_map_change=self.on_map_change, on_puzzle_trigger=self.on_puzzle_trigger, on_dialogue=self.on_dialogue_trigger, on_note_proximity=self.on_note_proximity, on_note_interact=self.on_note_interact)
            self.world.load_map("main_map", spawn_point=(19 * 16, 106 * 16))
            
            test_lines = [
                "¿Por qué me llamaría tan tarde el Dr. Pepe?",
                "Si no fuera porque necesitara esos puntos en la materia...",
                "...me hubiera quedado en casa."
            ]
            
            def start_fade_in():
                if kwargs.get("fade_in", False):
                    from gale.timer import Timer
                    Timer.tween(1.0, [(self, {'fade_alpha': 0.0})])
                    
            self.ui_stack.push(DialogueState(ui_stack=self.ui_stack, lines=test_lines, speaker="Andrea", on_close=start_fade_in))

        self.hud = HUD(self.sanity_system, self.quest_manager, phone_manager=self.phone_manager)

    def on_note_proximity(self, texts):
        from src.states.ui.DialogueState import DialogueState
        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=texts,
            speaker="Andrea"
        ))

    def on_note_interact(self, texts, note_index):
        from src.states.ui.DialogueState import DialogueState
        
        def after_note():
            # note_index 2 (Note 3) is just standard dialogue now, no objective change
            if note_index == 4:
                self.quest_manager.notify("find_things_1")
            elif note_index == 5:
                self.quest_manager.notify("find_things_2")
            elif note_index == 7:
                self.quest_manager.notify("find_things_3")
                
            if note_index == 2:
                from gale.timer import Timer
                def send_foto2():
                    from src.states.ui.DialogueState import DialogueState
                    def after_dialogue():
                        if hasattr(self, 'phone_manager'):
                            self.phone_manager.send_message(dialogue_lines=[], is_animated=True, overlay_key="foto2")
                    self.ui_stack.push(DialogueState(
                        self.ui_stack,
                        lines=["(Has recibido un mensaje)"],
                        speaker="Telefono",
                        on_close=after_dialogue
                    ))
                Timer.after(3.0, send_foto2)
            elif note_index == 11:
                def start_scene():
                    from src.states.ui.DrDeadSceneState import DrDeadSceneState
                    
                    def on_demo_end():
                        self.ui_stack.clear()
                        self.state_machine.change("title")
                        
                    self.ui_stack.push(DrDeadSceneState(self.ui_stack, on_close=on_demo_end))
                
                # Append to the end of dialogue
                start_scene()
            elif note_index == 8:
                # Play loud sound
                if "loud_bang" in settings.SOUNDS:
                    settings.SOUNDS["loud_bang"].play()
                    
                def on_qte_complete():
                    if hasattr(self, 'inventory') and self.inventory:
                        self.inventory.add_pills(1)
                    self.return_to_previous_map()
                def start_qte():
                    from src.states.ui.QTEEscapeState import QTEEscapeState
                    self.ui_stack.push(QTEEscapeState(
                        self.world,
                        self.ui_stack,
                        on_complete=on_qte_complete,
                        on_fail=None
                    ))
                    
                def d2():
                    from src.states.ui.DialogueState import DialogueState
                    self.ui_stack.push(DialogueState(
                        self.ui_stack,
                        lines=["QUE HA SIDO ESO!!!"],
                        speaker="Andrea",
                        on_close=start_qte
                    ))
                from src.states.ui.DialogueState import DialogueState
                self.ui_stack.push(DialogueState(
                    self.ui_stack,
                    lines=["(Vidrio rompiendose)"],
                    speaker="",
                    on_close=d2
                ))

        self.ui_stack.push(DialogueState(
            self.ui_stack,
            lines=texts,
            speaker="Desconocido",
            on_close=after_note
        ))

    def on_dialogue_trigger(self, dialogue_key, custom_lines=None):
        from src.states.ui.DialogueState import DialogueState
        from src.systems.EventManager import EventManager
        
        if dialogue_key == "random_msg" and custom_lines:
            self.ui_stack.push(DialogueState(
                self.ui_stack,
                lines=custom_lines,
                speaker="Andrea"
            ))
            return
            
        event_manager = EventManager(self)
        if event_manager.trigger_event(dialogue_key):
            return
            
        # Fallback to DialogueManager for any missing keys
        from src.systems.DialogueManager import DialogueManager
        dialogue_manager = DialogueManager()
        lines_data = dialogue_manager.get_dialogue(dialogue_key)
        if lines_data and lines_data[0][1] != "Dialogue not found.":
            speaker = lines_data[0][0]
            texts = [t for s, t in lines_data]
            self.ui_stack.push(DialogueState(
                self.ui_stack,
                lines=texts,
                speaker=speaker
            ))
            return

    def on_puzzle_trigger(self, puzzle_type):
        from src.systems.PuzzleManager import PuzzleManager
        pm = PuzzleManager(self)
        pm.trigger_puzzle(puzzle_type)

    def on_map_change(self, target_map, spawn_point=(3*16, 14*16)):
        if getattr(self, 'is_transitioning', False): return
        
        if target_map == "return":
            def post_return():
                if getattr(self, 'delivered_coat', False) and not getattr(self, 'find_keys_dialogue_shown', False):
                    self.find_keys_dialogue_shown = True
                    self.quest_manager.notify("return_coat")
                    from src.states.ui.DialogueState import DialogueState
                    self.ui_stack.push(DialogueState(
                        self.ui_stack,
                        lines=["Voy a buscar mis cosas en el anfiteatro"],
                        speaker="Andrea"
                    ))
            
            self.return_to_previous_map(on_finish=post_return)
            return
            
        print(f"[PlayState] Apilando mundo actual y viajando a {target_map}")
        self.is_transitioning = True
        
        def do_map_change():
            def after_transition():
                obj_text = self.quest_manager.current_objective_text()
                
                # Check target triggers
                if target_map == "amphitheater_map" and obj_text == "Ir al anfiteatro":
                    self.quest_manager.notify("arrive_amphitheater")
                    from src.states.ui.DialogueState import DialogueState
                    self.ui_stack.push(DialogueState(
                        self.ui_stack,
                        lines=["Deberia guardar mis cosas en el casillero"],
                        speaker="Andrea"
                    ))
                elif target_map == "anatomy_map" and obj_text == "Ir al edificio Antiguo de Anatomia":
                    if "locker_memory" not in getattr(self, "completed_puzzles", set()):
                        self.quest_manager.notify("arrive_anatomy")
                    else:
                        self.quest_manager.notify("go_anatomy_2")
                elif target_map == "office_map" and obj_text == "Ir a la oficina del Dr Pepe":
                    self.quest_manager.notify("go_office")
                elif target_map == "embriology_map" and obj_text == "Ir al edificio de Embriologia":
                    self.quest_manager.notify("go_embryology")
                    
            self._execute_map_change(target_map, spawn_point, after_transition)
            
        from gale.timer import Timer
        Timer.tween(1.0, [(self, {'fade_alpha': 255.0})], on_finish=do_map_change)

    def _execute_map_change(self, target_map, spawn_point, on_finish_fade=None):
        self.world_stack.append(self.world)
        self.world = GameWorld(target_map, on_map_change=self.on_map_change, on_puzzle_trigger=self.on_puzzle_trigger, on_dialogue=self.on_dialogue_trigger, on_note_proximity=self.on_note_proximity, on_note_interact=self.on_note_interact)
        self.world.load_map(target_map, spawn_point=spawn_point)
        
        def finalize():
            setattr(self, 'is_transitioning', False)
            
            if "locker_memory" in self.completed_puzzles and not getattr(self, "final_phone_notified", False):
                self.final_phone_notified = True
                from gale.timer import Timer
                def send_final_phone():
                    from src.states.ui.DialogueState import DialogueState
                    def after_dialogue():
                        if hasattr(self, 'phone_manager'):
                            self.phone_manager.send_message(dialogue_lines=[], is_animated=True, overlay_key="foto1")
                    self.ui_stack.push(DialogueState(
                        self.ui_stack,
                        lines=["(Has recibido un mensaje)"],
                        speaker="Telefono",
                        on_close=after_dialogue
                    ))
                Timer.after(3.0, send_final_phone)

            if on_finish_fade:
                on_finish_fade()
                
        Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=finalize)

    def return_to_previous_map(self, on_finish=None):
        if len(self.world_stack) > 0 and not getattr(self, 'is_transitioning', False):
            print("[PlayState] Regresando al mapa anterior...")
            self.is_transitioning = True
            self._map_return_callback = on_finish
            Timer.tween(1.0, [(self, {'fade_alpha': 255.0})], on_finish=self._execute_map_return)

    def _execute_map_return(self):
        self.world = self.world_stack.pop()
        
        def on_fade_in():
            setattr(self, 'is_transitioning', False)
            cb = getattr(self, '_map_return_callback', None)
            if cb:
                cb()
                self._map_return_callback = None
            
            import src.world.GameWorld as gw
            if getattr(gw.GameWorld, 'jezu_disabled', False):
                self.world.npcs = [npc for npc in self.world.npcs if getattr(npc, "__class__", None).__name__ != "Jezu"]
            if getattr(gw.GameWorld, 'dr_pepe_disabled', False):
                self.world.npcs = [npc for npc in self.world.npcs if getattr(npc, "__class__", None).__name__ != "DrPepe"]

            from src.states.ui.DialogueState import DialogueState

            def _send_phone(lines, delay=2.0):
                from gale.timer import Timer
                def do_send():
                    if hasattr(self, 'phone_manager'):
                        self.phone_manager.send_message(dialogue_lines=lines)
                        if not getattr(self, 'phone_tutorial_shown', False):
                            self.phone_tutorial_shown = True
                            from src.states.ui.PhoneTutorialState import PhoneTutorialState
                            self.ui_stack.push(PhoneTutorialState(self.ui_stack))
                Timer.after(delay, do_send)

            obj = self.quest_manager.current_objective_text()

            # Msg 1: Jezu writes when leaving amphitheater after storing things (going to anatomy)
            if obj == "Ir al edificio Antiguo de Anatomia" and not getattr(self, "jezu_msg_sent", False):
                self.jezu_msg_sent = True
                _send_phone([
                    "(Te ha escrito Jezu)",
                    "Jezu: 'En 15 minutos salimos, trata de terminar rapido'",
                    "En un rato le contesto"
                ], delay=4.0)

            # Msg 2: Desconocido after leaving office with coat delivered
            elif getattr(self, "delivered_coat", False):
                self.delivered_coat = False
                self.quest_manager.notify("return_coat")

                def trigger_find_keys():
                    if not getattr(self, "desconocido_msg_sent", False):
                        self.desconocido_msg_sent = True
                        _send_phone([
                            "(Te ha escrito un numero desconocido)",
                            "Desconocido: 'Ten cuidado, que no se te vaya a olvidar nada'",
                            "Que raro que Jezu no me escribio desde su numero"
                        ], delay=1.5)

                def a2():
                    self.ui_stack.push(DialogueState(self.ui_stack,
                        lines=["Voy a buscar mis cosas en el anfiteatro."],
                        speaker="Andrea", on_close=trigger_find_keys))

                self.ui_stack.push(DialogueState(self.ui_stack,
                    lines=["El Doctor jura que es gracioso"],
                    speaker="Andrea", on_close=a2))

            # Foto 1: leaving amphitheater without keys (keys not found yet)
            elif obj == "Buscar mis cosas en el anfiteatro" and not getattr(self, "foto1_sent", False) and "locker_simon" in self.completed_puzzles:
                self.foto1_sent = True
                from gale.timer import Timer
                def send_foto1():
                    def after_notif():
                        if hasattr(self, 'phone_manager'):
                            self.phone_manager.send_message(dialogue_lines=[], is_animated=True, overlay_key="foto1")
                    self.ui_stack.push(DialogueState(self.ui_stack,
                        lines=["(Has recibido un mensaje)"],
                        speaker="Telefono", on_close=after_notif))
                Timer.after(3.0, send_foto1)
                
        Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=on_fade_in)

    def update(self, dt: float) -> None:
        is_paused = any(getattr(s, "__class__", None).__name__ == "PauseState" for s in self.ui_stack.states)
        
        if hasattr(self, 'audio_manager'):
            self.audio_manager.update(dt)
            
        if is_paused:
            self.ui_stack.update(dt)
            return

        if hasattr(self, 'phone_manager') and self.phone_manager.has_messages():
            if hasattr(self.world, 'player'):
                self.world.player.input_locked = True
                self.world.player.velocity.update(0, 0)
                if hasattr(self.world.player, 'change_state'):
                    self.world.player.change_state("idle")
        else:
            if hasattr(self.world, 'player') and getattr(self.world.player, 'input_locked', False):
                pass

        if len(self.ui_stack.states) > 0:
            self.ui_stack.update(dt)
        else:
            has_msgs = hasattr(self, 'phone_manager') and self.phone_manager.has_messages()
            was_locked = getattr(self.world.player, 'input_locked', False) if hasattr(self.world, 'player') else False
            
            if has_msgs and hasattr(self.world, 'player'):
                self.world.player.input_locked = True
                self.world.player.velocity.update(0, 0)
                if hasattr(self.world.player, 'change_state'):
                    self.world.player.change_state("idle")
                
            self.world.update(dt)
            
            self.sanity_system.update(dt)
            self.quest_manager.update(dt)
            self.hud.update(dt)
            
            if has_msgs and not was_locked and hasattr(self.world, 'player'):
                pass
            elif not has_msgs and was_locked and hasattr(self, '_phone_locked') and self._phone_locked:
                self.world.player.input_locked = False
                self._phone_locked = False
                
            if has_msgs:
                self._phone_locked = True
                
            if getattr(self.sanity_system, 'is_dead', lambda: False)():
                self.state_machine.change("game_over")
                
        if self.sanity_system.sanity < 60.0:
            if not getattr(self, 'is_shaking', False):
                self.global_shake_timer += dt
                if self.global_shake_timer >= 15.0:
                    self.is_shaking = True
                    self.shake_duration = 3.0
                    self.global_shake_timer = 0.0
            else:
                self.shake_duration -= dt
                if self.shake_duration <= 0:
                    self.is_shaking = False
        else:
            self.is_shaking = False
            self.global_shake_timer = 0.0

    def render(self, surface: pygame.Surface) -> None:
        if getattr(self, 'is_shaking', False):
            import random
            dx = random.randint(-3, 3)
            dy = random.randint(-3, 3)
            render_surf = getattr(self, 'shake_surface', None)
            if render_surf is None:
                render_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
                self.shake_surface = render_surf
            
            render_surf.fill((0, 0, 0))
            self._do_render(render_surf)
            
            # Clear main surface and blit offset
            surface.fill((0, 0, 0))
            surface.blit(render_surf, (dx, dy))
        else:
            self._do_render(surface)
            
    def _do_render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        
        if getattr(self, 'fade_alpha', 0) > 0:
            if not hasattr(self, 'fade_surface'):
                self.fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
                self.fade_surface.fill((0, 0, 0))
            self.fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(self.fade_surface, (0, 0))
            
        self.hud.render(surface)
        
        if getattr(self.world, 'active_interactable', None):
            self.hud.render_interaction_prompt(surface)

        if len(self.ui_stack.states) > 0:
            self.ui_stack.render(surface)

    def on_input(self, input_id: str, input_data) -> None:
        if getattr(self, 'is_transitioning', False): return
        
        if len(self.ui_stack.states) > 0:
            self.ui_stack.on_input(input_id, input_data)
            return
        
        if input_data.pressed:
            if input_id in ("pause", "cancel"):
                from src.states.ui.PauseState import PauseState
                self.ui_stack.push(PauseState(self))
                return
                
            if hasattr(self, 'phone_manager') and self.phone_manager.has_messages():
                if input_id in ("interact", "return"):
                    return # Block everything except inventory
                    
            if input_id == "interact":
                if getattr(self.world, 'active_interactable', None):
                    if hasattr(self.world.active_interactable, 'trigger'):
                        self.world.active_interactable.trigger()
                    elif hasattr(self.world.active_interactable, 'interact'):
                        self.world.active_interactable.interact()
                        if hasattr(self.world.active_interactable, 'dialogue_key'):
                            self.on_dialogue_trigger(self.world.active_interactable.dialogue_key)
            elif input_id == "return":
                self.return_to_previous_map()
            elif input_id == "inventory":
                def handle_item_click(item_key):
                    if item_key == "inv_pills":
                        self.inventory.use_pill()
                    elif item_key == "inv_phone":
                        if hasattr(self, 'phone_manager') and self.phone_manager.has_messages():
                            msg = self.phone_manager.pop_message()
                            self.ui_stack.pop() # Close inventory
                            
                            if msg.get('is_animated'):
                                import settings
                                settings.SLOW_DIALOGUE = True
                                
                                from src.states.ui.AnimatedPhoneSceneState import AnimatedPhoneSceneState
                                from src.states.ui.DialogueState import DialogueState
                                
                                overlay = msg.get('overlay_key', 'foto1')
                                
                                if overlay == 'foto1':
                                    def d8():
                                        self.quest_manager.notify("find_keys_again")
                                    def d7():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["Necesito mis cosas antes de irme..."], speaker="Andrea", on_close=d8))
                                    def d6():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=[" Querra hacerme dano ?"], speaker="Andrea", on_close=d7))
                                    def d5():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["No se quien es esa persona..."], speaker="Andrea", on_close=d6))
                                    def d4():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["(Andrea queda helada por unos segundos)"], speaker="", on_close=d5))
                                    def d3():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["Entonces, buscame en el cementerio"], speaker="Desconocido", on_close=d4))
                                    def d2():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["Quieres saber en donde estan tus llaves"], speaker="Desconocido", on_close=d3))
                                    def d1():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["Que estas buscando?"], speaker="Desconocido", on_close=d2))
                                    def d0():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["Se te perdio algo??"], speaker="Desconocido", on_close=d1))
                                    
                                    def after_anim():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["(Te ha escrito un numero desconocido)"], speaker="", on_close=d0))

                                    self.ui_stack.push(AnimatedPhoneSceneState(self.ui_stack, on_complete=after_anim, overlay_key="foto1"))
                                else:
                                    def after_anim_2():
                                        self.ui_stack.push(DialogueState(self.ui_stack, lines=["(...)"], speaker="Andrea", on_close=None))
                                    
                                    self.ui_stack.push(AnimatedPhoneSceneState(self.ui_stack, on_complete=after_anim_2, overlay_key="foto2"))
                            elif msg.get('image'):
                                from src.states.ui.PhoneSceneState import PhoneSceneState
                                self.ui_stack.push(PhoneSceneState(self.ui_stack, msg))
                            else:
                                from src.states.ui.DialogueState import DialogueState
                                self.ui_stack.push(DialogueState(self.ui_stack, lines=msg.get('dialogue', []), speaker="Andrea"))
                                
                self.ui_stack.push(InventoryState(inventory=self.inventory, ui_stack=self.ui_stack, on_item_click=handle_item_click))
