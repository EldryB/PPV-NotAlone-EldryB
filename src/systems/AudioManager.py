import pygame
import random
import settings

class AudioManager:
    _instance = None
    
    def __init__(self, play_state=None):
        AudioManager._instance = self
        self.play_state = play_state
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.set_num_channels(32)
        
        # Load all SFX into memory
        self.sfx = {}
        sfx_list = ["loud_bang_short", "nota_short", "notification_short", 
                    "pasos_madera_short", "puerta_short", "vidrio_short", 
                    "respiracion", "voice_boy", "voice_girl", "lost", "horror"]
                    
        for name in sfx_list:
            path = settings.BASE_DIR / 'assets' / 'sounds' / f"{name}.wav"
            if path.exists():
                self.sfx[name] = pygame.mixer.Sound(str(path))
                
        # Dedicated channels
        self.breath_channel = pygame.mixer.Channel(4)
        self.voice_channel = pygame.mixer.Channel(5)
        self.lost_channel = pygame.mixer.Channel(6)
        self.spooky_channel = pygame.mixer.Channel(7)
        
        # Music tracks
        self.songs = []
        for i in range(1, 4):
            path = settings.BASE_DIR / 'assets' / 'sounds' / f"song{i}.wav"
            if path.exists():
                self.songs.append(path)
                
        self.current_song_idx = 0
        self.is_challenge_active = False
        self.challenge_music_path = settings.BASE_DIR / 'assets' / 'sounds' / "sonido_reto.wav"
        
        self.spooky_timer = 0.0
        self.last_spooky_was_wood = False
        
        self.start_bgm()

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def play_sfx(cls, sound_name):
        if cls._instance and sound_name in cls._instance.sfx:
            cls._instance.sfx[sound_name].play()

    def start_bgm(self):
        if not self.songs: return
        try:
            pygame.mixer.music.load(str(self.songs[self.current_song_idx]))
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play()
        except:
            pass

    def play_next_song(self):
        if not self.songs: return
        self.current_song_idx = (self.current_song_idx + 1) % len(self.songs)
        self.start_bgm()

    @classmethod
    def start_challenge_music(cls):
        if cls._instance:
            cls._instance.is_challenge_active = True
            if cls._instance.challenge_music_path.exists():
                try:
                    pygame.mixer.music.load(str(cls._instance.challenge_music_path))
                    pygame.mixer.music.set_volume(0.65)
                    pygame.mixer.music.play(-1)
                except:
                    pass

    @classmethod
    def stop_challenge_music(cls):
        if cls._instance and cls._instance.is_challenge_active:
            cls._instance.is_challenge_active = False
            cls._instance.start_bgm()

    @classmethod
    def start_breath(cls):
        if cls._instance and "respiracion" in cls._instance.sfx:
            sound = cls._instance.sfx["respiracion"]
            sound.set_volume(0.4)
            cls._instance.breath_channel.play(sound, loops=-1)

    @classmethod
    def stop_breath(cls):
        if cls._instance:
            cls._instance.breath_channel.stop()

    @classmethod
    def start_voice(cls, gender="girl"):
        if cls._instance:
            snd_name = "voice_boy" if gender == "boy" else "voice_girl"
            if snd_name in cls._instance.sfx:
                if not cls._instance.voice_channel.get_busy():
                    cls._instance.voice_channel.play(cls._instance.sfx[snd_name], loops=-1)

    @classmethod
    def stop_voice(cls):
        if cls._instance:
            cls._instance.voice_channel.stop()

    @classmethod
    def start_lost(cls):
        if cls._instance and "lost" in cls._instance.sfx:
            pygame.mixer.music.stop()
            if not cls._instance.lost_channel.get_busy():
                cls._instance.lost_channel.play(cls._instance.sfx["lost"], loops=-1)

    @classmethod
    def stop_lost(cls):
        if cls._instance:
            cls._instance.lost_channel.stop()
            cls._instance.start_bgm()

    def update(self, dt):
        if not self.is_challenge_active and not pygame.mixer.music.get_busy():
            self.play_next_song()

        if not self.play_state: return
        
        self.spooky_timer += dt
        if self.spooky_timer >= 15.0:
            self.spooky_timer = 0.0
            
            if hasattr(self.play_state, 'world') and getattr(self.play_state.world, "map_name", "main_map") != "main_map":
                sanity = self.play_state.sanity_system.sanity
                clamped_sanity = max(10.0, min(100.0, sanity))
                
                # prob_percent: 100 -> 3%, 10 -> 65%
                prob_percent = 3.0 + ((65.0 - 3.0) / (10.0 - 100.0)) * (clamped_sanity - 100.0)
                
                if random.random() * 100.0 <= prob_percent:
                    snd_name = "vidrio_short" if self.last_spooky_was_wood else "pasos_madera_short"
                    self.last_spooky_was_wood = not self.last_spooky_was_wood
                    
                    if snd_name in self.sfx:
                        self.spooky_channel.play(self.sfx[snd_name])
