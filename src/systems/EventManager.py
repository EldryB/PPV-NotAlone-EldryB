from src.states.ui.DialogueState import DialogueState

class EventManager:
    def __init__(self, play_state):
        self.play_state = play_state
        self.quest_manager = play_state.quest_manager
        self.ui_stack = play_state.ui_stack
        
    def trigger_event(self, event_key):
        if event_key == "jezu_intro":
            self._handle_jezu_intro()
            return True
        elif event_key == "dr_pepe_intro":
            self._handle_dr_pepe_intro()
            return True
            
        return False
        
    def _handle_jezu_intro(self):
        if getattr(self.play_state, "jezu_talked", False):
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["Suerte con el Doctor!"], speaker="Jezu"))
            return
            
        self.play_state.jezu_talked = True
        
        def j_end():
            pass
        def a_reply2():
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["Gracias, me voy entonces, el Doctor me esta esperando"], speaker="Andrea", on_close=j_end))
        def j_reply():
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["Me puedes enviar un mensaje a lo que termines, yo te llevo"], speaker="Jezu", on_close=a_reply2))
        def a_reply1():
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["Si, es tan tarde que no queria venir, ya estaba lista para ir a la cama", "No creo que cuando termine mis tareas logre alcanzar transporte"], speaker="Andrea", on_close=j_reply))
        
        self.ui_stack.push(DialogueState(
            self.ui_stack, 
            lines=["Hola!! Tambien te ha llamado el Dr. Pepe ?"], 
            speaker="Jezu", 
            on_close=a_reply1
        ))

    def _handle_dr_pepe_intro(self):
        has_coat = hasattr(self.play_state, 'inventory') and self.play_state.inventory and self.play_state.inventory.has_item("inv_coat")
        if has_coat:
            def d_end():
                pass # self.quest_manager.notify("return_coat")
                if hasattr(self.play_state, 'inventory'):
                    self.play_state.inventory.remove_item("inv_coat")
                self.play_state.delivered_coat = True # Bandera para activar evento de salida
            def a1():
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["Nos vemos luego Dr. Pepe, Feliz noche"], speaker="Andrea", on_close=d_end))
            def dr3():
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["Es broma, ya te puedes retirar"], speaker="Dr. Pepe", on_close=a1))
            def dr2():
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["Puedes irte a tu casa, pero solo si los fantasmas te lo permiten!! JA JA"], speaker="Dr. Pepe", on_close=dr3))
            
            self.ui_stack.push(DialogueState(
                self.ui_stack,
                lines=["Bueno, creo que eso seria todo por hoy"],
                speaker="Dr. Pepe",
                on_close=dr2
            ))
            return
            
        has_skull = hasattr(self.play_state, 'inventory') and self.play_state.inventory and self.play_state.inventory.has_item("inv_craneo")
        if has_skull:
            def d6():
                self.quest_manager.notify("return_dr_pepe")
                if hasattr(self.play_state, 'inventory'):
                    self.play_state.inventory.remove_item("inv_craneo")
                
            def d5():
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["(Asiente con la cabeza)"], speaker="Andrea", on_close=d6))
            def d4():
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["JA JA!! Es solo un chiste, no te creas todo lo que te dicen!!"], speaker="Dr. Pepe", on_close=d5))
            def d3():
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["Pero ten cuidado, dicen que ahi espantan de noche"], speaker="Dr. Pepe", on_close=d4))
            def d2():
                self.ui_stack.push(DialogueState(self.ui_stack, lines=["Necesito que vayas al edifico de anatomia y busques mi bata"], speaker="Dr. Pepe", on_close=d3))
            
            d1_lines = [
                "Muy bien, eso ya casi estamos listos",
                "Solamente te voy a pedir un ultimo favor"
            ]
            self.ui_stack.push(DialogueState(self.ui_stack, lines=d1_lines, speaker="Dr. Pepe", on_close=d2))
            return
            
        def on_d4_close():
            self.quest_manager.notify("talk_dr_pepe") # self.quest_manager.notify("talk_dr_pepe")
            
        def d4():
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["Ok Doctor, voy para alla."], speaker="Andrea", on_close=on_d4_close))
        def d3():
            d3_lines = [
                "Ya Jezu se encargo de la mayoria de tareas, pero no hemos conseguido el craneo de la primera practica...",
                "Debe estar en alguna parte del anfiteatro..."
            ]
            self.ui_stack.push(DialogueState(self.ui_stack, lines=d3_lines, speaker="Dr. Pepe", on_close=d4))
        def d2():
            self.ui_stack.push(DialogueState(self.ui_stack, lines=["Buenas noches Dr. En que necesita ayuda?"], speaker="Andrea", on_close=d3))
            
        d1_lines = [
            "Al fin llegas!! MaAna llegan los nuevos ingresos a la facultad...",
            "Y necesito preparar todo.."
        ]
        self.ui_stack.push(DialogueState(self.ui_stack, lines=d1_lines, speaker="Dr. Pepe", on_close=d2))
