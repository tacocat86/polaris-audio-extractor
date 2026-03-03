import argparse
from pathlib import Path
from audio_extractor.extractor import extract


def main():
    parser = argparse.ArgumentParser(
        prog="extract-audio",
        description="Extract audio from video files via ffmpeg"
    )
    parser.add_argument("input", type=Path, help="Input video file")
    parser.add_argument("-o", "--output-dir", type=Path, default=None,
                        help="Output directory (default: same as input)")
    parser.add_argument("-f", "--format", default="mp3",
                        help="Output format (default: mp3)")
    parser.add_argument("--codec", default="libmp3lame",
                        help="Audio codec (default: libmp3lame)")
    parser.add_argument("--bitrate", default="192k",
                        help="Audio bitrate (default: 192k)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite output if it exists")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print ffmpeg command without executing")

    args = parser.parse_args()

    try:
        output = extract(
            input_path=args.input,
            output_dir=args.output_dir,
            fmt=args.format,
            codec=args.codec,
            bitrate=args.bitrate,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        if not args.dry_run:
            print(f"Done: {output}")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
