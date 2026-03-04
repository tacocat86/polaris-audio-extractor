import pytest
from unittest.mock import patch
from audio_extractor.renamer import parse_filename, propose_rename


def test_parse_filename_missing_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        parse_filename("Some Artist - Some Title")


def test_propose_rename_no_change_needed(tmp_path, monkeypatch):
    audio_file = tmp_path / "Artist - Title.mp3"
    audio_file.write_bytes(b"")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    with patch("audio_extractor.renamer.parse_filename") as mock_parse:
        mock_parse.return_value = {"artist": "Artist", "title": "Title", "confident": True}
        result = propose_rename(audio_file)
        assert result is None


def test_propose_rename_user_confirms(tmp_path, monkeypatch):
    audio_file = tmp_path / "USSR Aerospace - Simpsonwave 1995.mp3"
    audio_file.write_bytes(b"")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    with patch("audio_extractor.renamer.parse_filename") as mock_parse, \
         patch("builtins.input", return_value="y"):
        mock_parse.return_value = {
            "artist": "USSR Aerospace",
            "title": "Simpsonwave 1995",
            "confident": True
        }
        result = propose_rename(audio_file)
        assert result is not None
        assert result.name == "USSR Aerospace - Simpsonwave 1995.mp3"


def test_propose_rename_user_declines(tmp_path, monkeypatch):
    audio_file = tmp_path / "messy filename.mp3"
    audio_file.write_bytes(b"")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    with patch("audio_extractor.renamer.parse_filename") as mock_parse, \
         patch("builtins.input", return_value="n"):
        mock_parse.return_value = {"artist": "Some Artist", "title": "Some Title", "confident": False}
        result = propose_rename(audio_file)
        assert result is None
        assert audio_file.exists()
