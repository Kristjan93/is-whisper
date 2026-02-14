# is-whisper

## Key Info
- **Model:** `language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2`
- **Hardware:** M1 CPU only — `device="cpu"`, `compute_type="int8"`
- **Python:** 3.12.8

## Files
```
transcribe.py    # CLI + transcription engine
correction.py    # Optional Gemini punctuation/grammar fix
tests/           # pytest tests
```

## Do NOT change
- `device="cpu"` — no GPU on macOS
- `compute_type="int8"` — optimal for M1, float16 is GPU-only

## Usage
```bash
source venv/bin/activate
python transcribe.py audio/file.m4a [fast|balanced|accurate] [--llm]
```
