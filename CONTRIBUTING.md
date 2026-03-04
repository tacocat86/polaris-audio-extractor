# Contributing to polaris-audio-extractor

Thanks for your interest in contributing.

---

## Getting Started
```bash
git clone git@github.com:tacocat86/polaris-audio-extractor.git
cd polaris-audio-extractor
pip install -e ".[dev]"
```

---

## Running Tests
```bash
pytest tests/ -v
```

All tests must pass before submitting a pull request.

---

## Linting

This project uses [ruff](https://docs.astral.sh/ruff/) for linting:
```bash
ruff check .
ruff check . --fix   # auto-fix safe issues
```

CI will reject PRs with lint errors.

---

## Adding a New Format

1. Add an entry to `FORMAT_MAP` in `audio_extractor/formats.py`
2. Verify the codec name matches ffmpeg's codec list (`ffmpeg -codecs`)
3. Add a test in `tests/test_formats.py`
4. Update the formats table in `README.md`

---

## Submitting a Pull Request

- Keep PRs focused — one feature or fix per PR
- Write or update tests for any changed behaviour
- Run `ruff check .` and `pytest tests/ -v` before pushing
- Describe what changed and why in the PR description

---

## Project Structure
```
audio_extractor/
├── __init__.py      # version
├── cli.py           # argument parsing and dispatch
├── extractor.py     # core ffmpeg extraction logic
├── formats.py       # format/codec map and validation
├── scanner.py       # drop-folder scan mode
├── batch.py         # folder batch processing
├── progress.py      # rich progress bar and summary
├── config.py        # user config loading and defaults
└── utils.py         # file discovery and log writing
tests/
├── fixtures/        # sample video for integration tests
├── test_extractor.py
├── test_formats.py
├── test_batch.py
└── test_integration.py
```
