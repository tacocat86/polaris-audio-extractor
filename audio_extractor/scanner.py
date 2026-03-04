from pathlib import Path
from audio_extractor.extractor import extract
from audio_extractor.config import load_config, ensure_dirs
from audio_extractor.renamer import propose_rename


def scan(dry_run: bool = False, overwrite: bool = False, rename: bool = False) -> None:
    config = load_config()
    ensure_dirs(config)

    drop_folder = Path(config["paths"]["drop_folder"])
    output_dir = Path(config["paths"]["output_dir"])
    video_formats = config["extraction"]["formats"]
    audio_fmt = config["extraction"]["audio_format"]
    codec = config["extraction"]["codec"]
    bitrate = config["extraction"]["bitrate"]

    video_files = [
        f for f in drop_folder.iterdir()
        if f.is_file() and f.suffix.lstrip(".").lower() in video_formats
    ]

    if not video_files:
        print(f"No video files found in: {drop_folder}")
        return

    print(f"Found {len(video_files)} video file(s) in {drop_folder}")

    for video in sorted(video_files):
        try:
            output = extract(
                input_path=video,
                output_dir=output_dir,
                fmt=audio_fmt,
                codec=codec,
                bitrate=bitrate,
                overwrite=overwrite,
                dry_run=dry_run,
            )
            if rename and not dry_run:
                propose_rename(output)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"  Error processing {video.name}: {e}")
