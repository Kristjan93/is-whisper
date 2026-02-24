#!/usr/bin/env python
"""
Transcribe Icelandic audio using faster-whisper.
Usage: python transcribe.py <audio_file> [fast|balanced|accurate] [--llm] [--save] [--verbose]
"""

import sys
import time
import json
import os
from pathlib import Path
from faster_whisper import WhisperModel

MODEL = "language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2"

MODES = {
    "fast":     {"beam_size": 1,  "vad_filter": True},
    "balanced": {"beam_size": 5,  "vad_filter": True},
    "accurate": {"beam_size": 10, "vad_filter": False},
}

# ANSI colors
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"


def transcribe(audio_path, beam_size=5, vad_filter=True, verbose=False):
    """Transcribe Icelandic audio. Returns dict with full_text, segments, metadata."""
    print(f"{DIM}Loading model...{RESET}", end="", file=sys.stderr, flush=True)
    t0 = time.time()
    model = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    model_load_time = time.time() - t0
    print(f" {model_load_time:.1f}s", file=sys.stderr)

    print(f"{DIM}Transcribing...{RESET}", end="", file=sys.stderr, flush=True)
    t0 = time.time()

    segments, info = model.transcribe(
        audio_path,
        beam_size=beam_size,
        language="is",
        temperature=0.0,
        vad_filter=vad_filter,
        vad_parameters=dict(min_silence_duration_ms=500) if vad_filter else None,
    )

    texts = []
    details = []

    for seg in segments:
        text = seg.text.strip()
        # Skip hallucinated micro-segments
        if (seg.end - seg.start) < 0.3 and len(text) <= 3:
            continue
        if verbose:
            print(f"  {DIM}{seg.start:.2f}s -> {seg.end:.2f}s{RESET}  {text}", file=sys.stderr)
        texts.append(text)
        details.append({"start": seg.start, "end": seg.end, "text": text})

    transcription_time = time.time() - t0
    print(f" {transcription_time:.1f}s", file=sys.stderr)

    return {
        "full_text": " ".join(texts),
        "segments": details,
        "metadata": {
            "audio_duration": info.duration,
            "language": info.language,
            "language_probability": info.language_probability,
            "model_load_time": model_load_time,
            "transcription_time": transcription_time,
            "audio_file": str(Path(audio_path).resolve()),
        },
    }


def save_result(result, audio_path, corrected_text=None):
    """Save transcript files to transcripts/ directory."""
    out = Path("transcripts")
    out.mkdir(exist_ok=True)
    stem = Path(audio_path).stem

    (out / f"{stem}_transcript.txt").write_text(result["full_text"], encoding="utf-8")
    with open(out / f"{stem}_transcript.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"{GREEN}Saved:{RESET} transcripts/{stem}_transcript.txt", file=sys.stderr)
    print(f"{GREEN}Saved:{RESET} transcripts/{stem}_transcript.json", file=sys.stderr)

    if corrected_text is not None:
        (out / f"{stem}_corrected.txt").write_text(corrected_text, encoding="utf-8")
        print(f"{GREEN}Saved:{RESET} transcripts/{stem}_corrected.txt", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(f"{BOLD}Usage:{RESET} python transcribe.py <audio_file> [mode] [options]")
        print()
        print(f"{BOLD}Modes:{RESET}")
        print(f"  fast       {DIM}beam_size=1, fastest{RESET}")
        print(f"  balanced   {DIM}beam_size=5, default{RESET}")
        print(f"  accurate   {DIM}beam_size=10, best quality{RESET}")
        print()
        print(f"{BOLD}Options:{RESET}")
        print(f"  --llm, -l      {DIM}Fix punctuation/grammar with Google Gemini{RESET}")
        print(f"  --save, -s     {DIM}Save output to transcripts/ directory{RESET}")
        print(f"  --verbose, -v  {DIM}Show timestamps, timing, and progress{RESET}")
        print()
        print(f"{BOLD}Examples:{RESET}")
        print(f"  python transcribe.py audio/sample.m4a")
        print(f"  python transcribe.py audio/sample.m4a fast --llm")
        print(f"  python transcribe.py audio/sample.m4a --llm --save -v")
        sys.exit(0)

    audio_path = sys.argv[1]
    if not Path(audio_path).exists():
        print(f"{RED}Error:{RESET} File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    # Parse mode (optional positional arg, must come right after audio file)
    mode = "balanced"
    flags_start = 2
    if len(sys.argv) > 2 and not sys.argv[2].startswith("-"):
        if sys.argv[2] in MODES:
            mode = sys.argv[2]
            flags_start = 3
        else:
            print(f"{RED}Error:{RESET} Invalid mode '{sys.argv[2]}'. Must be one of: fast, balanced, accurate", file=sys.stderr)
            print(f"Run 'python transcribe.py --help' for usage.", file=sys.stderr)
            sys.exit(1)

    # Parse flags
    known_flags = {"--llm", "-l", "--save", "-s", "--verbose", "-v"}
    flags = sys.argv[flags_start:]
    for flag in flags:
        if flag not in known_flags:
            print(f"{RED}Error:{RESET} Unknown argument '{flag}'", file=sys.stderr)
            print(f"Run 'python transcribe.py --help' for usage.", file=sys.stderr)
            sys.exit(1)

    use_llm = "--llm" in flags or "-l" in flags
    save = "--save" in flags or "-s" in flags
    verbose = "--verbose" in flags or "-v" in flags

    result = transcribe(audio_path=audio_path, verbose=verbose, **MODES[mode])
    text = result["full_text"]

    corrected_text = None
    if use_llm:
        from correction import correct_icelandic

        print(f"{DIM}Correcting with Gemini...{RESET}", end="", file=sys.stderr, flush=True)
        t0 = time.time()
        corrected_text = correct_icelandic(text, verbose=verbose)
        print(f" {time.time() - t0:.1f}s", file=sys.stderr)
        text = corrected_text

    print(text)

    if save:
        save_result(result, audio_path, corrected_text)
