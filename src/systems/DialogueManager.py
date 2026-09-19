class DialogueManager:
    def __init__(self):
        self.dialogues = {
            "jake_interact": [
                ("", "(Andrea acaricia al perro)")
            ],
            "arrive_office": [
                ("Teacher", "You're late. I need a favor from you."),
                ("Player", "I'm sorry. What do you need?"),
                ("Teacher", "Go to the amphitheater and bring me the skull.")
            ],
            "arrive_amphitheater": [
                ("Player", "It's so dark and cold in here."),
                ("Player", "I better store my things before searching.")
            ],
            "store_things": [
                ("Player", "Things are stored. Now to find that skull.")
            ],
            "get_skull": [
                ("Player", "Found the skull. This place gives me the creeps."),
                ("Player", "I should bring this back to the teacher quickly.")
            ],
            "deliver_skull": [
                ("Teacher", "Good. Leave it on the desk."),
                ("Teacher", "One more thing. Go to the Anatomy lab, crack the safe, and bring my coat.")
            ],
            "arrive_anatomy": [
                ("Player", "The Anatomy lab. The safe should be around here somewhere.")
            ],
            "crack_safe": [
                ("Player", "The safe is open. There's the coat.")
            ],
            "get_coat": [
                ("Player", "I have the coat. Let's get out of here before something bad happens.")
            ]
        }
    
    def get_dialogue(self, dialogue_id):
        
    
        return self.dialogues.get(dialogue_id, [("System", "Dialogue not found.")])
