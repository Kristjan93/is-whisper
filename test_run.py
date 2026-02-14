from src.transcribe import transcribe_audio
from pathlib import Path

def main():
    audio_path = Path("audio/lagaleiti-5.m4a")

    if not audio_path.exists():
        print(f"ERROR: Audio file not found: {audio_path}")
        print("Please copy: cp 'path/to/Lágaleiti 5.m4a' audio/lagaleiti-5.m4a")
        return

    print("Starting transcription test...")
    print("=" * 60)

    result = transcribe_audio(audio_path=str(audio_path), beam_size=5)

    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    main()
