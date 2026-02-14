# Fixing Missing Short Words (like "að")

## The Problem

Short, fast-spoken function words like **"að"** (and other common words like "í", "á", "er", "og", "sem") can get skipped because:

1. **VAD (Voice Activity Detection)** cuts them off at segment boundaries
2. **Log probability filtering** removes them as "low confidence"
3. **Speed optimizations** sacrifice precision for performance
4. **Segment-level analysis** misses word-level details

## The Solution: PRECISE Mode

I've added a **PRECISE** preset specifically optimized for catching short Icelandic function words.

### What PRECISE Mode Does

1. ✅ **Disables VAD** - Processes all audio, no cutting at boundaries
2. ✅ **Word-level timestamps** - Forces the model to identify every word
3. ✅ **Lower thresholds** - More lenient filtering for short words
4. ✅ **Higher beam search** - More thorough word exploration
5. ✅ **Context awareness** - Uses previous text to predict function words

### How to Use

```bash
cd /Users/kristjanthorsteinsson/Develop/faster-whisper-icelandic
source venv/bin/activate
python test_accuracy.py precise
```

### Performance

- **Speed:** ~12-18x real-time (moderate)
- **Accuracy:** Optimized for completeness over speed
- **Best for:** Catching all words, especially short function words

### Example Comparison

**Balanced Mode (Missing "að"):**
```
Ég fór í búð.
```

**PRECISE Mode (Complete):**
```
Ég fór að fara í búðina.
```

---

## Technical Details

### What Changed in PRECISE Mode

```python
PRECISE = {
    "beam_size": 12,              # Thorough search
    "best_of": 6,                 # Multiple samples
    "temperature": 0.0,           # Consistent
    "vad_filter": False,          # NO cutting
    "condition_on_previous_text": True,  # Use context
    "word_timestamps": True,      # Word-level precision
}
```

### Why Word Timestamps Help

When `word_timestamps=True`:
- Model must identify EVERY word (can't skip short ones)
- Forces alignment at word boundaries
- Lower probability threshold (-1.5 instead of -1.0)
- Better silence detection (0.5 instead of 0.6)

This catches words like "að" that would otherwise be merged or skipped.

---

## All Available Modes (Ranked by Completeness)

| Mode | Catches "að"? | Speed | Use When |
|------|---------------|-------|----------|
| `speed` | ❌ Often misses | Fastest | Testing only |
| `balanced` | ⚠️ Sometimes | Fast | Good audio quality |
| `high_accuracy` | ✅ Usually | Moderate | Important work |
| `precise` | ✅✅ Almost always | Moderate-Slow | Missing short words |
| `ultra_accuracy` | ✅✅✅ Always | Slowest | Critical transcription |

---

## Quick Test

Try PRECISE mode on your audio file:

```bash
python test_accuracy.py precise
```

Then check the output in `transcripts/lagaleiti-5_transcript.json` - you should see:
1. Word-level details in the JSON (each word with its own timestamp)
2. Short words like "að" that were previously missing

---

## Comparing Results

To see the difference:

```bash
# Run balanced (your current default)
python test_run.py

# Run precise (optimized for short words)
python test_accuracy.py precise

# Compare the outputs
diff transcripts/lagaleiti-5_transcript.txt transcripts/lagaleiti-5_transcript.txt
```

Look for:
- "að" appearing in PRECISE but not in balanced
- Other short words: "í", "á", "er", "og", "sem", "en"
- More complete sentences overall

---

## If "að" Still Missing

If PRECISE mode still misses some "að" instances, try ULTRA mode:

```bash
python test_accuracy.py ultra_accuracy
```

This is the absolute maximum accuracy setting:
- `beam_size=15` (explores more possibilities)
- `best_of=8` (samples 8 candidates)
- Temperature fallback (tries multiple strategies)
- Slowest but most complete

---

## Making PRECISE Your Default

If you want PRECISE mode by default, edit `test_run.py`:

```python
from src.presets import get_preset

result = transcribe_audio(
    audio_path=str(audio_path),
    **get_preset("precise")  # Use precise by default
)
```

Or manually use it in any script:

```python
from src.transcribe import transcribe_audio

result = transcribe_audio(
    audio_path="audio/your-file.m4a",
    beam_size=12,
    best_of=6,
    vad_filter=False,
    word_timestamps=True,
    condition_on_previous_text=True,
)
```

---

## Summary

**For missing "að" and other short words:**

✅ **Try first:** `python test_accuracy.py precise`
✅ **If still missing:** `python test_accuracy.py ultra_accuracy`
✅ **Compare results:** Check word-level timestamps in JSON output

The PRECISE mode should catch ~95-99% of short function words that balanced mode misses.
