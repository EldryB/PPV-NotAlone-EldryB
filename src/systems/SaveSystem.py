import json
import os
import settings

SAVE_DIR = settings.BASE_DIR / "saves"

def save_game(slot: int, play_state):
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    import src.world.GameWorld as gw
    
    data = {
        "map_name": getattr(play_state.world, "map_name", "main_map"),
        "player_x": play_state.world.player.x,
        "player_y": play_state.world.player.y,
        "inventory": {
            "pills": play_state.inventory.pills,
            "items": play_state.inventory.items
        },
        "sanity": play_state.sanity_system.sanity,
        "quest_stage": play_state.quest_manager.current_stage_index,
        "completed_puzzles": list(getattr(play_state, "completed_puzzles", set())),
        "global_note_index": getattr(gw.GameWorld, "global_note_index", 0),
        "jezu_disabled": getattr(gw.GameWorld, "jezu_disabled", False),
        "dr_pepe_disabled": getattr(gw.GameWorld, "dr_pepe_disabled", False),
    }
    
    with open(SAVE_DIR / f"save_{slot}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_game(slot: int, play_state):
    file_path = SAVE_DIR / f"save_{slot}.json"
    if not file_path.exists():
        return False
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    import src.world.GameWorld as gw
    
    # Restore global states
    gw.GameWorld.global_note_index = data.get("global_note_index", 0)
    gw.GameWorld.jezu_disabled = data.get("jezu_disabled", False)
    gw.GameWorld.dr_pepe_disabled = data.get("dr_pepe_disabled", False)
    
    # Restore PlayState states
    play_state.completed_puzzles = set(data.get("completed_puzzles", []))
    play_state.quest_manager.current_stage_index = data.get("quest_stage", 0)
    play_state.sanity_system.sanity = data.get("sanity", 100.0)
    
    inv_data = data.get("inventory", {})
    play_state.inventory.pills = inv_data.get("pills", 0)
    play_state.inventory.items = inv_data.get("items", [])
    
    target_map = data.get("map_name", "main_map")
    px = data.get("player_x", 0)
    py = data.get("player_y", 0)
    
    # Setup the world stack correctly if needed
    if target_map != "main_map":
        base_world = gw.GameWorld("main_map", on_map_change=play_state.on_map_change, on_puzzle_trigger=play_state.on_puzzle_trigger, on_dialogue=play_state.on_dialogue_trigger, on_note_proximity=play_state.on_note_proximity, on_note_interact=play_state.on_note_interact)
        base_world.load_map("main_map")
        play_state.world_stack = [base_world]
        
    play_state.world = gw.GameWorld(target_map, on_map_change=play_state.on_map_change, on_puzzle_trigger=play_state.on_puzzle_trigger, on_dialogue=play_state.on_dialogue_trigger, on_note_proximity=play_state.on_note_proximity, on_note_interact=play_state.on_note_interact)
    play_state.world.load_map(target_map, spawn_point=(px, py))
    play_state.world.player.x = px
    play_state.world.player.y = py
    
    # Update sanity bar visual
    play_state.sanity_system.bar.value = max(0.0, play_state.sanity_system.sanity - 40.0)
    
    return True

def get_save_info(slot: int):
    file_path = SAVE_DIR / f"save_{slot}.json"
    if not file_path.exists():
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
