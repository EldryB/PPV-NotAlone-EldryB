import settings

class PuzzleManager:
    def __init__(self, play_state):
        self.play_state = play_state
        self.quest_manager = play_state.quest_manager
        self.ui_stack = play_state.ui_stack
        if not hasattr(self.play_state, 'completed_puzzles'):
            self.play_state.completed_puzzles = set()
            
    def trigger_puzzle(self, puzzle_type):
        if puzzle_type == "locker":
            self._handle_locker()
        elif puzzle_type == "poster":
            from src.states.ui.PosterSceneState import PosterSceneState
            self.ui_stack.push(PosterSceneState(self.ui_stack))
        elif puzzle_type == "watch":
            from src.states.ui.WatchSceneState import WatchSceneState
            self.ui_stack.push(WatchSceneState(self.ui_stack))
        elif puzzle_type == "coat":
            self._handle_coat()
        elif puzzle_type == "closet":
            self._handle_closet()

    def _handle_locker(self):
        if "locker_simon" in self.play_state.completed_puzzles:
            import src.world.GameWorld as gw
            gw.GameWorld.dr_pepe_disabled = True
            
            if "locker_memory" in self.play_state.completed_puzzles:
                from src.states.ui.DialogueState import DialogueState
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["Ya revise aqui, no hay nada mas."], speaker="Andrea"))
                return
                
            from src.puzzles.MemoryPuzzle import MemoryPuzzle
            from src.states.ui.PuzzleState import PuzzleState
            from src.states.ui.LockerSceneState import LockerSceneState
            
            def on_memory_success():
                self.play_state.completed_puzzles.add("locker_memory")
                if self.quest_manager.current_objective_text() == "Buscar mis cosas en el anfiteatro":
                    self.quest_manager.notify("find_keys")
                self.ui_stack.push(LockerSceneState(self.ui_stack, inventory=getattr(self.play_state, 'inventory', None), quest_manager=self.quest_manager, mode="retrieve_keys"))
                
            def on_memory_fail():
                self.ui_stack.pop()
                
            mem = MemoryPuzzle(on_success=on_memory_success, on_fail=on_memory_fail)
            mem.sanity_system = getattr(self.play_state, "sanity_system", None)
            self.ui_stack.push(PuzzleState(self.ui_stack, mem, getattr(self.play_state, "inventory", None)))
        else:
            import src.world.GameWorld as gw
            gw.GameWorld.jezu_disabled = True
            
            from src.states.ui.SimonSaysState import SimonSaysState
            from src.states.ui.LockerSceneState import LockerSceneState
            
            def on_success():
                self.play_state.completed_puzzles.add("locker_simon")
                print("[PuzzleManager] Simon Says solved! Starting cutscene...")
                self.quest_manager.notify("store_things")
                if hasattr(self.play_state, 'inventory'):
                    self.play_state.inventory.remove_item("inv_llaves")
                self.ui_stack.push(LockerSceneState(self.ui_stack, inventory=getattr(self.play_state, 'inventory', None)))
                
            self.ui_stack.push(SimonSaysState(self.ui_stack, on_success=on_success, sanity_system=self.play_state.sanity_system))

    def _handle_coat(self):
        def remove_coat():
            if hasattr(self.play_state.world, 'coat_decoration') and self.play_state.world.coat_decoration in self.play_state.world.decorations:
                self.play_state.world.decorations.remove(self.play_state.world.coat_decoration)
        from src.states.ui.CoatSceneState import CoatSceneState
        self.ui_stack.push(CoatSceneState(
            self.ui_stack,
            inventory=getattr(self.play_state, 'inventory', None),
            quest_manager=self.quest_manager,
            on_complete=remove_coat
        ))

    def _handle_closet(self):
        from src.states.ui.ClosetSceneState import ClosetSceneState
        from src.states.ui.DialogueState import DialogueState
        
        is_opened = "closet_opened" in getattr(self.play_state, "completed_puzzles", set())
                
        if is_opened:
            if "safe_puzzle" in getattr(self.play_state, "completed_puzzles", set()):
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["La caja fuerte ya esta abierta y vacia."], speaker="Andrea"))
                return
                
            from src.states.ui.PuzzleState import PuzzleState
            from src.puzzles.SafePuzzle import SafePuzzle
            
            def on_safe_complete():
                self.play_state.completed_puzzles.add("safe_puzzle")
                print("Safe opened!")
                self.quest_manager.notify("get_skull")
                if hasattr(self.play_state, 'inventory'):
                    self.play_state.inventory.add_item("inv_craneo")
                self.ui_stack.push(DialogueState(
                    self.ui_stack,
                    lines=["La caja fuerte se abrio!", "Aqui esta el craneo para la practica. (+1 Craneo)"],
                    speaker="Andrea"
                ))
                
            safe_puzzle = SafePuzzle(on_complete=on_safe_complete, on_fail=lambda: None, sanity_system=getattr(self.play_state, "sanity_system", None))
            safe_puzzle.reset()
            self.ui_stack.push(PuzzleState(self.ui_stack, safe_puzzle, getattr(self.play_state, "inventory", None)))
            
        else:
            def on_closet_complete():
                self.play_state.completed_puzzles.add("closet_opened")
                if hasattr(self.play_state.world, 'closet_decoration') and self.play_state.world.closet_decoration:
                    if hasattr(settings, 'TEXTURES') and "armario_abierto" in settings.TEXTURES:
                        self.play_state.world.closet_decoration.texture = settings.TEXTURES["armario_abierto"]
                    
                self.ui_stack.push(DialogueState(
                    self.ui_stack,
                    lines=["Ah! Hay una caja fuerte aqui."],
                    speaker="Andrea"
                ))
                
            self.ui_stack.push(ClosetSceneState(self.ui_stack, on_complete=on_closet_complete))