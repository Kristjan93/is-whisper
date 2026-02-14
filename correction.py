"""Fix punctuation and grammar in Icelandic transcriptions using Google Gemini."""

import sys
from google import genai
from google.genai import types
from pathlib import Path
from pydantic import BaseModel, Field

GREEN = "\033[32m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"


class CorrectionResult(BaseModel):
    corrected_text: str = Field(description="Corrected Icelandic text with punctuation and grammar")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    changes_summary: str = Field(description="Brief summary of changes (in Icelandic)")


def load_api_key():
    key_file = Path(".gemini_key")
    if not key_file.exists():
        raise FileNotFoundError(
            "Gemini API key not found. Save your key to .gemini_key file.\n"
            "Get one at https://aistudio.google.com/"
        )
    return key_file.read_text().strip()


def correct_icelandic(text, verbose=False):
    """Send text to Gemini to fix punctuation and grammar. Returns corrected text."""
    client = genai.Client(api_key=load_api_key())

    prompt = f"""Leiðrétta eftirfarandi íslenskan texta:
- Laga stafsetningu og málfræði
- Bæta við greinarmerki (kommur, punktar, spurningarmerki)
- Laga há-/lágstafi
- EKKI breyta orðalagi eða merkingu

Texti:
{text}

Skila AÐEINS leiðréttum texta, engum útskýringum."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=CorrectionResult,
                safety_settings=[
                    types.SafetySetting(category=cat, threshold="BLOCK_NONE")
                    for cat in [
                        "HARM_CATEGORY_HATE_SPEECH",
                        "HARM_CATEGORY_HARASSMENT",
                        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "HARM_CATEGORY_DANGEROUS_CONTENT",
                    ]
                ],
            ),
        )

        result = response.parsed
        if verbose:
            print(f"{GREEN}Corrected{RESET} {DIM}({result.confidence:.0%} confidence): {result.changes_summary}{RESET}", file=sys.stderr)

        return result.corrected_text

    except Exception as e:
        if verbose:
            print(f"{RED}Correction failed:{RESET} {e}", file=sys.stderr)
        return text
