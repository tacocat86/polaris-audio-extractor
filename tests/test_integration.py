import pytest
from pathlib import Path
from audio_extractor.extractor import extract

FIXTURE = Path(__file__).parent / "fixtures" / "sample.mp4"


@pytest.mark.skipif(not FIXTURE.exists(), reason="Fixture video not found")
def test_extract_real_file(tmp_path):
    """Integration test: extract real audio from fixture video."""
    output = extract(FIXTURE, output_dir=tmp_path, fmt="mp3")
    assert output.exists()
    assert output.suffix == ".mp3"
    assert output.stat().st_size > 0


@pytest.mark.skipif(not FIXTURE.exists(), reason="Fixture video not found")
def test_extract_flac(tmp_path):
    """Integration test: extract FLAC from fixture video."""
    output = extract(FIXTURE, output_dir=tmp_path, fmt="flac")
    assert output.exists()
    assert output.suffix == ".flac"
    assert output.stat().st_size > 0


@pytest.mark.skipif(not FIXTURE.exists(), reason="Fixture video not found")
def test_skip_if_exists_integration(tmp_path, capsys):
    """Integration test: second run skips existing file."""
    extract(FIXTURE, output_dir=tmp_path, fmt="mp3")
    extract(FIXTURE, output_dir=tmp_path, fmt="mp3", overwrite=False)
    captured = capsys.readouterr()
    assert "Skipping" in captured.out
