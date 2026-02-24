# is-whisper

## Key Info
- **Model:** `language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2`
- **Hardware:** Any CPU (Mac, Linux, Windows) — `device="cpu"`, `compute_type="int8"`
- **Python:** 3.12

## Files
```
transcribe.py    # CLI + transcription engine
correction.py    # Optional Gemini punctuation/grammar fix
tests/           # pytest tests
```

## Usage
```bash
source venv/bin/activate
python transcribe.py audio/sample.m4a [fast|balanced|accurate] [--llm]
```
