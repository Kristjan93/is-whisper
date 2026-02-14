# is-whisper

Icelandic speech-to-text using a post-trained Whisper model.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The model (~3GB) downloads automatically on first run.

For Gemini correction (`--llm`), get an API key from https://aistudio.google.com/ and save it:

```bash
echo "your-api-key" > .gemini_key
```

## Why

There aren't many good open source options for Icelandic speech-to-text. The [whisper-large-icelandic](https://huggingface.co/language-and-voice-lab/whisper-large-icelandic-62640-steps-967h-ct2) model from Language and Voice Lab is post-trained on 967 hours of Icelandic speech and runs locally via [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

It's not great — accuracy is rough and it outputs raw text with no punctuation or capitalization. But it's the best we found for Icelandic without paying for a cloud API.

To compensate, we added an optional Google Gemini step (`--llm`) that takes the raw output and fixes punctuation, capitalization, and grammar. It doesn't fix what the model heard wrong, but it makes the output actually readable.

## Usage

```
python transcribe.py <audio_file> [mode] [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `audio_file` | Path to audio file (M4A, MP3, WAV, FLAC, OGG) |

### Modes

| Mode | beam_size | Description |
|------|-----------|-------------|
| `fast` | 1 | Fastest, less accurate |
| `balanced` | 5 | Default |
| `accurate` | 10 | Slowest, best quality |

### Options

| Flag | Description |
|------|-------------|
| `--llm`, `-l` | Post-process with Google Gemini to add punctuation and fix grammar. Requires `.gemini_key` |
| `--help`, `-h` | Show help |

### Output

All output goes to `transcripts/`:

| File | Content |
|------|---------|
| `<name>_transcript.txt` | Plain text |
| `<name>_transcript.json` | Text with timestamps and metadata |
| `<name>_corrected.txt` | Punctuation-fixed text (only with `--llm`) |

## Examples

**Basic transcription:**

```bash
$ python transcribe.py audio/recording.m4a
Transcribing: audio/recording.m4a (balanced mode)
Loading model...
Transcribing: audio/recording.m4a
[0.00s -> 4.82s] þetta er tilraun til þess að sjá hvort þetta virkar
[4.82s -> 8.10s] ég er að tala á íslensku

Duration: 8.1s | Time: 42.3s
Saved: transcripts/recording_transcript.txt
Done!
```

**Fast mode with Gemini correction:**

```bash
$ python transcribe.py audio/recording.m4a fast --llm
Transcribing: audio/recording.m4a (fast mode)
Loading model...
Transcribing: audio/recording.m4a
[0.00s -> 4.82s] þetta er tilraun til þess að sjá hvort þetta virkar
[4.82s -> 8.10s] ég er að tala á íslensku

Duration: 8.1s | Time: 12.5s
Saved: transcripts/recording_transcript.txt

Fixing punctuation with Gemini...
Correcting with Gemini...
Corrected (95% confidence): Bætti við greinarmerki og lagaði hástafi.
Saved: transcripts/recording_corrected.txt
Done!
```

**Corrected output:**

```
Þetta er tilraun til þess að sjá hvort þetta virkar. Ég er að tala á íslensku.
```
