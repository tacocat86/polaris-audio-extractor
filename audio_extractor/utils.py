from pathlib import Path
from datetime import datetime

VIDEO_EXTENSIONS = {
    ".mkv", ".mp4", ".avi", ".mov", ".wmv",
    ".flv", ".webm", ".m4v", ".ts", ".m2ts"
}


def find_video_files(folder: Path, recursive: bool = False) -> list[Path]:
    """Find all video files in a folder."""
    pattern = "**/*" if recursive else "*"
    return sorted([
        f for f in folder.glob(pattern)
        if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
    ])


def write_log(
    log_path: Path,
    results: list[dict],
) -> None:
    """Write a plain text log of batch results."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Polaris Audio Extractor — Batch Run: {timestamp}\n")
        f.write(f"{'='*60}\n")
        for r in results:
            status = r["status"].upper().ljust(9)
            f.write(f"[{status}] {r['input']}")
            if r.get("output"):
                f.write(f" -> {r['output']}")
            if r.get("error"):
                f.write(f" | ERROR: {r['error']}")
            f.write("\n")
        succeeded = sum(1 for r in results if r["status"] == "success")
        skipped   = sum(1 for r in results if r["status"] == "skipped")
        failed    = sum(1 for r in results if r["status"] == "failed")
        f.write(f"\nTotal: {len(results)} | "
                f"Succeeded: {succeeded} | "
                f"Skipped: {skipped} | "
                f"Failed: {failed}\n")
