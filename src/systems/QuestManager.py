from gale.quest import QuestLog, Quest, Stage, Objective

class QuestManager:
    def __init__(self):
        self.quest_log = QuestLog()
        
        # list the missions
        stages = [
            Stage([Objective("arrive_office", "Ve a la oficina del Dr. Pepe", target=1)]),
            Stage([Objective("arrive_amphitheater", "Ve al anfiteatro", target=1)]),
            Stage([Objective("store_things", "Guarda tus cosas en el casillero", target=1)]),
            Stage([Objective("get_skull", "Consigue el cráneo", target=1)]),
            Stage([Objective("deliver_skull", "Entrega el cráneo al Dr. Pepe", target=1)]),
            Stage([Objective("arrive_anatomy", "Ve al edificio de anatomía", target=1)]),
            Stage([Objective("crack_safe", "Descifra el código de la caja fuerte", target=1)]),
            Stage([Objective("get_coat", "Consigue la bata del Dr.", target=1)])
        ]
        
        # Quest receives (id, title, list_of_stages)
        main_quest = Quest("main_story", "La Noche del Stalker", stages)
        
        # regiter and begin the quest
        self.quest_log.register(main_quest)
        self.quest_log.start("main_story")

    def notify(self, objective_id):
        self.quest_log.notify(objective_id, 1)

    def update(self, dt):
        self.quest_log.update(dt)
        
    def current_objective_text(self):
        quest = self.quest_log._quests.get("main_story")
        
        #if mision exist and is active
        if quest and getattr(quest, 'current_stage', None):
            stage = quest.current_stage
            
            # Look for first objetive
            objectives = getattr(stage, 'objectives', [])
            for obj in objectives:
                is_done = obj.is_complete() if callable(getattr(obj, 'is_complete', None)) else getattr(obj, 'is_complete', False)
                if not is_done:
                    return getattr(obj, 'description', getattr(obj, 'title', 'Objetivo activo'))
                    
        return "Objetivos completados"
