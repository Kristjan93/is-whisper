"""Tests for transcribe.py — the core transcription logic."""

import json
from unittest.mock import patch, MagicMock

from transcribe import transcribe, save_result, MODEL, MODES


def make_segment(start, end, text):
    seg = MagicMock()
    seg.start = start
    seg.end = end
    seg.text = text
    return seg


def make_info(duration=10.0, language="is", language_probability=0.99):
    info = MagicMock()
    info.duration = duration
    info.language = language
    info.language_probability = language_probability
    return info


def mock_whisper(segments, info):
    mock_cls = MagicMock()
    mock_instance = MagicMock()
    mock_instance.transcribe.return_value = (iter(segments), info)
    mock_cls.return_value = mock_instance
    return patch("transcribe.WhisperModel", mock_cls)


# --- Model ---

def test_model_points_to_icelandic():
    assert "icelandic" in MODEL.lower()
    assert "ct2" in MODEL


# --- Modes ---

def test_three_modes_exist():
    assert set(MODES.keys()) == {"fast", "balanced", "accurate"}


def test_beam_sizes_increase_with_quality():
    assert MODES["fast"]["beam_size"] < MODES["balanced"]["beam_size"] < MODES["accurate"]["beam_size"]


def test_accurate_disables_vad():
    assert MODES["accurate"]["vad_filter"] is False
    assert MODES["fast"]["vad_filter"] is True


# --- Output structure ---

def test_result_structure():
    segments = [
        make_segment(0.0, 3.5, "Halló heimur"),
        make_segment(3.5, 7.0, "þetta er prufa"),
    ]
    with mock_whisper(segments, make_info(duration=7.0)):
        result = transcribe("fake.m4a", verbose=False)

    assert result["full_text"] == "Halló heimur þetta er prufa"
    assert len(result["segments"]) == 2
    assert result["segments"][0] == {"start": 0.0, "end": 3.5, "text": "Halló heimur"}
    assert result["metadata"]["language"] == "is"
    assert result["metadata"]["audio_duration"] == 7.0


# --- Hallucination filter ---

def test_filters_short_hallucinated_segments():
    """Segments < 0.3s with <= 3 chars are hallucination noise — skip them."""
    segments = [
        make_segment(0.0, 5.0, "Þetta er rétt"),  # kept
        make_segment(5.0, 5.2, "á"),                # filtered (0.2s, 1 char)
        make_segment(5.2, 5.4, "um"),               # filtered (0.2s, 2 chars)
        make_segment(5.5, 8.0, "halló"),            # kept
        make_segment(8.0, 8.5, "já"),               # kept (0.5s > 0.3s)
    ]
    with mock_whisper(segments, make_info()):
        result = transcribe("fake.m4a", verbose=False)

    assert [s["text"] for s in result["segments"]] == ["Þetta er rétt", "halló", "já"]


# --- Empty audio ---

def test_empty_audio():
    with mock_whisper([], make_info(duration=5.0)):
        result = transcribe("fake.m4a", verbose=False)

    assert result["full_text"] == ""
    assert result["segments"] == []


# --- No files saved by default ---

def test_transcribe_does_not_save_files(monkeypatch, tmp_path):
    """transcribe() should not write any files — saving is opt-in via save_result()."""
    monkeypatch.chdir(tmp_path)
    with mock_whisper([make_segment(0.0, 3.0, "Halló")], make_info(duration=3.0)):
        transcribe("test.m4a", verbose=False)

    assert not (tmp_path / "transcripts").exists()


# --- save_result writes files ---

def test_save_result_creates_files(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    result = {"full_text": "Halló", "segments": [], "metadata": {}}
    save_result(result, "test.m4a")

    assert (tmp_path / "transcripts" / "test_transcript.txt").read_text() == "Halló"
    assert json.loads((tmp_path / "transcripts" / "test_transcript.json").read_text())["full_text"] == "Halló"


def test_save_result_with_correction(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    result = {"full_text": "halló", "segments": [], "metadata": {}}
    save_result(result, "test.m4a", corrected_text="Halló.")

    assert (tmp_path / "transcripts" / "test_corrected.txt").read_text() == "Halló."


# --- Parameters reach the model ---

def test_beam_size_and_vad_passed_through():
    mock_cls = MagicMock()
    mock_inst = MagicMock()
    mock_inst.transcribe.return_value = (iter([]), make_info())
    mock_cls.return_value = mock_inst

    with patch("transcribe.WhisperModel", mock_cls):
        transcribe("fake.m4a", beam_size=10, vad_filter=False, verbose=False)

    kwargs = mock_inst.transcribe.call_args[1]
    assert kwargs["beam_size"] == 10
    assert kwargs["vad_filter"] is False
    assert kwargs["vad_parameters"] is None
    # Removed parameters should not be present
    assert "initial_prompt" not in kwargs
    assert "best_of" not in kwargs
    assert "condition_on_previous_text" not in kwargs
    assert "compression_ratio_threshold" not in kwargs
    assert "log_prob_threshold" not in kwargs
    assert "no_speech_threshold" not in kwargs


def test_vad_params_set_when_enabled():
    mock_cls = MagicMock()
    mock_inst = MagicMock()
    mock_inst.transcribe.return_value = (iter([]), make_info())
    mock_cls.return_value = mock_inst

    with patch("transcribe.WhisperModel", mock_cls):
        transcribe("fake.m4a", vad_filter=True, verbose=False)

    kwargs = mock_inst.transcribe.call_args[1]
    assert kwargs["vad_parameters"] == {"min_silence_duration_ms": 500}
