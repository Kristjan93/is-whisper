"""Tests for correction.py — Gemini punctuation/grammar fixing."""

from unittest.mock import patch, MagicMock
import pytest

from correction import load_api_key, correct_icelandic, CorrectionResult


# --- API key ---

def test_load_api_key(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".gemini_key").write_text("test-key-123\n")
    assert load_api_key() == "test-key-123"


def test_load_api_key_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="Gemini API key not found"):
        load_api_key()


# --- Pydantic schema ---

def test_valid_correction_result():
    r = CorrectionResult(corrected_text="Halló.", confidence=0.95, changes_summary="Punkt.")
    assert r.corrected_text == "Halló."


def test_rejects_invalid_confidence():
    with pytest.raises(Exception):
        CorrectionResult(corrected_text="x", confidence=1.5, changes_summary="x")
    with pytest.raises(Exception):
        CorrectionResult(corrected_text="x", confidence=-0.1, changes_summary="x")


# --- Correction ---

def test_correction_returns_fixed_text(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".gemini_key").write_text("fake-key")

    mock_response = MagicMock()
    mock_response.parsed = CorrectionResult(
        corrected_text="Halló, heimur.",
        confidence=0.95,
        changes_summary="Bætti við kommu og punkt.",
    )
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("correction.genai.Client", return_value=mock_client):
        assert correct_icelandic("halló heimur") == "Halló, heimur."


def test_api_failure_returns_original(tmp_path, monkeypatch):
    """If Gemini fails, return the original text instead of crashing."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".gemini_key").write_text("fake-key")

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API down")

    with patch("correction.genai.Client", return_value=mock_client):
        assert correct_icelandic("óbreytt texti") == "óbreytt texti"


def test_api_key_reaches_client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".gemini_key").write_text("my-key")

    mock_cls = MagicMock()
    mock_cls.return_value.models.generate_content.side_effect = Exception("stop")

    with patch("correction.genai.Client", mock_cls):
        correct_icelandic("test")

    mock_cls.assert_called_once_with(api_key="my-key")
