"""
LLM-based post-processing for Icelandic transcriptions.
Uses Gemini 2.5 Flash (free tier) to correct grammar, spelling, and add punctuation.
"""

from google import genai
from google.genai import types
from pathlib import Path
from pydantic import BaseModel, Field


class IcelandicCorrectionResult(BaseModel):
    """Structured output model for Icelandic text correction."""
    corrected_text: str = Field(
        description="Fully corrected Icelandic text with proper punctuation, grammar, capitalization"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Model's confidence in corrections (0.0-1.0)"
    )
    changes_summary: str = Field(
        description="Brief summary of what was changed (in Icelandic)"
    )


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


def correct_icelandic(text: str, verbose: bool = False) -> str:
    """
    Correct Icelandic transcription using Gemini 2.5 Flash with structured JSON output.

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
        print("Correcting with Gemini 2.5 Flash...")

    # Load API key and create client
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

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
        # Generate with structured output using Pydantic model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,  # Deterministic output
                max_output_tokens=2000,
                response_mime_type='application/json',
                response_schema=IcelandicCorrectionResult,
                safety_settings=[
                    types.SafetySetting(
                        category='HARM_CATEGORY_HATE_SPEECH',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_HARASSMENT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_DANGEROUS_CONTENT',
                        threshold='BLOCK_NONE'
                    ),
                ],
            )
        )

        # Get parsed Pydantic object directly from response
        result = response.parsed

        if verbose:
            print(f"✓ Corrected ({len(result.corrected_text)} chars)")
            print(f"  Confidence: {result.confidence:.2%}")
            print(f"  Changes: {result.changes_summary}")
            # Show token usage if available
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                if hasattr(usage, 'prompt_token_count') and hasattr(usage, 'candidates_token_count'):
                    print(f"  Tokens: {usage.prompt_token_count} in, {usage.candidates_token_count} out")

        return result.corrected_text

    except Exception as e:
        if verbose:
            print(f"⚠ LLM correction failed: {e}")
            print("  Returning original text")
        return text  # Return original if correction fails


def correct_icelandic_detailed(text: str, verbose: bool = False) -> dict:
    """
    Correct Icelandic transcription with full metadata.

    Args:
        text: Raw transcription text from Whisper
        verbose: Print processing information

    Returns:
        Dictionary with:
        - corrected_text: Corrected text
        - confidence: Confidence score (0.0-1.0)
        - changes_summary: Summary of changes in Icelandic

    Raises:
        FileNotFoundError: If .gemini_key file not found
        Exception: If API call fails
    """
    if verbose:
        print("Correcting with Gemini 2.5 Flash...")

    # Load API key and create client
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

    # Minimal Icelandic prompt for token efficiency
    prompt = f"""Leiðrétta eftirfarandi íslenskan texta:
- Laga stafsetningu og málfræði
- Bæta við greinarmerki (kommur, punktar, spurningarmerki)
- Laga há-/lágstafi
- EKKI breyta orðalagi eða merkingu

Texti:
{text}

Skila AÐEINS leiðréttum texta, engum útskýringum."""

    try:
        # Generate with structured output using Pydantic model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,  # Deterministic output
                max_output_tokens=2000,
                response_mime_type='application/json',
                response_schema=IcelandicCorrectionResult,
                safety_settings=[
                    types.SafetySetting(
                        category='HARM_CATEGORY_HATE_SPEECH',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_HARASSMENT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_DANGEROUS_CONTENT',
                        threshold='BLOCK_NONE'
                    ),
                ],
            )
        )

        # Get parsed Pydantic object directly from response
        result = response.parsed

        if verbose:
            print(f"✓ Corrected ({len(result.corrected_text)} chars)")
            print(f"  Confidence: {result.confidence:.2%}")
            print(f"  Changes: {result.changes_summary}")
            # Show token usage if available
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage = response.usage_metadata
                if hasattr(usage, 'prompt_token_count') and hasattr(usage, 'candidates_token_count'):
                    print(f"  Tokens: {usage.prompt_token_count} in, {usage.candidates_token_count} out")

        return {
            "corrected_text": result.corrected_text,
            "confidence": result.confidence,
            "changes_summary": result.changes_summary,
        }

    except Exception as e:
        if verbose:
            print(f"⚠ LLM correction failed: {e}")
            print("  Returning original text")
        return {
            "corrected_text": text,
            "confidence": 0.0,
            "changes_summary": "Leiðrétting mistókst",
        }
