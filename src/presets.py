"""
Transcription presets for different accuracy/speed trade-offs.
"""

# SPEED MODE: Fastest processing, good accuracy (~3-5x real-time)
SPEED = {
    "beam_size": 1,
    "best_of": 1,
    "temperature": 0.0,
    "vad_filter": True,
    "condition_on_previous_text": False,
    "word_timestamps": False,
}

# BALANCED MODE: Good balance (~5-8x real-time) - DEFAULT
BALANCED = {
    "beam_size": 5,
    "best_of": 5,
    "temperature": 0.0,
    "vad_filter": True,
    "condition_on_previous_text": True,
    "word_timestamps": False,
}

# HIGH ACCURACY MODE: Maximum accuracy (~10-15x real-time)
HIGH_ACCURACY = {
    "beam_size": 10,
    "best_of": 5,
    "temperature": 0.0,
    "vad_filter": False,           # Don't skip any audio
    "condition_on_previous_text": True,
    "word_timestamps": True,       # Force word-level precision
}

# ULTRA ACCURACY MODE: Best possible accuracy (~15-20x real-time)
# Use for critical transcriptions where accuracy > speed
ULTRA_ACCURACY = {
    "beam_size": 15,
    "best_of": 8,
    "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],  # Temperature fallback
    "vad_filter": False,
    "condition_on_previous_text": True,
    "word_timestamps": True,       # Forces more granular analysis
}

# PRECISE MODE: Specifically for catching short/fast words like "að"
# Optimized for Icelandic function words
PRECISE = {
    "beam_size": 12,
    "best_of": 6,
    "temperature": 0.0,
    "vad_filter": False,           # Never skip audio
    "condition_on_previous_text": True,
    "word_timestamps": True,       # Word-level analysis
}


def get_preset(name: str = "balanced") -> dict:
    """
    Get transcription preset by name.

    Args:
        name: Preset name ('speed', 'balanced', 'high_accuracy', 'ultra_accuracy', 'precise')

    Returns:
        Dictionary of transcription parameters

    Example:
        >>> from src.transcribe import transcribe_audio
        >>> from src.presets import get_preset
        >>> result = transcribe_audio("audio.m4a", **get_preset("precise"))
    """
    presets = {
        "speed": SPEED,
        "balanced": BALANCED,
        "high_accuracy": HIGH_ACCURACY,
        "ultra_accuracy": ULTRA_ACCURACY,
        "precise": PRECISE,
    }

    preset_name = name.lower()
    if preset_name not in presets:
        raise ValueError(
            f"Unknown preset: {name}. "
            f"Available: {', '.join(presets.keys())}"
        )

    return presets[preset_name].copy()


def print_presets():
    """Print all available presets with their settings."""
    print("\n=== Available Transcription Presets ===\n")

    print("1. SPEED (~3-5x real-time)")
    print(f"   {SPEED}\n")

    print("2. BALANCED (~5-8x real-time) - DEFAULT")
    print(f"   {BALANCED}\n")

    print("3. HIGH_ACCURACY (~10-15x real-time)")
    print(f"   {HIGH_ACCURACY}\n")

    print("4. ULTRA_ACCURACY (~15-20x real-time)")
    print(f"   {ULTRA_ACCURACY}\n")

    print("5. PRECISE (~12-18x real-time) - Best for short/fast words")
    print(f"   {PRECISE}\n")


if __name__ == "__main__":
    print_presets()
