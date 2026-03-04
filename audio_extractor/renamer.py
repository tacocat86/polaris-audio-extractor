import os
import json
import urllib.request
import urllib.error
from pathlib import Path


API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are a music metadata parser. Given a raw filename (without extension),
extract the artist and title. The filename may follow patterns like:
- Artist - Title
- Title (Artist)
- Artist - Title (Year)
- Messy or ambiguous names

Respond ONLY with a JSON object in this exact format, no preamble or markdown:
{"artist": "Artist Name", "title": "Song Title", "confident": true}

If you cannot confidently determine both artist and title, set confident to false and
make your best guess. Never return anything other than this JSON object."""


def parse_filename(stem: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Export it with: export ANTHROPIC_API_KEY=your_key"
        )

    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 200,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": f"Filename: {stem}"}
        ]
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            text = data["content"][0]["text"].strip()
            return json.loads(text)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Anthropic API error {e.code}: {e.read().decode()}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse API response as JSON: {e}")


def propose_rename(output_path: Path) -> Path | None:
    stem = output_path.stem
    ext = output_path.suffix

    print(f"\nParsing filename: '{stem}'")
    try:
        result = parse_filename(stem)
    except RuntimeError as e:
        print(f"  Rename skipped — {e}")
        return None

    artist = result.get("artist", "").strip()
    title = result.get("title", "").strip()
    confident = result.get("confident", False)

    if not artist or not title:
        print("  Rename skipped — could not parse artist/title")
        return None

    confidence_note = "" if confident else " (low confidence)"
    new_name = f"{artist} - {title}{ext}"
    new_path = output_path.parent / new_name

    print(f"  Proposed rename{confidence_note}:")
    print(f"    {output_path.name}")
    print(f"    → {new_name}")

    if new_path == output_path:
        print("  No change needed.")
        return None

    answer = input("  Apply rename? [y/N] ").strip().lower()
    if answer == "y":
        output_path.rename(new_path)
        print(f"  Renamed: {new_name}")
        return new_path
    else:
        print("  Skipped.")
        return None
