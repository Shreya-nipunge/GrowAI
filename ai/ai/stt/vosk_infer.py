import sys
import os
import wave
import json
from vosk import Model, KaldiRecognizer

def transcribe(audio_path, model_path):
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not os.path.isdir(model_path):
        raise FileNotFoundError(f"Model folder not found: {model_path}")

    wf = wave.open(audio_path, "rb")
    # Ensure audio is mono PCM WAV
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise ValueError("Audio file must be WAV format mono PCM.")

    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        print(f"Read {len(data)} bytes")  # Debug print

        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            print("Partial result:", res)  # Debug print
            results.append(res.get('text', ''))
    final_res = json.loads(rec.FinalResult())
    results.append(final_res.get('text', ''))

    return " ".join(results).strip()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python vosk_infer.py <audio_wav_file> <model_path>")
        print("Example: python vosk_infer.py sample.wav models/vosk-model-small-hi-0.22")
        sys.exit(1)

    audio_file = sys.argv[1]
    model_dir = sys.argv[2]

    try:
        text = transcribe(audio_file, model_dir)
        print("\n--- Transcription ---")
        print(text)
    except Exception as e:
        print(f"Error: {e}")
