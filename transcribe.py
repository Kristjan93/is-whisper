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
    if verbose:
        print(f"{DIM}Loading model...{RESET}", file=sys.stderr)

    model = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=os.cpu_count())

    if verbose:
        print(f"{DIM}Transcribing: {audio_path}{RESET}", file=sys.stderr)

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
            print(f"  {DIM}{seg.start:.2f}s -> {seg.end:.2f}s{RESET}  {text}", file=sys.stderr)
        texts.append(text)
        details.append({"start": seg.start, "end": seg.end, "text": text})

    elapsed = time.time() - start

    if verbose:
        print(f"{DIM}Duration: {info.duration:.1f}s | Time: {elapsed:.1f}s{RESET}", file=sys.stderr)

    return {
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

    if corrected_text:
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
        print(f"  --llm, -l      {DIM}Fix punctuation/grammar with Google Gemini (needs .gemini_key){RESET}")
        print(f"  --save, -s     {DIM}Save output to transcripts/ directory{RESET}")
        print(f"  --verbose, -v  {DIM}Show timestamps, timing, and progress{RESET}")
        print()
        print(f"{BOLD}Examples:{RESET}")
        print(f"  python transcribe.py audio/recording.m4a")
        print(f"  python transcribe.py audio/recording.m4a fast --llm")
        print(f"  python transcribe.py audio/recording.m4a --llm --save -v")
        sys.exit(0)

    audio_path = sys.argv[1]
    if not Path(audio_path).exists():
        print(f"{RED}Error:{RESET} File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[2:]
    use_llm = "--llm" in args or "-l" in args
    save = "--save" in args or "-s" in args
    verbose = "--verbose" in args or "-v" in args

    mode = "balanced"
    for arg in args:
        if not arg.startswith("-") and arg in MODES:
            mode = arg

    result = transcribe(audio_path=audio_path, verbose=verbose, **MODES[mode])
    text = result["full_text"]

    corrected_text = None
    if use_llm:
        from correction import correct_icelandic

        if verbose:
            print(f"{CYAN}Fixing punctuation with Gemini...{RESET}", file=sys.stderr)
        corrected_text = correct_icelandic(text, verbose=verbose)
        text = corrected_text

    print(text)

    if save:
        save_result(result, audio_path, corrected_text)
