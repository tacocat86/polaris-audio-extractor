import subprocess

FORMAT_MAP = {
    "mp3":  {"codec": "libmp3lame", "bitrate": "192k", "description": "MP3 (MPEG Audio Layer III)"},
    "aac":  {"codec": "aac",        "bitrate": "192k", "description": "AAC (Advanced Audio Codec)"},
    "flac": {"codec": "flac",       "bitrate": None,   "description": "FLAC (Lossless)"},
    "opus": {"codec": "libopus",    "bitrate": "128k", "description": "Opus (modern lossy)"},
    "wav":  {"codec": "pcm_s16le",  "bitrate": None,   "description": "WAV (uncompressed PCM)"},
    "ogg":  {"codec": "libvorbis",  "bitrate": "192k", "description": "OGG Vorbis"},
    "m4a":  {"codec": "aac",        "bitrate": "192k", "description": "M4A (AAC in MPEG-4)"},
}


def is_codec_available(codec: str) -> bool:
    """Check if a codec is available in the local ffmpeg installation."""
    result = subprocess.run(
        ["ffmpeg", "-codecs"],
        capture_output=True, text=True
    )
    return codec in result.stdout


def probe_available_formats() -> dict[str, bool]:
    """Return a dict of format name → available on this machine."""
    return {
        fmt: is_codec_available(info["codec"])
        for fmt, info in FORMAT_MAP.items()
    }


def validate_format(fmt: str) -> None:
    """Raise ValueError if format is unknown or unavailable."""
    if fmt not in FORMAT_MAP:
        known = ", ".join(FORMAT_MAP.keys())
        raise ValueError(
            f"Unknown format '{fmt}'. Available formats: {known}"
        )
    info = FORMAT_MAP[fmt]
    if not is_codec_available(info["codec"]):
        raise ValueError(
            f"Format '{fmt}' requires codec '{info['codec']}' "
            f"which is not available in your ffmpeg installation."
        )


def get_codec_for_format(fmt: str) -> tuple[str, str | None]:
    """Return (codec, bitrate) for a given format name."""
    info = FORMAT_MAP[fmt]
    return info["codec"], info["bitrate"]


def list_formats() -> None:
    """Print all formats with availability status."""
    availability = probe_available_formats()
    print(f"\n{'Format':<8} {'Codec':<14} {'Bitrate':<10} {'Description':<35} {'Status'}")
    print("-" * 85)
    for fmt, info in FORMAT_MAP.items():
        bitrate = info["bitrate"] or "N/A"
        status = "✓ available" if availability[fmt] else "✗ unavailable"
        print(f"{fmt:<8} {info['codec']:<14} {bitrate:<10} {info['description']:<35} {status}")
    print()
