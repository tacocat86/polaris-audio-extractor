import argparse
from pathlib import Path
from audio_extractor.extractor import extract
from audio_extractor.scanner import scan
from audio_extractor.formats import list_formats


def main():
    parser = argparse.ArgumentParser(
        prog="extract-audio",
        description="Extract audio from video files via ffmpeg"
    )
    parser.add_argument("input", type=Path, nargs="?", default=None,
                        help="Input video file (omit to use --scan)")
    parser.add_argument("-o", "--output-dir", type=Path, default=None)
    parser.add_argument("-f", "--format", default="mp3",
                        help="Output format (default: mp3)")
    parser.add_argument("--codec", default=None,
                        help="Override audio codec")
    parser.add_argument("--bitrate", default=None,
                        help="Override audio bitrate")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scan", action="store_true",
                        help="Scan drop folder and extract all videos")
    parser.add_argument("--list-formats", action="store_true",
                        help="List all supported formats and availability")

    args = parser.parse_args()

    if args.list_formats:
        list_formats()

    elif args.scan:
        scan(dry_run=args.dry_run, overwrite=args.overwrite)

    elif args.input:
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
        except (FileNotFoundError, RuntimeError, ValueError) as e:
            print(f"Error: {e}")
            raise SystemExit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
