# is-whisper

Icelandic speech-to-text using a post-trained Whisper model.

## Setup

Requires **Python 3.9 - 3.12**. The `ctranslate2` engine (used by faster-whisper) ships pre-built binaries for these versions. Python 3.13+ may not work yet.

```bash
python3 --version  # check you have 3.9-3.12

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The model (~3GB) downloads automatically on first run.

For Gemini correction (`--llm`), get an API key from https://aistudio.google.com/ and save it:

```bash
echo "your-api-key" > .gemini_key
```

## Try it

You can go from voice to text in under a minute:

1. Open **Voice Memos** on your Mac (it's already installed)
2. Hit record, say something in Icelandic, stop
3. Right-click the recording → **Share** → **Save to Files** → save it or drag it into the `audio/` folder
4. Run:

```bash
python transcribe.py audio/your-recording.m4a --llm
```

That's it. Your spoken Icelandic comes back as text with punctuation. No account needed, no cloud service, everything runs on your machine.

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
| `--llm`, `-l` | Fix punctuation/grammar with Google Gemini (needs `.gemini_key`) |
| `--save`, `-s` | Save output to `transcripts/` directory |
| `--verbose`, `-v` | Show timestamps, timing, and progress |

### Output

By default, the transcribed text is printed to stdout. With `--save`, files are written to `transcripts/`:

| File | Content |
|------|---------|
| `<name>_transcript.txt` | Plain text |
| `<name>_transcript.json` | Text with timestamps and metadata |
| `<name>_corrected.txt` | Punctuation-fixed text (only with `--llm`) |

## Examples

### Default — just the text

```bash
$ python transcribe.py audio/recording.m4a
þetta er tilraun til þess að sjá hvort þetta virkar ég er að tala á íslensku
```

### With Gemini correction

```bash
$ python transcribe.py audio/recording.m4a --llm
Þetta er tilraun til þess að sjá hvort þetta virkar. Ég er að tala á íslensku.
```

### Verbose mode

```bash
$ python transcribe.py audio/recording.m4a --llm -v
Þetta er tilraun til þess að sjá hvort þetta virkar. Ég er að tala á íslensku.
```

stderr shows progress:

```
Loading model...
Transcribing: audio/recording.m4a
  0.00s -> 4.82s  þetta er tilraun til þess að sjá hvort þetta virkar
  4.82s -> 8.10s  ég er að tala á íslensku
Duration: 8.1s | Time: 42.3s
Fixing punctuation with Gemini...
Corrected (95% confidence): Bætti við greinarmerki og lagaði hástafi.
```

### Save to files

```bash
$ python transcribe.py audio/recording.m4a --llm --save
Þetta er tilraun til þess að sjá hvort þetta virkar. Ég er að tala á íslensku.
```

```
Saved: transcripts/recording_transcript.txt
Saved: transcripts/recording_transcript.json
Saved: transcripts/recording_corrected.txt
```
