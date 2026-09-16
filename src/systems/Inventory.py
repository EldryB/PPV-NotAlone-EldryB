import settings

class Inventory:
    def __init__(self, sanity_system): 
        self.pills = 2 
            
        self.sanity_system = sanity_system
        self.pill_restore_amount = 30.0 # Each pill restores 30 sanity

    def add_pills(self, count):
        self.pills += count

    def use_pill(self):
        if self.pills > 0:
            self.pills -= 1
            self.sanity_system.restore(self.pill_restore_amount)
            return True
        return False
