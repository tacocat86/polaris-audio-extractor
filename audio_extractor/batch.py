import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from audio_extractor.extractor import extract, resolve_output_path
from audio_extractor.utils import find_video_files, write_log
from audio_extractor.progress import make_progress, print_summary
from audio_extractor.renamer import propose_rename, DEFAULT_OLLAMA_HOST


def process_one(
    video: Path,
    output_dir: Path | None,
    fmt: str,
    overwrite: bool,
    dry_run: bool,
    rename: bool = False,
    ollama_host: str = DEFAULT_OLLAMA_HOST,
) -> dict:
    try:
        # Check existence BEFORE extraction to correctly classify status
        expected_output = resolve_output_path(video, output_dir, fmt)
        already_existed = expected_output.exists() and not overwrite

        output = extract(
            input_path=video,
            output_dir=output_dir,
            fmt=fmt,
            overwrite=overwrite,
            dry_run=dry_run,
        )
        if rename and not dry_run and not already_existed:
            proposed = propose_rename(output, ollama_host=ollama_host, auto=True)
            if proposed:
                output = proposed

        status = "skipped" if already_existed else "success"
        return {"input": str(video), "output": str(output),
                "status": status, "error": None}
    except Exception as e:
        return {"input": str(video), "output": None,
                "status": "failed", "error": str(e)}


def run_batch(
    folder: Path,
    output_dir: Path | None = None,
    fmt: str = "mp3",
    overwrite: bool = False,
    dry_run: bool = False,
    recursive: bool = False,
    workers: int = 1,
    log_file: Path | None = None,
    rename: bool = False,
    ollama_host: str = DEFAULT_OLLAMA_HOST,
) -> None:
    max_workers = min(workers, os.cpu_count() or 1)
    video_files = find_video_files(folder, recursive=recursive)

    if not video_files:
        print(f"No video files found in: {folder}")
        return

    print(f"Found {len(video_files)} video file(s) — "
          f"workers: {max_workers}, dry-run: {dry_run}"
          + (f", ollama-host: {ollama_host}" if rename else ""))

    results = []

    with make_progress() as progress:
        task = progress.add_task("Extracting audio", total=len(video_files))

        if max_workers == 1:
            for video in video_files:
                result = process_one(
                    video, output_dir, fmt, overwrite, dry_run, rename, ollama_host
                )
                results.append(result)
                progress.advance(task)
        else:
            futures = {}
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for video in video_files:
                    f = executor.submit(
                        process_one, video, output_dir, fmt,
                        overwrite, dry_run, rename, ollama_host
                    )
                    futures[f] = video
                for future in as_completed(futures):
                    results.append(future.result())
                    progress.advance(task)

    succeeded = sum(1 for r in results if r["status"] == "success")
    skipped   = sum(1 for r in results if r["status"] == "skipped")
    failed    = sum(1 for r in results if r["status"] == "failed")
    print_summary(succeeded, skipped, failed)

    if log_file:
        write_log(log_file, results)
        print(f"Log written to: {log_file}")
