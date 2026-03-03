import pytest
from audio_extractor.formats import (
    FORMAT_MAP,
    validate_format,
    get_codec_for_format,
    probe_available_formats,
)


def test_format_map_has_required_formats():
    for fmt in ["mp3", "aac", "flac", "wav", "opus", "ogg", "m4a"]:
        assert fmt in FORMAT_MAP


def test_format_map_entries_have_required_keys():
    for fmt, info in FORMAT_MAP.items():
        assert "codec" in info, f"{fmt} missing codec"
        assert "description" in info, f"{fmt} missing description"
        assert "bitrate" in info, f"{fmt} missing bitrate key"


def test_get_codec_for_mp3():
    codec, bitrate = get_codec_for_format("mp3")
    assert codec == "libmp3lame"
    assert bitrate == "192k"


def test_get_codec_for_flac():
    codec, bitrate = get_codec_for_format("flac")
    assert codec == "flac"
    assert bitrate is None  # lossless, no bitrate


def test_validate_unknown_format_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        validate_format("xyz")


def test_probe_available_formats_returns_all_keys():
    availability = probe_available_formats()
    for fmt in FORMAT_MAP:
        assert fmt in availability
        assert isinstance(availability[fmt], bool)
