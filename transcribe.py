#!/usr/bin/env python
"""
Transcribe Icelandic audio using faster-whisper.
Usage: python transcribe.py <audio_file> [fast|balanced|accurate] [--llm]
"""

import sys
import time
import json
from pathlib import Path
from faster_whisper import WhisperModel

MODEL = "language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2"

MODES = {
    "fast":     {"beam_size": 1,  "vad_filter": True},
    "balanced": {"beam_size": 5,  "vad_filter": True},
    "accurate": {"beam_size": 10, "vad_filter": False},
}


def transcribe(audio_path, beam_size=5, vad_filter=True, verbose=True):
    """Transcribe Icelandic audio. Returns dict with full_text, segments, metadata."""
    if verbose:
        print("Loading model...")

    model = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=8)

    if verbose:
        print(f"Transcribing: {audio_path}")

    start = time.time()

    segments, info = model.transcribe(
        audio_path,
        beam_size=beam_size,
        language="is",
        best_of=5,
        temperature=0.0,
        condition_on_previous_text=True,
        vad_filter=vad_filter,
        vad_parameters=dict(min_silence_duration_ms=500) if vad_filter else None,
        compression_ratio_threshold=2.4,
        log_prob_threshold=-0.8,
        no_speech_threshold=0.6,
    )

    texts = []
    details = []

    for seg in segments:
        text = seg.text.strip()
        # Skip hallucinated micro-segments
        if (seg.end - seg.start) < 0.3 and len(text) <= 3:
            continue
        if verbose:
            print(f"[{seg.start:.2f}s -> {seg.end:.2f}s] {text}")
        texts.append(text)
        details.append({"start": seg.start, "end": seg.end, "text": text})

    elapsed = time.time() - start

    result = {
        "full_text": " ".join(texts),
        "segments": details,
        "metadata": {
            "audio_duration": info.duration,
            "language": info.language,
            "language_probability": info.language_probability,
            "transcription_time": elapsed,
            "audio_file": audio_path,
        },
    }

    # Save outputs
    out = Path("transcripts")
    out.mkdir(exist_ok=True)
    stem = Path(audio_path).stem

    (out / f"{stem}_transcript.txt").write_text(result["full_text"], encoding="utf-8")
    with open(out / f"{stem}_transcript.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if verbose:
        print(f"\nDuration: {info.duration:.1f}s | Time: {elapsed:.1f}s")
        print(f"Saved: transcripts/{stem}_transcript.txt")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python transcribe.py <audio_file> [fast|balanced|accurate] [--llm]")
        print()
        print("Modes:")
        print("  fast       beam_size=1, fastest")
        print("  balanced   beam_size=5, default")
        print("  accurate   beam_size=10, best quality")
        print()
        print("Options:")
        print("  --llm, -l  Fix punctuation/grammar with Google Gemini (needs .gemini_key)")
        print()
        print("Examples:")
        print("  python transcribe.py audio/recording.m4a")
        print("  python transcribe.py audio/recording.m4a fast --llm")
        sys.exit(0)

    audio_path = sys.argv[1]
    if not Path(audio_path).exists():
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    use_llm = "--llm" in sys.argv or "-l" in sys.argv
    mode = "balanced"
    for arg in sys.argv[2:]:
        if not arg.startswith("-") and arg in MODES:
            mode = arg

    print(f"Transcribing: {audio_path} ({mode} mode)")
    result = transcribe(audio_path=audio_path, verbose=True, **MODES[mode])

    if use_llm:
        from correction import correct_icelandic

        print("\nFixing punctuation with Gemini...")
        try:
            corrected = correct_icelandic(result["full_text"], verbose=True)
            stem = Path(audio_path).stem
            corrected_file = Path("transcripts") / f"{stem}_corrected.txt"
            corrected_file.write_text(corrected, encoding="utf-8")
            print(f"Saved: transcripts/{stem}_corrected.txt")
        except FileNotFoundError as e:
            print(f"Error: {e}")

    print("Done!")
