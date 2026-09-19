class PhoneManager:
    def __init__(self):
        self.messages = []
        
    def send_message(self, dialogue_lines=None, image_key=None, is_animated=False, overlay_key=None):
        from src.systems.AudioManager import AudioManager
        AudioManager.play_sfx("notification_short")
        self.messages.append({
            'dialogue': dialogue_lines or [],
            'image': image_key,
            'is_animated': is_animated,
            'overlay_key': overlay_key
        })
        
    def has_messages(self):
        return len(self.messages) > 0
        
    def pop_message(self):
        if self.has_messages():
            return self.messages.pop(0)
        return None
