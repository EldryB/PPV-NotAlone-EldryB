import settings

class Inventory:
    def __init__(self, sanity_system): 
        self.pills = settings.PLAYER_START_PILLS 
        self.items = ["inv_llaves", "inv_phone"]
            
        self.sanity_system = sanity_system
        self.pill_restore_amount = 30.0 # Each pill restores 30 sanity

    def add_pills(self, count):
        self.pills += count
        if self.pills > 0 and "inv_pills" not in self.items:
            self.items.append("inv_pills")

    def use_pill(self):
        if self.pills > 0:
            self.pills -= 1
            self.sanity_system.restore(self.pill_restore_amount)
            if self.pills <= 0 and "inv_pills" in self.items:
                self.items.remove("inv_pills")
            return True
        return False

    def has_item(self, item_name):
        return item_name in self.items
        
    def add_item(self, item_name):
        if not self.has_item(item_name):
            self.items.append(item_name)
            
    def remove_item(self, item_name):
        if self.has_item(item_name):
            self.items.remove(item_name)
