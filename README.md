# polaris-audio-extractor

Extract audio from video files via ffmpeg — single file, batch folder, or drop-folder scan.

Built as part of the Polaris home media workflow.

---

## Features

- Extract audio from any video file ffmpeg supports
- Batch process entire folders (with optional recursion)
- Drop-folder scan mode (`--scan`) for automated workflows
- 7 output formats: MP3, AAC, FLAC, WAV, Opus, OGG, M4A
- Dry-run mode — preview ffmpeg commands without executing
- Skip-if-exists protection with optional `--overwrite`
- Parallel processing with `--workers`
- Rich progress bar and batch summary report
- Plain-text log file output (`--log-file`)
- User-editable config at `~/.config/audio-extractor/config.toml`

---

## Requirements

- Python 3.10+
- ffmpeg (must be on PATH)

Install ffmpeg on Ubuntu/Debian:
```bash
sudo apt install ffmpeg
```

Install ffmpeg on macOS:
```bash
brew install ffmpeg
```

---

## Installation

**From GitHub:**
```bash
pip install git+https://github.com/tacocat86/polaris-audio-extractor.git
```

**From source:**
```bash
git clone git@github.com:tacocat86/polaris-audio-extractor.git
cd polaris-audio-extractor
pip install -e ".[dev]"
```

---

## Usage

### Single file
```bash
extract-audio video.mp4
extract-audio video.mkv --format flac
extract-audio video.mp4 --output-dir ~/Music
```

### Batch folder
```bash
extract-audio ~/Videos/
extract-audio ~/Videos/ --recursive
extract-audio ~/Videos/ --workers 4 --output-dir ~/Music/extracted
```

### Drop-folder scan
```bash
extract-audio --scan
extract-audio --scan --dry-run
```

### Dry-run
```bash
extract-audio video.mp4 --dry-run
extract-audio ~/Videos/ --dry-run
```

### Format selection
```bash
extract-audio video.mp4 --format aac
extract-audio video.mp4 --format opus --bitrate 128k
extract-audio --list-formats
```

---

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `input` | — | Input video file or folder |
| `-o`, `--output-dir` | Same as input | Output directory |
| `-f`, `--format` | `mp3` | Output audio format |
| `--codec` | From format map | Override ffmpeg audio codec |
| `--bitrate` | From format map | Override audio bitrate |
| `--overwrite` | Off | Overwrite existing output files |
| `--dry-run` | Off | Print commands without executing |
| `--scan` | Off | Scan configured drop folder |
| `--list-formats` | Off | Show all formats and availability |
| `--recursive` | Off | Recurse into subdirectories |
| `--workers` | `1` | Parallel worker count |
| `--log-file` | None | Path to write plain-text log |
| `--version` | — | Show version and exit |

---

## Supported Formats

| Format | Codec | Bitrate | Notes |
|--------|-------|---------|-------|
| mp3 | libmp3lame | 192k | Most compatible |
| aac | aac | 192k | Good for Apple devices |
| flac | flac | — | Lossless |
| wav | pcm_s16le | — | Uncompressed PCM |
| opus | libopus | 128k | Modern lossy, excellent quality |
| ogg | libvorbis | 192k | Open format |
| m4a | aac | 192k | AAC in MPEG-4 container |

Run `extract-audio --list-formats` to check availability on your machine.

---

## Configuration

On first run, a config file is created at:
```
~/.config/audio-extractor/config.toml
```

Default contents:
```toml
[paths]
drop_folder = "~/Videos/inbox"
output_dir = "~/Music/extracted"

[extraction]
formats = ["mp4", "mkv", "avi", "mov"]
audio_format = "mp3"
codec = "libmp3lame"
bitrate = "192k"
```

Edit this file to change the drop folder location or default output format.

---

## Polaris Integration

This tool is part of the Polaris home media server workflow running on Lighthouse (Ubuntu server). Videos dropped into `~/Videos/inbox` are automatically extractable via:
```bash
extract-audio --scan
```

Extracted audio lands in `~/Music/extracted` where it is picked up by Jellyfin and Nextcloud for library indexing.

---

## License

MIT — see [LICENSE](LICENSE)
