import json
import urllib.request
import urllib.error
from pathlib import Path

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
MODEL = "llama3.1:70b"
CONFIDENCE_THRESHOLD = 0.7

PROMPT_TEMPLATE = """You are a music metadata assistant. You must respond with raw JSON only. No explanation. No code. No markdown. Only a JSON object.

Given this music filename: {stem}

Respond with exactly this structure using your knowledge:
{{"artist": "artist name or null", "title": "song title or null", "confidence": 0.0}}

Rules:
- confidence is a float between 0.0 and 1.0
- Use null (not empty string) if you cannot determine artist or title
- Raw JSON only."""


def query_ollama(stem: str, host: str = DEFAULT_OLLAMA_HOST) -> dict:
    """Call the Ollama API and return parsed JSON metadata."""
    url = f"{host.rstrip('/')}/api/generate"
    prompt = PROMPT_TEMPLATE.format(stem=stem)
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            return json.loads(data["response"])
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ollama unreachable at {host}: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Ollama response as JSON: {e}")


def propose_rename(
    output_path: Path,
    ollama_host: str = DEFAULT_OLLAMA_HOST,
    auto: bool = False,
) -> Path | None:
    """
    Query Ollama to propose a rename for the extracted audio file.

    auto=False (single file): interactive y/N prompt
    auto=True  (batch mode):  apply automatically if confidence >= threshold
    """
    stem = output_path.stem
    ext = output_path.suffix

    print(f"\n  Parsing filename: '{stem}'")
    try:
        result = query_ollama(stem, ollama_host)
    except RuntimeError as e:
        print(f"  Rename skipped — {e}")
        return None

    artist = (result.get("artist") or "").strip()
    title = (result.get("title") or "").strip()
    confidence = float(result.get("confidence", 0.0))

    if not artist or not title:
        print(f"  Rename skipped — artist/title not determined "
              f"(confidence: {confidence:.2f})")
        return None

    if confidence < CONFIDENCE_THRESHOLD:
        print(f"  Rename skipped — confidence too low "
              f"({confidence:.2f} < {CONFIDENCE_THRESHOLD:.2f})")
        print(f"  Best guess was: '{artist} - {title}' — log for manual review")
        return None

    new_name = f"{artist} - {title}{ext}"
    new_path = output_path.parent / new_name

    if new_path == output_path:
        print("  No rename needed — filename already correct.")
        return None

    if new_path.exists():
        print(f"  Rename skipped — target already exists: {new_name}")
        return None

    confidence_note = f" (confidence: {confidence:.2f})"
    print(f"  Proposed{confidence_note}: {output_path.name} → {new_name}")

    if auto:
        output_path.rename(new_path)
        print(f"  Renamed: {new_name}")
        return new_path

    answer = input("  Apply rename? [y/N] ").strip().lower()
    if answer == "y":
        output_path.rename(new_path)
        print(f"  Renamed: {new_name}")
        return new_path
    else:
        print("  Skipped.")
        return None
