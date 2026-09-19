import pathlib
import pygame
from gale import input_handler

input_handler.InputHandler.set_keyboard_action(input_handler.KEY_ESCAPE, "cancel")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_w, "move_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_s, "move_down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_a, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_d, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_UP, "move_up")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_DOWN, "move_down")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_LEFT, "move_left")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RIGHT, "move_right")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_e, "interact")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_r, "return")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_i, "inventory")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_p, "pause")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_RETURN, "confirm")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_SPACE, "confirm")
input_handler.InputHandler.set_keyboard_action(input_handler.KEY_KP_ENTER, "confirm")
input_handler.InputHandler.set_mouse_click_action(input_handler.MOUSE_BUTTON_1, "click")

TITLE = "Not Alone"
BASE_DIR = pathlib.Path(__file__).parent
VIRTUAL_WIDTH = 656
VIRTUAL_HEIGHT = 384
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILE_SIZE = 16

SLOW_DIALOGUE = False

PLAYER_START_PILLS = 0
safe_code_correct = "714"
safe_code_display = "7 1 4"

COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255)
}

SEQUENCE_COLORS = [(200, 50, 50), (50, 100, 200), (50, 180, 50), (200, 200, 50)]
SEQUENCE_BRIGHT_COLORS = [(255, 80, 80), (80, 150, 255), (80, 230, 80), (255, 255, 80)]

MAPS = {
    "main": BASE_DIR / "assets" / "maps" / "main.json",
    "main_map": BASE_DIR / "assets" / "maps" / "main_map.json",
    "office": BASE_DIR / "assets" / "maps" / "office.json",
    "amphitheater": BASE_DIR / "assets" / "maps" / "amphitheater.json",
    "anatomy": BASE_DIR / "assets" / "maps" / "anatomy.json",
    "amphitheater_map": BASE_DIR / "assets" / "maps" / "amphitheater_map.json",
    "anatomy_map": BASE_DIR / "assets" / "maps" / "anatomy_map.json",
    "embriology_map": BASE_DIR / "assets" / "maps" / "embriology_map.json",
    "dr_map": BASE_DIR / "assets" / "maps" / "dr_map.json"
}

pygame.font.init()
font_path = BASE_DIR / "assets" / "fonts" / "font.ttf"
FONTS = {
    "small": pygame.font.Font(font_path, 12) if font_path.exists() else pygame.font.Font(None, 12),
    "medium": pygame.font.Font(font_path, 16) if font_path.exists() else pygame.font.Font(None, 16),
    "large": pygame.font.Font(font_path, 24) if font_path.exists() else pygame.font.Font(None, 24)
}

from gale import frames

TEXTURES = {
    "andrea_idle": pygame.image.load(BASE_DIR / "assets" / "graphics" / "characters" / "andrea_idle.png"),
    "andrea_walking": pygame.image.load(BASE_DIR / "assets" / "graphics" / "characters" / "andrea_walking.png"),
    "valla_horizontal": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "valla_horizontal.png"),
    "valla_vertical": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "valla_vertical.png"),
    "logo": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "logo.jpg"),
    "dr_dead": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "dr_dead.png"),
    "porton": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "porton.png"),
    "puerta": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "puerta.png"),
    "faro": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "faro.png"),
    "arbol1": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "arbol1.png"),
    "arbol2": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "arbol2.png"),
    "toldo": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "toldo.png"),
    "edificio1": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "edificio1.png"),
    "edificio2": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "edificio2.png"),
    "edificio3": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "edificio3.png"),
    "edificio4": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "edificio4.png"),
    "edificio5": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "edificio5.png"),
    "edificio6": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "edificio6.png"),
    "valla_madera": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "valla_madera.png"),
    "arbusto": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "arbusto.png"),
    "carros": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "carro.png"),
    "dulces": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "dulces.png"),
    "marco_superior": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "amphitheater" / "marco_superior.png"),
    "note": pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "note.png")
}

try:
    TEXTURES["simon_bg"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "puzzles" / "bg.png")
    TEXTURES["simon_btn_off"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "puzzles" / "buttons_off.png")
    TEXTURES["simon_btn_on"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "puzzles" / "buttons_on.png")
    TEXTURES["locker_open"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "casillero_abierto.png")
    TEXTURES["keys"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "llaves.png")
    TEXTURES["jezu_animation"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "characters" / "jezu_animation.png")
    TEXTURES["armario_abierto"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "amphitheater" / "armario_abierto.png")
    TEXTURES["armario_cerrado"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "amphitheater" / "armario_cerrado.png")
    TEXTURES["closet_scene"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "closet_scene.jpg")
    TEXTURES["title_img"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "title_img.jpg")
    TEXTURES["marco_oficina"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "office" / "marco_oficina.png")
    TEXTURES["dr_pepe"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "characters" / "dr_pepe.png")
    TEXTURES["dr_mesa"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "office" / "dr_mesa.png")
    TEXTURES["background_anphitheater"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "background_anphitheater.jpg")
    TEXTURES["cartel_pista"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "cartel_pista.png")
    TEXTURES["watch_scene"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "watch_scene.jpg")
    TEXTURES["inv_llaves"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "inventory" / "llaves.png")
    TEXTURES["scene_pills"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "pildoras.png")
    TEXTURES["inv_pills"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "inventory" / "pildoras.png")
    TEXTURES["inv_craneo"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "inventory" / "craneo.png")
    TEXTURES["inv_phone"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "inventory" / "phone_small.png")
    TEXTURES["coat"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "tilesets" / "anatomy" / "coat.png")
    TEXTURES["coat_scene"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "coat_scene.jpg")
    TEXTURES["no_coat_scene"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "no_coat_scene.jpg")
    TEXTURES["inv_coat"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "inventory" / "coat.png")
    TEXTURES["phone_bg"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "phone.png")
    TEXTURES["foto1"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "foto1.jpg")
    TEXTURES["foto2"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "foto2.jpg")
    TEXTURES["fall_andrea"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "characters" / "fall_andrea.png")
    TEXTURES["dr_dead_scene"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / "dr_dead_scene.jpg")
    for i in range(1, 17):
        TEXTURES[f"phone_anim_{i}"] = pygame.image.load(BASE_DIR / "assets" / "graphics" / "scenes" / f"scene_phone ({i}).jpeg")
except Exception as e:
    print(f"Warning: Puzzle assets not found perfectly named. {e}")

TEXTURES["faro_flipped"] = pygame.transform.flip(TEXTURES["faro"], True, False)

#Main character frames
FRAMES = {
    "andrea_idle": frames.generate_frames(TEXTURES["andrea_idle"], 48, 48),
    "andrea_walking": frames.generate_frames(TEXTURES["andrea_walking"], 48, 48),
    "fall_andrea": frames.generate_frames(TEXTURES["fall_andrea"], 48, 48),
    "jezu_animation": frames.generate_frames(TEXTURES["jezu_animation"], 48, 48)
}

SOUNDS = {}
loud_bang_path = BASE_DIR / "assets" / "sounds" / "loud_bang_short.wav"
if loud_bang_path.exists():
    try:
        SOUNDS["loud_bang"] = pygame.mixer.Sound(str(loud_bang_path))
    except:
        pass

ladrando_path = BASE_DIR / "assets" / "sounds" / "ladrando.wav"
if ladrando_path.exists():
    try:
        SOUNDS["ladrando"] = pygame.mixer.Sound(str(ladrando_path))
    except:
        pass

boton_path = BASE_DIR / "assets" / "sounds" / "boton.wav"
if boton_path.exists():
    try:
        SOUNDS["boton"] = pygame.mixer.Sound(str(boton_path))
    except:
        pass

