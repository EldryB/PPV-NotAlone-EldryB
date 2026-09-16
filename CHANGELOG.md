#CHANGELOG
## Version 0.1
  ### Añadido
  - **Estructura Base del Motor:** Inicialización de la arquitectura del juego utilizando `Pygame` y la librería de estados `Gale`.
  - **Máquina de Estados Global:** Implementación de pantallas núcleo (`TitleState`, `PlayState`, `GameOverState`, `EndingState`).
  - **Integración con Tiled:** Sistema de parseo para mapas JSON múltiples con gestión de hitboxes.
  - **Sistema de Cámara y Y-Sorting:** Movimiento de cámara integrado y algoritmo de profundidad para que los personajes pasen correctamente por detrás y por delante de objetos, edificios y marcos de puertas.
  - **Niebla de Guerra y Habitaciones:** Sistema matemático de oscurecimiento (`BLEND_RGBA_MIN`) que permite ocultar habitaciones no exploradas y hacer transiciones al cruzar puertas.
  - **Transiciones Cinemáticas:** Efectos de *Fade-In / Fade-Out* dinámicos con `Timer.tween` para el cambio de mapas y puzles.
  - **Mecánicas del Jugador:** 
    - **Sistema de Cordura (SanitySystem):** Barra de vida mental que produce alteraciones visuales si decae.
    - **Inventario:** Sistema de pastillas consumibles para restaurar cordura.
  - **Puzles y Minijuegos:** 
    - **Minijuego "Simon Says":** Acertijo de memoria visual.
    - Generación de grilla interactiva, paleta de colores dinámicos, tiempos de reacción cortos y temporizador de penalización.
    - HUD translúcido de instrucciones del minijuego.
  - **Sistema de UI e Interacciones:** Gestor de diálogos flotantes estilo RPG.
