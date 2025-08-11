import os
import tempfile
from gtts import gTTS

class GoogleTTS:
    def __init__(self):
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".google_tts")
        os.makedirs(self.cache_dir, exist_ok=True)

    def speak(self, text, lang="en", speed="normal"):
        slow = speed == "slow"
        # Generate unique temp filename
        output_path = os.path.join(self.cache_dir, next(tempfile._get_candidate_names()) + ".mp3")

        try:
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(output_path)

            with open(output_path, "rb") as f:
                audio_bytes = f.read()

            return output_path, audio_bytes

        except Exception as e:
            print(f"[Google TTS Error] {e}")
            raise
