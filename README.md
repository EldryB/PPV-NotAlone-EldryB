# Not Alone

A top-down 2D psychological horror and puzzle game built in Python using Pygame and the Gale engine. 
Play as Andrea, a medical student navigating the university at night while dealing with her own sanity, cryptic messages, and an unknown stalker.

## Features
- **Exploration & Puzzles**: Explore different university buildings (Amphitheater, Old Anatomy Building, Office, Embryology) and solve various minigames like Simon Says, Visual Memory sequences, Safe cracking, and QTE escape sequences.
- **Sanity System**: Keep track of Andrea's mental state. Errors in puzzles and terrifying events drain sanity, triggering visual hallucinations (screen shake, red tints, dynamic heartbeat sounds) and eventually a game over if it reaches zero. Consume pills to regain sanity.
- **Phone & Messages**: Receive terrifying real-time messages and images from an unknown stalker, complete with audio notifications.
- **Narrative Progression**: A fully functional quest log, interactive NPCs (Dr. Pepe, Jezu, Jake the dog), and a persistent inventory system.

## Requirements
- Python 3.12+
- pygame

## How to Play
1. Install dependencies: pip install pygame
2. Run the game: python main.py
3. Controls:
   - **Arrows / WASD**: Move
   - **E**: Interact
   - **I**: Open Inventory (Use pills or read messages)
   - **Enter / Space**: Confirm / Advance Dialogue
   - **ESC**: Exit Puzzles / Pause Menu

## Version 1.0
This version encompasses the fully playable core loop, including all map transitions, the complete quest sequence, all puzzles, the phone message mechanic, and the sanity survival system.
