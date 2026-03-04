# Changelog

All notable changes to polaris-audio-extractor are documented here.

---

## [0.1.0] — 2026-03-03

### Added
- Single-file audio extraction via ffmpeg
- Batch folder processing with progress bar
- Drop-folder scan mode (`--scan`) with user-editable config
- 7 output formats: MP3, AAC, FLAC, WAV, Opus, OGG, M4A
- Format validation with availability check against local ffmpeg
- Dry-run mode (`--dry-run`)
- Skip-if-exists protection and `--overwrite` flag
- Parallel processing via `--workers`
- Rich progress bar and batch summary report
- Plain-text log file output via `--log-file`
- `--recursive` flag for nested folder traversal
- `--list-formats` flag showing codec availability
- `--version` flag
- User config at `~/.config/audio-extractor/config.toml`
- GitHub Actions CI (lint + test on every push)
- 21 unit and integration tests
