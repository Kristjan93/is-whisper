from faster_whisper import WhisperModel
import time
from pathlib import Path
import json


def transcribe_audio(
    audio_path: str,
    model_name: str = "language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2",
    output_dir: str = "transcripts",
    beam_size: int = 5,
    language: str = "is",
    best_of: int = 5,
    temperature: float = 0.0,
    condition_on_previous_text: bool = True,
    vad_filter: bool = True,
    word_timestamps: bool = False,
    verbose: bool = True,
):
    """
    Transcribe Icelandic audio using faster-whisper.

    Args:
        audio_path: Path to audio file
        beam_size: 1=fastest, 5=balanced, 10+=accurate
        vad_filter: True=faster (skips silence), False=more complete
        verbose: Show detailed output
    """
    if verbose:
        print(f"Loading model...")

    # M1 CPU Configuration
    model = WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8",
        cpu_threads=8,
        num_workers=1,
    )

    if verbose:
        print(f"Transcribing: {audio_path}")

    start_time = time.time()

    # Transcribe with filtering to avoid hallucinations
    segments, info = model.transcribe(
        audio_path,
        beam_size=beam_size,
        language=language,
        best_of=best_of,
        temperature=temperature,
        condition_on_previous_text=condition_on_previous_text,
        vad_filter=vad_filter,
        vad_parameters=dict(min_silence_duration_ms=500) if vad_filter else None,
        compression_ratio_threshold=2.4,  # Filter repetitions
        log_prob_threshold=-0.8,          # Filter low-confidence (stricter)
        no_speech_threshold=0.6,          # Detect silence
        word_timestamps=word_timestamps,
    )

    # Collect results and filter hallucinations
    transcription_text = []
    segment_details = []

    if verbose:
        print("\n--- Segments ---")

    for segment in segments:
        text = segment.text.strip()
        duration = segment.end - segment.start

        # Skip very short repetitive hallucinations (like "um um um")
        if duration < 0.3 and len(text) <= 3:
            continue

        if verbose:
            print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {text}")

        transcription_text.append(text)

        segment_data = {
            "start": segment.start,
            "end": segment.end,
            "text": text,
        }

        # Add word-level timestamps if enabled
        if word_timestamps and hasattr(segment, 'words') and segment.words:
            # Filter low-probability words (hallucinations)
            segment_data["words"] = [
                {
                    "word": word.word,
                    "start": word.start,
                    "end": word.end,
                    "probability": word.probability,
                }
                for word in segment.words
                if word.probability > 0.1  # Skip <10% confidence
            ]

        segment_details.append(segment_data)

    elapsed_time = time.time() - start_time

    # Build result
    result = {
        "full_text": " ".join(transcription_text),
        "segments": segment_details,
        "metadata": {
            "audio_duration": info.duration,
            "language": info.language,
            "language_probability": info.language_probability,
            "transcription_time": elapsed_time,
            "audio_file": audio_path,
            "model": model_name,
        }
    }

    # Save outputs
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    audio_filename = Path(audio_path).stem

    text_file = output_path / f"{audio_filename}_transcript.txt"
    json_file = output_path / f"{audio_filename}_transcript.json"

    with open(text_file, "w", encoding="utf-8") as f:
        f.write(result["full_text"])

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if verbose:
        print(f"\n--- Summary ---")
        print(f"Duration: {info.duration:.2f}s | Time: {elapsed_time:.2f}s")
        print(f"Saved: {text_file}")

    return result


if __name__ == "__main__":
    # Quick test
    result = transcribe_audio(
        audio_path="audio/lagaleiti-5.m4a",
        beam_size=5,
        vad_filter=True,
    )
    print(f"\n{result['full_text']}")
