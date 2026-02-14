"""
Test script for high-accuracy transcription.
Uses the HIGH_ACCURACY preset for best results.
"""

from src.transcribe import transcribe_audio
from src.presets import get_preset, print_presets
from pathlib import Path
import sys


def main():
    audio_path = Path("audio/lagaleiti-5.m4a")

    if not audio_path.exists():
        print(f"ERROR: Audio file not found: {audio_path}")
        print("Please copy: cp 'path/to/Lágaleiti 5.m4a' audio/lagaleiti-5.m4a")
        return

    # Allow preset selection from command line
    preset_name = "high_accuracy"
    if len(sys.argv) > 1:
        preset_name = sys.argv[1].lower()

    try:
        preset = get_preset(preset_name)
    except ValueError as e:
        print(f"Error: {e}")
        print_presets()
        return

    print(f"Using preset: {preset_name.upper()}")
    print(f"Settings: {preset}")
    print("=" * 60)
    print("\nStarting HIGH ACCURACY transcription...")
    print("This will be slower but more accurate than the default settings.")
    print("=" * 60)

    result = transcribe_audio(
        audio_path=str(audio_path),
        **preset
    )

    print("\n" + "=" * 60)
    print("Transcription completed!")
    print("=" * 60)

    # Show additional analysis
    print("\n--- Accuracy Indicators ---")
    metadata = result["metadata"]
    print(f"Language confidence: {metadata['language_probability']:.2%}")
    print(f"Average segment length: {len(result['segments']) / metadata['audio_duration']:.2f} segments/second")
    print(f"\nTotal segments: {len(result['segments'])}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        print("Usage: python test_accuracy.py [preset]")
        print("\nAvailable presets:")
        print("  speed          - Fastest (~3-5x real-time)")
        print("  balanced       - Default (~5-8x real-time)")
        print("  high_accuracy  - High accuracy (~10-15x real-time) [DEFAULT]")
        print("  ultra_accuracy - Maximum accuracy (~15-20x real-time)")
        print("  precise        - For catching short/fast words like 'að' (~12-18x real-time)")
        print("\nExample:")
        print("  python test_accuracy.py precise     # Catch short words")
        print("  python test_accuracy.py ultra_accuracy")
        sys.exit(0)

    main()
