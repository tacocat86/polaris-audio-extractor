from pathlib import Path
from audio_extractor.utils import find_video_files


def test_find_video_files_flat(tmp_path):
    (tmp_path / "a.mp4").write_bytes(b"")
    (tmp_path / "b.mkv").write_bytes(b"")
    (tmp_path / "c.txt").write_bytes(b"")
    result = find_video_files(tmp_path)
    assert len(result) == 2
    assert all(f.suffix in {".mp4", ".mkv"} for f in result)


def test_find_video_files_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "a.mp4").write_bytes(b"")
    (sub / "b.mkv").write_bytes(b"")
    result = find_video_files(tmp_path, recursive=True)
    assert len(result) == 2


def test_find_video_files_empty(tmp_path):
    result = find_video_files(tmp_path)
    assert result == []


def test_find_video_files_all_extensions(tmp_path):
    for ext in [".mkv", ".mp4", ".avi", ".mov", ".wmv",
                ".flv", ".webm", ".m4v", ".ts", ".m2ts"]:
        (tmp_path / f"file{ext}").write_bytes(b"")
    result = find_video_files(tmp_path)
    assert len(result) == 10
