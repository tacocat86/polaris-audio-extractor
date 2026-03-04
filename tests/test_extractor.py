from pathlib import Path
from audio_extractor.extractor import resolve_output_path, build_ffmpeg_cmd, extract


# --- Path resolution tests ---

def test_resolve_output_same_dir():
    p = Path("/videos/movie.mkv")
    result = resolve_output_path(p, None, "mp3")
    assert result == Path("/videos/movie.mp3")


def test_resolve_output_custom_dir():
    p = Path("/videos/movie.mkv")
    result = resolve_output_path(p, Path("/audio"), "mp3")
    assert result == Path("/audio/movie.mp3")


def test_resolve_output_format():
    p = Path("/videos/movie.mkv")
    result = resolve_output_path(p, None, "flac")
    assert result.suffix == ".flac"


# --- ffmpeg command builder tests ---

def test_build_cmd_basic():
    cmd = build_ffmpeg_cmd(Path("/in/a.mkv"), Path("/out/a.mp3"))
    assert "ffmpeg" in cmd
    assert "-vn" in cmd
    assert "-y" not in cmd


def test_build_cmd_overwrite():
    cmd = build_ffmpeg_cmd(Path("/in/a.mkv"), Path("/out/a.mp3"), overwrite=True)
    assert "-y" in cmd


def test_build_cmd_codec_bitrate():
    cmd = build_ffmpeg_cmd(
        Path("/in/a.mkv"), Path("/out/a.mp3"),
        codec="aac", bitrate="128k"
    )
    assert "aac" in cmd
    assert "128k" in cmd


# --- Dry-run test ---

def test_dry_run_no_file_created(tmp_path, capsys):
    # Create a fake input file so path resolution works
    fake_input = tmp_path / "fake.mkv"
    fake_input.write_bytes(b"")

    extract(fake_input, output_dir=tmp_path, fmt="mp3", dry_run=True)

    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out

    # No real output file should be created
    assert not (tmp_path / "fake.mp3").exists()


# --- Skip-if-exists test ---

def test_skip_if_exists(tmp_path, capsys):
    fake_input = tmp_path / "fake.mkv"
    fake_input.write_bytes(b"")
    existing_output = tmp_path / "fake.mp3"
    existing_output.write_bytes(b"already here")

    extract(fake_input, output_dir=tmp_path, fmt="mp3", overwrite=False)

    captured = capsys.readouterr()
    assert "Skipping" in captured.out
