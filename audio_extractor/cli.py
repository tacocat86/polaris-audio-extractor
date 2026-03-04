import argparse
import os
from pathlib import Path
from audio_extractor.extractor import extract
from audio_extractor.scanner import scan
from audio_extractor.formats import list_formats
from audio_extractor.batch import run_batch


def main():
    parser = argparse.ArgumentParser(
        prog="extract-audio",
        description="Extract audio from video files via ffmpeg"
    )
    parser.add_argument("input", type=Path, nargs="?", default=None,
                        help="Input video file or folder")
    parser.add_argument("-o", "--output-dir", type=Path, default=None,
                        help="Output directory")
    parser.add_argument("-f", "--format", default="mp3",
                        help="Output format (default: mp3)")
    parser.add_argument("--codec", default=None,
                        help="Override audio codec")
    parser.add_argument("--bitrate", default=None,
                        help="Override audio bitrate")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing output files")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without executing")
    parser.add_argument("--scan", action="store_true",
                        help="Scan configured drop folder")
    parser.add_argument("--list-formats", action="store_true",
                        help="List supported formats and availability")
    parser.add_argument("--recursive", action="store_true",
                        help="Recurse into subdirectories")
    parser.add_argument("--workers", type=int, default=1,
                        help=f"Parallel workers (default: 1, max: {os.cpu_count()})")
    parser.add_argument("--log-file", type=Path, default=None,
                        help="Path to write a plain text log")

    args = parser.parse_args()

    if args.list_formats:
        list_formats()

    elif args.scan:
        scan(dry_run=args.dry_run, overwrite=args.overwrite)

    elif args.input and args.input.is_dir():
        run_batch(
            folder=args.input,
            output_dir=args.output_dir,
            fmt=args.format,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            recursive=args.recursive,
            workers=args.workers,
            log_file=args.log_file,
        )

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
