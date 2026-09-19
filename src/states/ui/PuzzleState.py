import pygame
from gale.state import BaseState

class PuzzleState(BaseState):
    def __init__(self, stack, puzzle, inventory):
        self.stack = stack
        self.puzzle = puzzle
        self.inventory = inventory
        
        self.original_on_success = getattr(self.puzzle, 'on_success', None)
        self.puzzle.on_success = self.handle_puzzle_complete

    def handle_puzzle_complete(self, *args, **kwargs):
        # We no longer give pills automatically here. 
        self.stack.pop()
        if self.original_on_success:
            self.original_on_success(*args, **kwargs)

    def update(self, dt):
        if hasattr(self.puzzle, 'update'):
            self.puzzle.update(dt)

    def render(self, surface):
        bg = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 200))
        surface.blit(bg, (0, 0))
        
        if hasattr(self.puzzle, 'render'):
            self.puzzle.render(surface)

    def on_input(self, input_id, input_data):
        if input_data.pressed and input_id == "cancel":
            self.stack.pop()
            return
            
        if hasattr(self.puzzle, 'on_input'):
            self.puzzle.on_input(input_id, input_data)
