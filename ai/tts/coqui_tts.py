import os
import tempfile
from TTS.api import TTS

class CoquiTTS:
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
        self.model_name = model_name
        self.tts = TTS(model_name, progress_bar=False)

    def speak(self, text, speed="normal"):
        # Map speed param to speed scale Coqui expects
        speed_scale = 1.0
        if speed == "slow":
            speed_scale = 0.8
        elif speed == "fast":
            speed_scale = 1.2

        # Create a unique temp file
        output_path = os.path.join(tempfile.gettempdir(), "coqui_tts_output.wav")

        self.tts.tts_to_file(text=text, file_path=output_path, speed=speed_scale)

        with open(output_path, "rb") as f:
            audio_bytes = f.read()

        return output_path, audio_bytes
