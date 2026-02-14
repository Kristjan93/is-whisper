"""
LLM-based post-processing for Icelandic transcriptions.
Uses Gemini Flash (free tier) to correct grammar, spelling, and add punctuation.
"""

import google.generativeai as genai
from pathlib import Path


def load_api_key():
    """Load Gemini API key from .gemini_key file"""
    key_file = Path(".gemini_key")
    if not key_file.exists():
        raise FileNotFoundError(
            "\nGemini API key not found!\n"
            "1. Go to https://aistudio.google.com/\n"
            "2. Get your API key\n"
            "3. Save it to .gemini_key file\n"
        )
    return key_file.read_text().strip()


def clean_llm_output(text: str) -> str:
    """
    Clean LLM output to ensure only corrected text is returned.
    Removes markdown formatting, prefixes, and other artifacts.
    """
    # Remove markdown code blocks
    if "```" in text:
        # Extract content between code blocks
        parts = text.split("```")
        # Usually the corrected text is in the middle part
        if len(parts) >= 3:
            text = parts[1].strip()
        else:
            text = text.replace("```", "").strip()

    # Remove common Icelandic prefixes
    icelandic_prefixes = [
        "Leiðréttur texti:",
        "Leiðrétt útgáfa:",
        "Svarið er:",
        "Hér er leiðréttur texti:",
    ]

    # Remove common English prefixes (in case LLM responds in English)
    english_prefixes = [
        "Here's the corrected text:",
        "Here is the corrected text:",
        "Corrected text:",
        "The corrected text is:",
        "Corrected version:",
    ]

    all_prefixes = icelandic_prefixes + english_prefixes

    for prefix in all_prefixes:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
            break

    # Remove leading/trailing quotes if present
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()

    return text.strip()


def correct_icelandic(text: str, verbose: bool = False) -> str:
    """
    Correct Icelandic transcription using Gemini Flash.

    Args:
        text: Raw transcription text from Whisper
        verbose: Print processing information

    Returns:
        Corrected Icelandic text with proper grammar, spelling, and punctuation

    Raises:
        FileNotFoundError: If .gemini_key file not found
        Exception: If API call fails
    """
    if verbose:
        print("Correcting with Gemini Flash...")

    # Load and configure API
    api_key = load_api_key()
    genai.configure(api_key=api_key)

    # Use Gemini 1.5 Flash (fastest, cheapest, free tier)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Minimal Icelandic prompt for token efficiency
    # Written in Icelandic to force Icelandic language mode
    prompt = f"""Leiðrétta eftirfarandi íslenskan texta:
- Laga stafsetningu og málfræði
- Bæta við greinarmerki (kommur, punktar, spurningarmerki)
- Laga há-/lágstafi
- EKKI breyta orðalagi eða merkingu

Texti:
{text}

Skila AÐEINS leiðréttum texta, engum útskýringum."""

    try:
        # Generate with minimal settings to save tokens
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0,  # Deterministic output
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2000,  # Limit output length
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        )

        # Extract and clean the response
        corrected = response.text.strip()
        corrected = clean_llm_output(corrected)

        if verbose:
            print(f"✓ Corrected ({len(corrected)} chars)")
            # Show token usage if available
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                print(f"  Tokens: {usage.prompt_token_count} in, {usage.candidates_token_count} out")

        return corrected

    except Exception as e:
        if verbose:
            print(f"⚠ LLM correction failed: {e}")
            print("  Returning original text")
        return text  # Return original if correction fails
