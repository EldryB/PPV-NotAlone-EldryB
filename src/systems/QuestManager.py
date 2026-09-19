from gale.quest import QuestLog, Quest, Stage, Objective

class QuestManager:
    def __init__(self):
        self.quest_log = QuestLog()
        
        stages = [
            Stage([Objective("talk_dr_pepe", "Hablar con el Dr. Pepe", target=1)]),
            Stage([Objective("arrive_amphitheater", "Ir al anfiteatro", target=1)]),
            Stage([Objective("store_things", "Guardar tus cosas en el casillero", target=1)]),
            Stage([Objective("get_skull", "Buscar el craneo", target=1)]),
            Stage([Objective("return_dr_pepe", "Llevarle el craneo al Dr. Pepe", target=1)]),
            Stage([Objective("arrive_anatomy", "Ir al edificio Antiguo de Anatomia", target=1)]),
            Stage([Objective("get_coat", "Buscar la bata", target=1)]),
            Stage([Objective("return_coat", "Llevarle la bata al Dr. Pepe", target=1)]),
            Stage([Objective("find_keys", "Buscar mis cosas en el anfiteatro", target=1)]),
            Stage([Objective("find_things_1", "Encuentra tus cosas", target=1)]),
            Stage([Objective("go_office", "Ir a la oficina del Dr Pepe", target=1)]),
            Stage([Objective("find_things_2", "Encuentra tus cosas", target=1)]),
            Stage([Objective("go_anatomy_2", "Ir al Edificio Antiguo de Anatomia", target=1)]),
            Stage([Objective("find_things_3", "Encuentra tus cosas", target=1)]),
            Stage([Objective("go_embryology", "Ir al edificio de Embriologia", target=1)]),
            Stage([Objective("find_things_4", "Encuentra tus cosas", target=1)])
        ]
        
        main_quest = Quest("main_story", "La Noche del Stalker", stages)
        
        self.quest_log.register(main_quest)
        self.quest_log.start("main_story")

    def notify(self, objective_id):
        self.quest_log.notify(objective_id, 1)

    def update(self, dt):
        self.quest_log.update(dt)
        
    def current_objective_text(self):
        quest = self.quest_log._quests.get("main_story")
        if quest and getattr(quest, 'current_stage', None):
            stage = quest.current_stage
            steps = getattr(stage, 'steps', [])
            for obj in steps:
                is_done = obj.is_complete() if callable(getattr(obj, 'is_complete', None)) else getattr(obj, 'is_complete', False)
                if not is_done:
                    return getattr(obj, 'description', getattr(obj, 'title', 'Objetivo activo'))
        return "Objetivos completados"

    @property
    def current_stage_index(self):
        quest = self.quest_log._quests.get("main_story")
        if quest and quest.current in quest.steps:
            return quest.steps.index(quest.current)
        return -1

    @current_stage_index.setter
    def current_stage_index(self, value):
        quest = self.quest_log._quests.get("main_story")
        if quest and 0 <= value < len(quest.steps):
            quest.index = value
            quest.current = quest.steps[value]
            for i in range(value):
                for obj in quest.steps[i].steps:
                    obj.amount = obj.target
        elif quest and value == -1:
            quest.finished = True
