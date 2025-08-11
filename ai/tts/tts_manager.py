"""
tts_manager.py
Manages TTS with Coqui as primary and Google TTS as fallback.
"""

from ai.tts.coqui_tts import speak_coqui
from ai.tts.google_tts import speak_google


def speak_text(text, lang="en", speed="normal"):
    """
    Try Coqui TTS first (offline), then Google TTS (online) if Coqui fails.
    Returns: (audio_path, audio_bytes)
    """
    try:
        return speak_coqui(text, lang=lang, speed=speed)
    except Exception as e:
        print(f"[TTS Manager] Coqui failed, trying Google... ({e})")
        return speak_google(text, lang=lang, speed=speed)


if __name__ == "__main__":
    # Test both TTS methods
    path, _ = speak_text("Hello! This is a test of the TTS system.", lang="en", speed="normal")
    print(f"Audio saved at: {path}")
