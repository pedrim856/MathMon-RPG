# MathMon RPG - Sound Generator
# Generates all sounds and music procedurally
import pygame
import math
import array


class SoundGenerator:
    """Generates game sounds and chiptune music procedurally."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if SoundGenerator._initialized:
            return
        SoundGenerator._initialized = True
        self.sounds = {}
        self.music_sounds = {}
        self._current_music = None
        self._enabled = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            self._generate_sounds()
            self._generate_music()
        except Exception:
            self._enabled = False

    def _generate_tone(self, frequency, duration_ms, volume=0.3, wave="square"):
        """Generate a tone as a pygame Sound object."""
        sample_rate = 44100
        n_samples = int(sample_rate * duration_ms / 1000)
        buf = array.array('h', [0] * n_samples)

        for i in range(n_samples):
            t = i / sample_rate
            if wave == "square":
                val = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave == "sine":
                val = math.sin(2 * math.pi * frequency * t)
            elif wave == "triangle":
                val = 2 * abs(2 * (frequency * t - math.floor(frequency * t + 0.5))) - 1
            else:
                val = math.sin(2 * math.pi * frequency * t)

            # Envelope (fade in/out)
            envelope = 1.0
            fade_samples = int(n_samples * 0.1)
            if i < fade_samples:
                envelope = i / max(1, fade_samples)
            elif i > n_samples - fade_samples:
                envelope = (n_samples - i) / max(1, fade_samples)

            buf[i] = int(val * volume * 32767 * envelope)

        return pygame.mixer.Sound(buffer=buf)

    # ─── MUSIC SEQUENCER ─────────────────────────────────────────────

    def _sequencer(self, notes):
        """Render a note list [(freq_hz, duration_ms), ...] into a Sound."""
        sample_rate = 44100
        total_ms = sum(d for _, d in notes)
        n_samples = int(sample_rate * total_ms / 1000)
        buf = array.array('h', [0]) * n_samples

        pos = 0
        for freq, dur in notes:
            n = int(sample_rate * dur / 1000)
            if freq <= 0:  # rest
                pos += n
                continue
            for i in range(n):
                t = i / sample_rate
                # Soft lead voice (sine) with a hint of square for chip feel
                val = 0.7 * math.sin(2 * math.pi * freq * t)
                val += 0.3 * (1 if math.sin(2 * math.pi * freq * t) > 0 else -1)
                # Amplitude envelope
                attack = min(1.0, i / max(1, int(sample_rate * 0.015)))
                release = min(1.0, (n - i) / max(1, int(sample_rate * 0.04)))
                envelope = min(attack, release)
                if pos + i < n_samples:
                    buf[pos + i] = int(val * envelope * 0.13 * 32767)
            pos += n
        return pygame.mixer.Sound(buffer=buf)

    def _generate_music(self):
        """Generate looping chiptune themes."""
        C4, D4, E4, F4, G4, A4, B4 = 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88
        C5, D5, E5, F5, G5, A5 = 523.25, 587.33, 659.25, 698.46, 783.99, 880.00
        C6 = 1046.50

        # Calm menu arpeggio
        menu = [
            (C4, 240), (G4, 240), (A4, 240), (C5, 240),
            (G4, 240), (A4, 240), (C5, 240), (E5, 480),
            (D5, 240), (A4, 240), (B4, 240), (D5, 240),
            (G4, 240), (B4, 240), (D5, 240), (G5, 480),
        ]
        # Bright overworld theme
        overworld = [
            (B4, 180), (E5, 180), (B4, 180), (G4, 180),
            (A4, 360), (B4, 180), (E5, 180), (D5, 360),
            (C5, 180), (E5, 180), (A4, 180), (C5, 180),
            (B4, 360), (D5, 180), (G4, 180), (E4, 360),
        ]
        # Energetic battle loop
        battle = [
            (C5, 120), (E5, 120), (G5, 120), (E5, 120),
            (C5, 120), (E5, 120), (A5, 120), (G5, 120),
            (F5, 120), (A5, 120), (C6, 120), (A5, 120),
            (G5, 120), (E5, 120), (D5, 120), (C5, 240),
        ]

        self.music_sounds["menu"] = self._sequencer(menu)
        self.music_sounds["overworld"] = self._sequencer(overworld)
        self.music_sounds["battle"] = self._sequencer(battle)

    def play_music(self, music_name):
        """Start looping background music."""
        if not self._enabled:
            return
        if self._current_music == music_name:
            return
        self.stop_music()
        sound = self.music_sounds.get(music_name)
        if sound:
            try:
                sound.play(-1)
                self._current_music = music_name
            except Exception:
                pass

    def stop_music(self):
        """Stop any playing background music."""
        if not self._enabled:
            return
        sound = self.music_sounds.get(self._current_music)
        if sound:
            try:
                sound.stop()
            except Exception:
                pass
        self._current_music = None

    # ─── SFX ─────────────────────────────────────────────────────────

    def _generate_sounds(self):
        """Generate all game sounds."""
        try:
            # Menu sounds
            self.sounds["menu_select"] = self._generate_tone(800, 80, 0.2, "square")
            self.sounds["menu_confirm"] = self._generate_tone(1000, 120, 0.2, "square")
            self.sounds["menu_back"] = self._generate_tone(400, 100, 0.2, "square")

            # Battle sounds
            self.sounds["battle_start"] = self._generate_tone(600, 300, 0.25, "square")
            self.sounds["attack_hit"] = self._generate_tone(200, 150, 0.3, "square")
            self.sounds["attack_miss"] = self._generate_tone(150, 200, 0.2, "triangle")

            # Challenge sounds
            self.sounds["correct"] = self._generate_tone(880, 150, 0.25, "sine")
            self.sounds["wrong"] = self._generate_tone(200, 300, 0.25, "square")
            self.sounds["timer_tick"] = self._generate_tone(600, 50, 0.1, "square")
            self.sounds["timer_warning"] = self._generate_tone(900, 80, 0.2, "square")

            # Level up
            self.sounds["level_up"] = self._generate_tone(523, 200, 0.2, "sine")
            self.sounds["evolution"] = self._generate_tone(660, 400, 0.25, "sine")

            # Overworld
            self.sounds["bump"] = self._generate_tone(100, 80, 0.15, "square")
            self.sounds["dialog"] = self._generate_tone(700, 40, 0.1, "square")

            # Victory / defeat
            self.sounds["victory"] = self._generate_tone(784, 300, 0.2, "sine")
            self.sounds["defeat"] = self._generate_tone(220, 500, 0.2, "triangle")
        except Exception:
            self._enabled = False

    def play(self, sound_name):
        """Play a sound by name."""
        if self._enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass