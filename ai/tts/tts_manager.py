"""
tts_manager.py
Manages TTS with Coqui as primary and Google TTS as fallback.
"""

from ai.tts.coqui_tts import CoquiTTS
from ai.tts.google_tts import GoogleTTS

class TTSManager:
    def __init__(self):
        self.coqui = CoquiTTS()
        self.google = GoogleTTS()

    def speak_text(self, text, lang="en", speed="normal"):
        """
        Try Coqui TTS first (offline), then Google TTS (online) if Coqui fails.
        Returns: (audio_path, audio_bytes)
        """
        try:
            return self.coqui.speak(text, speed=speed)
        except Exception as e:
            print(f"[TTS Manager] Coqui failed, trying Google... ({e})")
            return self.google.speak(text, lang=lang, speed=speed)


if __name__ == "__main__":
    manager = TTSManager()
    path, _ = manager.speak_text("Hello! This is a test of the TTS system.", lang="en", speed="normal")
    print(f"Audio saved at: {path}")
