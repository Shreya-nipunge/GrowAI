import whisper
import sys
import os

def transcribe(audio_path, model_size="base"):
    """
    Transcribe audio file to text using OpenAI Whisper.

    Args:
        audio_path (str): Path to the audio file.
        model_size (str): Whisper model size. Options: tiny, base, small, medium, large

    Returns:
        str: Transcribed text
    """
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Loading Whisper model '{model_size}'...")
    model = whisper.load_model(model_size)

    print(f"Transcribing audio: {audio_path}")
    result = model.transcribe(audio_path)

    return result["text"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python whisper_infer.py <audio_file_path> [model_size]")
        print("Example: python whisper_infer.py sample.wav base")
        sys.exit(1)

    audio_file = sys.argv[1]
    model_size = sys.argv[2] if len(sys.argv) > 2 else "base"

    try:
        text = transcribe(audio_file, model_size)
        print("\n--- Transcription ---")
        print(text)
    except Exception as e:
        print(f"Error: {e}")
