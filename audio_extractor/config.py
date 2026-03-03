import tomllib
import tomli_w
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "audio-extractor" / "config.toml"

DEFAULTS = {
    "paths": {
        "drop_folder": str(Path.home() / "Videos" / "inbox"),
        "output_dir": str(Path.home() / "Music" / "extracted"),
    },
    "extraction": {
        "formats": ["mp4", "mkv", "avi", "mov"],
        "audio_format": "mp3",
        "codec": "libmp3lame",
        "bitrate": "192k",
    }
}


def create_default_config() -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "wb") as f:
        tomli_w.dump(DEFAULTS, f)
    print(f"Created default config: {CONFIG_PATH}")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        create_default_config()
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def ensure_dirs(config: dict) -> None:
    drop = Path(config["paths"]["drop_folder"])
    out = Path(config["paths"]["output_dir"])
    drop.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
