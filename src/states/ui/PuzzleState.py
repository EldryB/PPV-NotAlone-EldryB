import pygame
from gale.state import BaseState
from gale.ui.manager import UIManager

class PuzzleState(BaseState):
    def __init__(self, stack, puzzle, inventory):
        self.stack = stack
        self.puzzle = puzzle
        self.inventory = inventory
        
        # override the puzzle on_complete
        self.original_on_complete = getattr(self.puzzle, 'on_complete', None)
        self.puzzle.on_complete = self.handle_puzzle_complete

    def handle_puzzle_complete(self, *args, **kwargs):
        # Reward the player
        if self.inventory:
            if hasattr(self.inventory, 'add_pills'):
                self.inventory.add_pills(1)
            else:
                self.inventory.pills = getattr(self.inventory, 'pills', 0) + 1
                
        # call original if exists
        if self.original_on_complete:
            self.original_on_complete(*args, **kwargs)
            
        # Close the puzzle state
        self.stack.pop()

    def update(self, dt):
        if hasattr(self.puzzle, 'update'):
            self.puzzle.update(dt)

    def render(self, surface):
        # Draw a semitransparent dark background
        bg = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 200))
        surface.blit(bg, (0, 0))
        
        if hasattr(self.puzzle, 'render'):
            self.puzzle.render(surface)

    def on_input(self, input_id, input_data):
        if hasattr(self.puzzle, 'on_input'):
            self.puzzle.on_input(input_id, input_data)
            
        if input_data.pressed and input_id == "escape":
            self.stack.pop()
