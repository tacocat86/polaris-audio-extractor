import subprocess
import json
from pathlib import Path


def probe(input_path: Path) -> dict:
    """Get stream info from a video file via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        str(input_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    return json.loads(result.stdout)


def resolve_output_path(input_path: Path, output_dir: Path | None, fmt: str) -> Path:
    """Resolve the output file path."""
    stem = input_path.stem
    filename = f"{stem}.{fmt}"
    if output_dir:
        return output_dir / filename
    return input_path.parent / filename


def build_ffmpeg_cmd(
    input_path: Path,
    output_path: Path,
    codec: str = "libmp3lame",
    bitrate: str = "192k",
    overwrite: bool = False,
) -> list[str]:
    """Build the ffmpeg command list."""
    cmd = ["ffmpeg"]
    if overwrite:
        cmd.append("-y")
    cmd += [
        "-i", str(input_path),
        "-vn",
        "-acodec", codec,
        "-ab", bitrate,
        str(output_path),
    ]
    return cmd


def extract(
    input_path: Path,
    output_dir: Path | None = None,
    fmt: str = "mp3",
    codec: str = "libmp3lame",
    bitrate: str = "192k",
    overwrite: bool = False,
    dry_run: bool = False,
) -> Path:
    """
    Extract audio from a video file.
    Returns the output path.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = resolve_output_path(input_path, output_dir, fmt)
    cmd = build_ffmpeg_cmd(input_path, output_path, codec, bitrate, overwrite)

    if dry_run:
        print("DRY RUN — command that would be executed:")
        print(" ".join(cmd))
        return output_path

    if output_path.exists() and not overwrite:
        print(f"Skipping (already exists): {output_path}")
        return output_path

    print(f"Extracting audio: {input_path} -> {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")

    return output_path
