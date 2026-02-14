"""
Configuration settings for Icelandic audio transcription.

This module contains all configurable parameters that affect transcription
quality, speed, and resource usage. Each setting is documented with its
purpose and impact on the transcription process.
"""

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

ICELANDIC_MODEL = "language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2"
"""
The HuggingFace model identifier for the fine-tuned Icelandic Whisper model.

**What it does:**
- Specifies which pre-trained model to download and use for transcription
- This model was fine-tuned on 967 hours of Icelandic speech data
- Uses CTranslate2 format for optimized inference speed

**How it affects outcome:**
- Model size: Large model (~3GB) provides best accuracy for Icelandic
- First run: Automatically downloads model from HuggingFace (~3GB download)
- Subsequent runs: Uses cached model (no download needed)
- Accuracy: Fine-tuned specifically for Icelandic, better than base Whisper models
- Speed: CTranslate2 format enables faster inference than standard PyTorch models

**When to change:**
- Only if you want to use a different model variant (e.g., smaller base model)
- Changing this requires re-downloading the new model
"""

# ============================================================================
# HARDWARE CONFIGURATION (M1 CPU Settings)
# ============================================================================

CPU_THREADS = 8
"""
Number of CPU threads to use for model inference.

**What it does:**
- Controls parallel processing during transcription
- Each thread can process different parts of the audio simultaneously
- More threads = better CPU core utilization

**How it affects outcome:**
- Speed: More threads = faster transcription (up to your CPU core limit)
- CPU Usage: Higher thread count uses more CPU resources
- Memory: Minimal impact on memory usage
- Recommended values:
  * M1 (base): 8 threads
  * M1 Pro/Max: 10 threads
  * M1 Ultra: 20 threads
  * Intel Macs: Match to your CPU core count

**When to change:**
- If you have more CPU cores available (M1 Pro/Max/Ultra)
- If you want to reduce CPU usage (lower value = slower but less CPU)
- If transcription is too slow and you have unused CPU capacity
"""

COMPUTE_TYPE = "int8"
"""
Numerical precision used for model computations.

**What it does:**
- Controls how model weights are stored and computed
- "int8" uses 8-bit integers (quantized) instead of full 32-bit floats
- Reduces memory usage and speeds up CPU inference

**How it affects outcome:**
- Memory: Significantly reduces RAM usage (~4x less than float32)
- Speed: Faster inference on CPU (optimized for Apple Silicon)
- Accuracy: Minimal quality loss (~1-2% compared to float32)
- Compatibility: Required for CPU-only inference (no GPU on macOS)

**Available options:**
- "int8": Best for CPU (current setting) - balanced speed/quality
- "int8_float16": Not available on CPU
- "float16": GPU-only, will fail on macOS
- "float32": Highest quality but very slow on CPU

**When to change:**
- DO NOT change on macOS - "int8" is optimal for M1 CPU
- Only change if using GPU (Linux/Windows with NVIDIA)
"""

# ============================================================================
# TRANSCRIPTION QUALITY SETTINGS
# ============================================================================

DEFAULT_BEAM_SIZE = 5
"""
Beam search width for decoding the transcription.

**What it does:**
- Controls how many candidate transcriptions are explored simultaneously
- Higher values = more thorough search through possible transcriptions
- Beam search balances between greedy decoding (fast) and exhaustive search (slow)

**How it affects outcome:**
- Accuracy: Higher values = better transcription quality (fewer errors)
- Speed: Higher values = slower transcription (exponential relationship)
- Quality impact:
  * beam_size=1: Fastest, ~5-10% more errors, good for quick drafts
  * beam_size=5: Balanced (current) - good quality, reasonable speed
  * beam_size=10: High quality, ~2x slower than beam_size=5
  * beam_size=20+: Diminishing returns, very slow

**When to change:**
- Increase (5→10): When accuracy is critical and speed is less important
- Decrease (5→1): When you need faster transcription for quick previews
- For production: Keep at 5 for best balance
- For real-time: Use 1 for fastest results
"""

LANGUAGE_CODE = "is"
"""
Language code for the target transcription language.

**What it does:**
- Forces the model to transcribe in Icelandic
- Prevents automatic language detection
- Ensures consistent Icelandic output

**How it affects outcome:**
- Accuracy: Better results when language is known (no detection errors)
- Speed: Slightly faster (skips language detection step)
- Consistency: Always produces Icelandic, never switches to other languages
- Detection: Model still reports detected language probability in metadata

**When to change:**
- Only if transcribing non-Icelandic audio
- Keep as "is" for all Icelandic content
- Set to None for auto-detection (not recommended for this project)
"""

# ============================================================================
# VOICE ACTIVITY DETECTION (VAD) SETTINGS
# ============================================================================

VAD_ENABLED = True
"""
Enable Voice Activity Detection to skip silent portions of audio.

**What it does:**
- Automatically detects and skips silent/silence-only segments
- Only processes audio segments containing speech
- Reduces processing time by ignoring non-speech audio

**How it affects outcome:**
- Speed: Significantly faster (~30-50% speedup) by skipping silence
- Accuracy: Can improve quality by focusing on speech segments
- Output: Only transcribes actual speech, skips long pauses
- Edge cases: May miss very quiet speech or background noise

**When to change:**
- Set to False: If you need to capture all audio including silence markers
- Set to False: If audio has very quiet speech that might be filtered
- Keep True: For normal speech transcription (recommended)
- Keep True: When audio has long pauses between speech segments
"""

VAD_MIN_SILENCE_MS = 500
"""
Minimum duration of silence (in milliseconds) to be considered a break.

**What it does:**
- Defines how long silence must be before VAD treats it as a break
- Shorter pauses (< 500ms) are still processed as part of speech
- Longer pauses (≥ 500ms) are skipped entirely

**How it affects outcome:**
- Speed: Lower values = more segments processed = slower
- Natural breaks: Higher values = longer pauses required = fewer segments
- Accuracy: Affects how speech is segmented (not transcription quality)
- Output: Controls where transcription segments are split

**When to change:**
- Decrease (500→200): For audio with natural pauses in speech (e.g., "um...")
- Increase (500→1000): For audio with long pauses between speakers/topics
- Current value (500ms): Good default for most speech patterns
- Very low (100ms): May split words incorrectly, slower processing
- Very high (2000ms): May miss natural speech pauses
"""
