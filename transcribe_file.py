#!/usr/bin/env python
"""
Simple CLI to transcribe any audio file.
Usage: python transcribe_file.py <audio_file> [mode]

Modes:
  fast     - Fastest (beam_size=1, ~0.5x real-time)
  balanced - Default (beam_size=5, ~1x real-time)
  accurate - Best quality (beam_size=10, ~2-3x real-time)
"""

import sys
from pathlib import Path
from src.transcribe import transcribe_audio
from src.presets import get_preset
from src.llm_correction import correct_icelandic

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        print("=" * 70)
        print("Icelandic Audio Transcription - faster-whisper")
        print("=" * 70)
        print("\nUSAGE:")
        print("  python transcribe_file.py <audio_file> [mode]")

        print("\nMODES:")
        print("  fast       Fastest processing (~0.5-1x real-time)")
        print("             - beam_size=1, VAD enabled")
        print("             - Good for: Quick drafts, testing")
        print("             - Speed: ~7-10 seconds for 15s audio")
        print()
        print("  balanced   Balanced speed/quality (~1-1.5x real-time) [DEFAULT]")
        print("             - beam_size=5, VAD enabled, catches 'að'")
        print("             - Good for: Daily use, most transcriptions")
        print("             - Speed: ~15-20 seconds for 15s audio")
        print()
        print("  accurate   Best quality (~2-3x real-time)")
        print("             - beam_size=10, VAD disabled, word timestamps")
        print("             - Good for: Important meetings, unclear audio")
        print("             - Speed: ~30-45 seconds for 15s audio")

        print("\nSUPPORTED FORMATS:")
        print("  .m4a, .mp3, .wav, .flac, .ogg, .mp4")

        print("\nOUTPUT:")
        print("  transcripts/<filename>_transcript.txt  - Plain text")
        print("  transcripts/<filename>_transcript.json - With timestamps & metadata")
        print()
        print("POST-PROCESSING:")
        print("  --llm, -l  Use Gemini 2.5 Flash AI for correction (FREE)")
        print("             - Adds punctuation (commas, periods, question marks)")
        print("             - Fixes spelling and grammar")
        print("             - Shows confidence scores and change summaries")
        print("             - Creates: transcripts/<filename>_corrected.txt")

        print("\nEXAMPLES:")
        print("  # Default (balanced mode)")
        print("  python transcribe_file.py audio/recording.m4a")
        print()
        print("  # With AI correction (adds punctuation!)")
        print("  python transcribe_file.py audio/recording.m4a --llm")
        print()
        print("  # Fast mode with AI correction")
        print("  python transcribe_file.py audio/recording.m4a fast --llm")
        print()
        print("  # Best quality")
        print("  python transcribe_file.py ~/Downloads/meeting.mp3 accurate")

        print("\nFIRST RUN:")
        print("  Model (~3GB) will download automatically - takes 2-5 minutes")
        print("  Subsequent runs use cached model (no download)")

        print("\n" + "=" * 70)
        sys.exit(0)

    # Parse arguments
    audio_path = sys.argv[1]

    # Check for --llm flag
    use_llm = "--llm" in sys.argv or "-l" in sys.argv

    # Get mode (skip flags)
    mode = "balanced"
    for arg in sys.argv[2:]:
        if not arg.startswith("-"):
            mode = arg
            break

    if not Path(audio_path).exists():
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    # Map simple mode names to presets
    mode_map = {
        "fast": "speed",
        "balanced": "balanced",
        "accurate": "high_accuracy",
    }

    if mode not in mode_map:
        print(f"Error: Unknown mode '{mode}'")
        print("Valid modes: fast, balanced, accurate")
        sys.exit(1)

    preset_name = mode_map[mode]
    settings = get_preset(preset_name)

    print(f"Transcribing: {audio_path} ({mode} mode)")
    if use_llm:
        print("+ LLM correction enabled (Gemini 2.5 Flash)")
    print("=" * 60)

    # Transcribe
    result = transcribe_audio(
        audio_path=audio_path,
        verbose=True,
        **settings
    )

    audio_filename = Path(audio_path).stem

    # Post-process with LLM if requested
    if use_llm:
        print("\n" + "=" * 60)
        print("Post-processing with Gemini 2.5 Flash AI...")

        try:
            corrected = correct_icelandic(result["full_text"], verbose=True)

            # Save corrected version
            corrected_file = Path("transcripts") / f"{audio_filename}_corrected.txt"
            corrected_file.write_text(corrected, encoding="utf-8")

            print("\n" + "=" * 60)
            print("✓ Transcription complete!")
            print(f"  Original:  transcripts/{audio_filename}_transcript.txt")
            print(f"  Corrected: transcripts/{audio_filename}_corrected.txt")
            print(f"  Metadata:  transcripts/{audio_filename}_transcript.json")

        except FileNotFoundError as e:
            print(f"\n⚠ Error: {e}")
            print("Saved transcription without LLM correction.")
            print(f"  Output: transcripts/{audio_filename}_transcript.txt")
        except Exception as e:
            print(f"\n⚠ LLM correction failed: {e}")
            print("Saved transcription without LLM correction.")
            print(f"  Output: transcripts/{audio_filename}_transcript.txt")
    else:
        print("\n" + "=" * 60)
        print("✓ Done!")
        print(f"  Output: transcripts/{audio_filename}_transcript.txt")
        print(f"  Tip: Use --llm flag to add punctuation and fix grammar")
