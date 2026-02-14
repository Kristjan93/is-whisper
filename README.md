# Icelandic Voice-to-Text with faster-whisper

Transcribe Icelandic audio using fine-tuned Whisper model on M1 CPU with multiple accuracy presets.

## Setup
```bash
pyenv local 3.12.8
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quick Start

**Standard transcription (balanced):**
```bash
python test_run.py
```

**High accuracy transcription:**
```bash
python test_accuracy.py high_accuracy
```

**Maximum accuracy (slower):**
```bash
python test_accuracy.py ultra_accuracy
```

## Accuracy Presets

Choose the right balance between speed and accuracy:

| Preset | Accuracy | Speed | Use Case |
|--------|----------|-------|----------|
| `speed` | Good | ~3-5x real-time | Quick drafts, testing |
| `balanced` | Very Good | ~5-8x real-time | Default, daily use |
| `high_accuracy` | Excellent | ~10-15x real-time | Important transcriptions |
| `ultra_accuracy` | Maximum | ~15-20x real-time | Critical accuracy needs |

### Running with Presets

```bash
# Standard (balanced)
python test_run.py

# High accuracy
python test_accuracy.py high_accuracy

# Ultra accuracy (best quality)
python test_accuracy.py ultra_accuracy

# Speed mode (fastest)
python test_accuracy.py speed
```

## Model
- `language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2`
- Fine-tuned on 967 hours of Icelandic speech
- ~3GB download on first run
- Cached in `~/.cache/huggingface/hub/`

## Performance (M1 CPU)

**Balanced mode:** ~5-8x real-time (1 min audio = 5-8 min processing)
**High accuracy:** ~10-15x real-time (1 min audio = 10-15 min processing)
**Ultra accuracy:** ~15-20x real-time (1 min audio = 15-20 min processing)

## Accuracy Improvements

The enhanced version includes:

- **Higher beam search** (`beam_size=10+`) - Explores more possibilities
- **Temperature fallback** - Multiple attempts for uncertain segments
- **Best-of sampling** - Picks best from multiple candidates
- **Compression filtering** - Removes repetitions
- **Log probability filtering** - Filters low-confidence segments
- **Context conditioning** - Uses previous text for better continuity
- **Optional VAD** - Can disable for maximum accuracy (slower)

## LLM Post-Processing (Optional)

Enhance transcriptions with **Gemini 2.5 Flash** AI correction (free tier):

```bash
# Add punctuation and fix grammar
python transcribe_file.py audio/recording.m4a --llm
```

**Features:**
- Adds punctuation (commas, periods, question marks)
- Fixes spelling and grammar
- Corrects capitalization
- Preserves original meaning and wording
- **Structured JSON output** with confidence scores and change summaries

**Output format:**
```json
{
  "corrected_text": "Þetta er leiðréttur texti...",
  "confidence": 0.95,
  "changes_summary": "Bætti við greinarmerki og lagaði hástafi"
}
```

**Setup:**
1. Get API key from https://aistudio.google.com/
2. Save to `.gemini_key` file in project root
3. Use `--llm` flag when transcribing

**Example:**
```bash
# Fast transcription with AI correction
python transcribe_file.py audio/meeting.m4a fast --llm
```

Creates:
- `transcripts/meeting_transcript.txt` - Original
- `transcripts/meeting_corrected.txt` - With punctuation and corrections
- `transcripts/meeting_transcript.json` - Metadata with timestamps
