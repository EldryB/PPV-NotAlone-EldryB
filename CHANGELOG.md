# CHANGELOG

## Version 1.0.0
### Added
- **Complete Narrative Sequence**: Full 16-step quest tracking system with dynamic objectives.
- **Untimed Exploration**: The Safe Puzzle is now untimed, allowing players to leave the UI (ESC) to freely explore the map for clues.
- **Global Sanity Screen Shake**: A terrifying screen shake effect triggers every 15 seconds when sanity drops below 60%, affecting the entire render pipeline without pausing gameplay.
- **Phone UI Tutorial**: Added a dedicated tutorial popup teaching players how to open the inventory to read text messages when the first message is received.
- **Persistent World States**: Opened closets, unlocked lockers, and acquired items (like the skull and coat) are now fully persistent across map transitions and save files.
- **Audio Overhaul**: BGM tracks, atmospheric noise, footsteps, and dynamic heartbeat sounds linked to the Sanity system.

### Changed
- **Puzzle Instruction UI**: Enlarged all puzzle instruction text boxes to 300x160. Text is now dynamically wrapped to prevent clipping off the 320x180 virtual resolution boundaries.
- **Locker Progression**: Interacting with the locker after the initial Simon Says puzzle accurately transitions into the Visual Memory puzzle for retrieving the keys.
- **Code Cleanliness**: Stripped out all overly verbose, redundant, and Spanish explanatory comments to improve codebase readability.

### Fixed
- Fixed an issue where the Safe puzzle did not properly add the "Craneo" asset to the inventory.
- Fixed a bug where returning to the amphitheater would trigger incorrect "Ya deje mis cosas" dialogue instead of advancing the key-finding puzzle.
- Fixed the phone message order to accurately send Jezu's message after delivering the coat, the unknown stalker's message when leaving the office, and the first photo when realizing the keys are missing.
- Fixed map transitions crashing with an unexpected on_finish keyword argument.
- Eliminated a debug loop that fast-forwarded players directly to the 9th objective on startup.

## Version 0.1
### Añadido
- **Estructura Base del Motor:** Inicialización de la arquitectura del juego utilizando Pygame y la librería de estados Gale.
- **Máquina de Estados Global:** Implementación de pantallas núcleo (TitleState, PlayState, GameOverState, EndingState).
- **Integración con Tiled:** Sistema de parseo para mapas JSON múltiples con gestión de hitboxes.
- **Sistema de Cámara y Y-Sorting:** Movimiento de cámara integrado y algoritmo de profundidad para que los personajes pasen correctamente por detrás y por delante de objetos, edificios y marcos de puertas.
- **Niebla de Guerra y Habitaciones:** Sistema matemático de oscurecimiento (BLEND_RGBA_MIN) que permite ocultar habitaciones no exploradas y hacer transiciones al cruzar puertas.
- **Transiciones Cinemáticas:** Efectos de *Fade-In / Fade-Out* dinámicos con Timer.tween para el cambio de mapas y puzles.
- **Mecánicas del Jugador:** 
  - **Sistema de Cordura (SanitySystem):** Barra de vida mental que produce alteraciones visuales si decae.
  - **Inventario:** Sistema de pastillas consumibles para restaurar cordura.
- **Puzles y Minijuegos:** 
  - **Minijuego "Simon Says":** Acertijo de memoria visual.
  - Generación de grilla interactiva, paleta de colores dinámicos, tiempos de reacción cortos y temporizador de penalización.
  - HUD translúcido de instrucciones del minijuego.
- **Sistema de UI e Interacciones:** Gestor de diálogos flotantes estilo RPG.
