import pygame
import random
from gale.state import BaseState
from gale.text import render_text
from gale.input_handler import InputData
import settings

class GameOverState(BaseState):
    def enter(self, **kwargs) -> None:
        self.frames = []
        base_dir = settings.BASE_DIR / 'assets' / 'graphics' / 'scenes' / 'gameover'
        for i in range(1, 101):
            fname = f"{i:03d}.png"
            path = base_dir / fname
            if path.exists():
                img = pygame.image.load(path).convert_alpha()
                self.frames.append(img)
                
        self.current_frame = 0
        self.timer = 0.0
        self.fps = 10.0
        self.frame_duration = 1.0 / self.fps
        
        self.animation_finished = False
        from src.systems.AudioManager import AudioManager
        AudioManager.start_lost()

    def update(self, dt: float) -> None:
        if not self.animation_finished and self.frames:
            self.timer += dt
            if self.timer >= self.frame_duration:
                self.timer -= self.frame_duration
                self.current_frame += 1
                if self.current_frame >= len(self.frames) - 1:
                    self.current_frame = len(self.frames) - 1
                    self.animation_finished = True

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((0, 0, 0))
        
        if self.frames:
            surface.blit(self.frames[self.current_frame], (0, 0))
            
        pygame.draw.rect(surface, (0, 0, 0), (36 * 16, 19 * 16, 32, 32))
        
        offset_x = random.randint(-2, 2)
        offset_y = random.randint(-2, 2)
        render_text(surface, "GAME OVER", settings.FONTS["large"], settings.VIRTUAL_WIDTH // 2 + offset_x, settings.VIRTUAL_HEIGHT // 4 - 48 + offset_y, (200, 20, 20), center=True)
        
        if self.animation_finished:
            render_text(surface, "Presiona ENTER para volver al menu", settings.FONTS["medium"], settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT - 40, (255, 255, 255), center=True)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.animation_finished and input_id in ("confirm", "return") and input_data.pressed:
            from src.systems.AudioManager import AudioManager
            AudioManager.stop_lost()
            self.state_machine.change("title")
