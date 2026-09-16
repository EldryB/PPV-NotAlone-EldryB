
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
        self.sanity_system = SanitySystem()
        self.inventory = Inventory(self.sanity_system)
        self.quest_manager = QuestManager()

        self.ui_stack = StateStack()
        self.world_stack = []

        self.hud = HUD(self.sanity_system, self.quest_manager)

        self.is_transitioning = False
        self.fade_alpha = 0.0
        self.fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
        self.fade_surface.fill((0, 0, 0))

        self.world = GameWorld("main_map", on_map_change=self.on_map_change, on_puzzle_trigger=self.on_puzzle_trigger)
        self.world.load_map("main_map", spawn_point=(320, 350))
        
        test_lines = [
            "¿Por qué me llamaría tan tarde el Dr. Pepe?",
            "Si no fuera porque necesitara esos puntos en la materia...",
            "...me hubiera quedado en casa."
        ]
        self.ui_stack.push(DialogueState(ui_stack=self.ui_stack, lines=test_lines, speaker="Andrea"))

    def on_puzzle_trigger(self, puzzle_type):
        if puzzle_type == "simon_says":

            def on_success():
                print("[PlayState] Puzzle resuelto exitosamente!")
                pass
                
            self.ui_stack.push(SimonSaysState(self.ui_stack, on_success=on_success, sanity_system=self.sanity_system))

    def on_map_change(self, target_map, spawn_point=(3*16, 14*16)):
        if getattr(self, 'is_transitioning', False): return
        print(f"[PlayState] Apilando mundo actual y viajando a {target_map}")
        
        self.is_transitioning = True
        Timer.tween(1.0, [(self, {'fade_alpha': 255.0})], on_finish=lambda: self._execute_map_change(target_map, spawn_point))

    def _execute_map_change(self, target_map, spawn_point):
        self.world_stack.append(self.world)
        self.world = GameWorld(target_map, on_map_change=self.on_map_change, on_puzzle_trigger=self.on_puzzle_trigger)
        self.world.load_map(target_map, spawn_point=spawn_point)
        Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=lambda: setattr(self, 'is_transitioning', False))

    def return_to_previous_map(self):
        if len(self.world_stack) > 0 and not getattr(self, 'is_transitioning', False):
            print("[PlayState] Regresando al mapa anterior...")
            self.is_transitioning = True
            Timer.tween(1.0, [(self, {'fade_alpha': 255.0})], on_finish=self._execute_map_return)

    def _execute_map_return(self):
        self.world = self.world_stack.pop()
        Timer.tween(1.0, [(self, {'fade_alpha': 0.0})], on_finish=lambda: setattr(self, 'is_transitioning', False))

    def update(self, dt: float) -> None:
        if len(self.ui_stack.states) > 0:
            self.ui_stack.update(dt)
        else:
            self.world.update(dt)
            self.sanity_system.update(dt)
            self.quest_manager.update(dt)
            self.hud.update(dt)
            if getattr(self.sanity_system, 'is_dead', lambda: False)():
                self.state_machine.change("game_over")

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.hud.render(surface)
        
        if getattr(self.world, 'active_interactable', None):
            self.hud.render_interaction_prompt(surface)

        if len(self.ui_stack.states) > 0:
            self.ui_stack.render(surface)
            
        if getattr(self, 'fade_alpha', 0) > 0:
            if not hasattr(self, 'fade_surface'):
                self.fade_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT))
                self.fade_surface.fill((0, 0, 0))
            self.fade_surface.set_alpha(int(self.fade_alpha))
            surface.blit(self.fade_surface, (0, 0))

    def on_input(self, input_id: str, input_data) -> None:
        if getattr(self, 'is_transitioning', False): return
        
        if len(self.ui_stack.states) > 0:
            self.ui_stack.on_input(input_id, input_data)
            return
        
        if input_data.pressed:
            if input_id == "interact":
                if getattr(self.world, 'active_interactable', None):
                    if hasattr(self.world.active_interactable, 'trigger'):
                        self.world.active_interactable.trigger()
                    elif hasattr(self.world.active_interactable, 'interact'):
                        self.world.active_interactable.interact()
            elif input_id == "return":
                self.return_to_previous_map()
            elif input_id == "inventory":
                self.ui_stack.push(InventoryState(inventory=self.inventory, ui_stack=self.ui_stack))
