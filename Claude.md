# Icelandic Voice-to-Text Project

## Project Purpose
Transcribe Icelandic audio recordings using the fine-tuned Whisper model optimized for Icelandic language processing on Apple Silicon (M1) hardware.

## Key Information

**Model:** `language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2`
- Fine-tuned on 967 hours of Icelandic speech
- CTranslate2 format for faster inference
- ~3GB download on first run

**Hardware:** MacBook Pro M1 2021
- CPU-only (no GPU/CUDA support on macOS)
- Performance: ~5-10x real-time processing speed
- Example: 1 minute audio = 5-10 minutes transcription time

**Python:** 3.12.8 (required for ctranslate2 compatibility)

## Critical Configuration

The project is **M1-specific**. Key settings in `src/transcribe.py`:

```python
model = WhisperModel(
    model_name,
    device="cpu",           # NEVER "cuda" on macOS
    compute_type="int8",    # Memory-optimized for CPU
    cpu_threads=8,          # M1 Pro has 8-10 cores
    num_workers=1,
)
```

**DO NOT** change these settings without understanding performance implications:
- `device="cuda"` will fail (no NVIDIA GPU on macOS)
- `compute_type="float16"` is GPU-only
- `compute_type="int8"` is optimal for M1 CPU

## Project Structure

```
faster-whisper-icelandic/
├── .python-version          # pyenv version lock (3.12.8)
├── requirements.txt         # Dependencies
├── README.md               # User-facing documentation
├── Claude.md               # This file - AI assistant context
├── venv/                   # Virtual environment
├── audio/                  # Input audio files (.m4a, .mp3, .wav)
├── transcripts/            # Output directory (auto-created)
│   ├── {filename}_transcript.txt   # Plain text output
│   └── {filename}_transcript.json  # JSON with metadata
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration constants
│   └── transcribe.py       # Main transcription logic
└── test_run.py             # Quick test runner
```

## Setup & Usage

**Initial Setup:**
```bash
cd /Users/kristjanthorsteinsson/Develop/faster-whisper-icelandic
source venv/bin/activate
# Dependencies already installed via requirements.txt
```

**Run Transcription:**
```bash
python test_run.py
```

**First Run Behavior:**
- Downloads model from HuggingFace (~3GB)
- Cached in `~/.cache/huggingface/hub/`
- Subsequent runs skip download

## Performance Optimization

**Current Settings (Recommended):**
- `beam_size=5` - Balanced accuracy/speed
- `vad_filter=True` - Skips silence (~50% speedup)
- `vad_parameters=dict(min_silence_duration_ms=500)`

**Adjustment Options:**
- Faster (lower quality): `beam_size=1`
- Better quality (slower): `beam_size=10`
- More CPU cores: Adjust `cpu_threads` in `src/transcribe.py` (M1 Max/Ultra)

## Audio Format Support

Via PyAV (includes bundled FFmpeg):
- M4A (Voice Memos default) ✓
- MP3 ✓
- WAV ✓
- FLAC ✓
- OGG ✓

**No separate FFmpeg installation needed.**

## Output Files

For input `audio/example.m4a`, generates:

**1. Plain Text:** `transcripts/example_transcript.txt`
```
Full transcription text here...
```

**2. JSON:** `transcripts/example_transcript.json`
```json
{
  "full_text": "...",
  "segments": [
    {"start": 0.0, "end": 5.2, "text": "..."}
  ],
  "metadata": {
    "audio_duration": 120.5,
    "transcription_time": 850.3,
    "language": "is",
    "language_probability": 0.99
  }
}
```

## Troubleshooting

**Slow Performance:**
- Expected on M1 CPU (5-10x real-time is normal)
- Close other apps to free RAM
- Reduce `beam_size` to 1 for faster processing

**Out of Memory:**
- Close memory-intensive apps
- Use `beam_size=1`
- Transcribe shorter audio segments

**Model Download Fails:**
- Check internet connection
- Model cached in `~/.cache/huggingface/hub/`
- Delete cache and retry if corrupted

**Wrong Language Detected:**
- Model explicitly set to `language="is"` (Icelandic)
- Should auto-detect as Icelandic with high probability

## Development Notes

**When modifying code:**
1. Always activate venv: `source venv/bin/activate`
2. Test with short audio clips first (~30 seconds)
3. Monitor Activity Monitor for memory usage
4. M1-specific settings are critical - don't copy GPU examples

**Adding new audio files:**
- Place in `audio/` directory
- Update `test_run.py` if needed
- Or call directly: `python src/transcribe.py` (modify `__main__` block)

## Dependencies

Core packages (auto-installed):
- `faster-whisper` - Main library
- `ctranslate2` - Inference engine
- `av` (PyAV) - Audio processing
- `huggingface-hub` - Model downloads
- `onnxruntime` - Neural network runtime
- `tokenizers` - Text processing

See `requirements.txt` for version constraints.

## Future Improvements

Potential enhancements:
- Batch processing multiple files
- CLI arguments for audio path, beam size
- Real-time transcription for microphone input
- Timestamp-based subtitle generation (SRT format)
- Speaker diarization (separate speakers)

## References

- **Model:** https://huggingface.co/language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2
- **faster-whisper:** https://github.com/SYSTRAN/faster-whisper
- **CTranslate2:** https://github.com/OpenNMT/CTranslate2
