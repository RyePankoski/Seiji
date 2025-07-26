import pygame
from pygame import mixer


class SoundManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not SoundManager._initialized:
            self.sounds = {
                'place': pygame.mixer.Sound("Sounds/place_sound.mp3"),
                'slide': pygame.mixer.Sound("Sounds/slide_sound.mp3"),
                'pick_up': pygame.mixer.Sound("Sounds/pick_up.mp3"),
                'capture': pygame.mixer.Sound("Sounds/capture.mp3"),
                'promote': pygame.mixer.Sound("Sounds/promote.mp3"),
                'endgame': pygame.mixer.Sound("Sounds/endgame.mp3"),
                'select_piece': pygame.mixer.Sound("Sounds/advisor.mp3"),
                'de_select': pygame.mixer.Sound("Sounds/de-select.mp3"),
                'enemy_select': pygame.mixer.Sound("Sounds/enemy_select.mp3"),
                'rematch': pygame.mixer.Sound("Sounds/rematch.mp3"),
                'to_menu': pygame.mixer.Sound("Sounds/to_menu.mp3")
            }
            self.current_music = None
            SoundManager._initialized = True

    @classmethod
    def play_sound(cls, sound_name):
        instance = cls()
        if sound_name in instance.sounds:
            instance.sounds[sound_name].play()
        else:
            print(f"Warning: Sound '{sound_name}' not found")

    @classmethod
    def handle_music_transition(cls, new_track, fadeout_time=1000):
        instance = cls()
        if new_track == instance.current_music:  # Skip if same track
            return
        try:
            mixer.music.fadeout(fadeout_time)
            mixer.music.load(new_track)
            mixer.music.play(-1)
            instance.current_music = new_track
        except pygame.error as e:
            print(f"Could not load or play music file: {e}")

    @classmethod
    def stop_music(cls):
        instance = cls()
        mixer.music.stop()
        instance.current_music = None

    @classmethod
    def set_music_volume(cls, volume):
        mixer.music.set_volume(volume)

    @classmethod
    def set_sound_volume(cls, volume):
        instance = cls()
        for sound in instance.sounds.values():
            sound.set_volume(volume)
