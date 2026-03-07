import acoustid
import musicbrainzngs
from pathlib import Path

ACOUSTID_API_KEY = "9xenZG8ScN"  # replace with your actual key
CONFIDENCE_THRESHOLD = 0.70

# Words that indicate a derivative edit — not an original recording
DERIVATIVE_MARKERS = {
    "slowed", "reverb", "remix", "edit", "lofi", "lo-fi",
    "sped up", "nightcore", "mashup", "cover", "instrumental",
    "extended", "acoustic", "remaster", "remastered",
}

musicbrainzngs.set_useragent(
    "Polaris Audio Extractor",
    "0.1.0",
    "https://github.com/tacocat86/polaris-audio-extractor"
)


def has_derivative_marker(stem: str) -> bool:
    """Return True if the filename contains words indicating a derivative edit."""
    import re
    lower = stem.lower()
    # Check set markers as substrings
    if any(marker in lower for marker in DERIVATIVE_MARKERS):
        return True
    # Check "live" as whole word only — avoids false positive on "REASON TO LIVE"
    if re.search(r"\blive\b", lower):
        return True
    return False


def artist_overlap(original_artist: str, returned_artist: str) -> bool:
    """
    Rough check: does the returned artist share any significant token
    with the original artist token from the filename?
    Prevents MusicBrainz from substituting a completely different artist
    when the filename already contains an artist name.
    """
    orig_tokens = set(original_artist.lower().split())
    ret_tokens = set(returned_artist.lower().split())
    # Remove common noise words
    noise = {"the", "a", "an", "and", "&", "vs", "feat", "ft"}
    orig_tokens -= noise
    ret_tokens -= noise
    return bool(orig_tokens & ret_tokens)


def identify_by_fingerprint(audio_path: Path) -> dict | None:
    """
    Fingerprint the audio file and look it up via AcoustID + MusicBrainz.
    Returns dict with artist, title, confidence — or None if no match found.
    """
    try:
        results = acoustid.match(
            ACOUSTID_API_KEY,
            str(audio_path),
            meta="recordings releases",
            force_fpcalc=True,
        )
        for score, recording_id, title, artist in results:
            if score >= CONFIDENCE_THRESHOLD and title and artist:
                return {
                    "artist": artist,
                    "title": title,
                    "confidence": round(score, 2),
                    "source": "acoustid",
                    "recording_id": recording_id,
                }
        return None
    except acoustid.NoBackendError:
        raise RuntimeError("fpcalc not found — install libchromaprint-tools")
    except acoustid.FingerprintGenerationError as e:
        raise RuntimeError(f"Fingerprint generation failed: {e}")
    except acoustid.WebServiceError as e:
        raise RuntimeError(f"AcoustID API error: {e}")
    except Exception:
        return None


def identify_by_text(stem: str) -> dict | None:
    """
    Search MusicBrainz by cleaned filename text.
    ONLY called when filename has 'Artist - Title' structure AND
    no derivative markers (slowed, reverb, remix, etc.).
    Validates that returned artist has token overlap with original artist.
    """
    try:
        query = stem.replace("_", " ").strip()
        result = musicbrainzngs.search_recordings(query=query, limit=1)
        recordings = result.get("recording-list", [])
        if not recordings:
            return None

        recording = recordings[0]
        score = int(recording.get("ext:score", 0)) / 100.0
        if score < CONFIDENCE_THRESHOLD:
            return None

        title = recording.get("title", "").strip()
        artist_credits = recording.get("artist-credit", [])
        if not artist_credits or not title:
            return None

        first = artist_credits[0]
        if isinstance(first, dict):
            returned_artist = first.get("artist", {}).get("name", "").strip()
        else:
            returned_artist = str(first).strip()

        if not returned_artist:
            return None

        # Validate artist overlap — reject if returned artist is completely different
        original_artist = stem.split(" - ", 1)[0].strip()
        if not artist_overlap(original_artist, returned_artist):
            return None

        # Validate title similarity — reject if returned title shares no tokens
        # with the original title portion of the filename.
        # Prevents MusicBrainz matching on artist token alone and substituting
        # a completely unrelated track (e.g. Tokyo Rain → I'm Fine).
        original_title = stem.split(" - ", 1)[1].strip() if " - " in stem else stem
        noise = {"the", "a", "an", "of", "in", "on", "at", "ft", "feat", "2", "ii"}
        orig_title_tokens = set(original_title.lower().split()) - noise
        ret_title_tokens = set(title.lower().split()) - noise
        if orig_title_tokens and ret_title_tokens and not (orig_title_tokens & ret_title_tokens):
            return None

        return {
            "artist": returned_artist,
            "title": title,
            "confidence": round(score, 2),
            "source": "musicbrainz",
        }
    except Exception:
        return None


def identify(audio_path: Path) -> dict | None:
    """
    Full identification pipeline:

      1. AcoustID fingerprint (audio-based — works on any filename)
      2. MusicBrainz text search ONLY if:
           - filename has 'Artist - Title' structure, AND
           - filename contains no derivative markers (slowed, reverb, etc.), AND
           - returned artist has token overlap with original artist token
      3. Returns None if both fail — caller falls back to Ollama or keeps original
    """
    stem = audio_path.stem

    # Tier 1 — audio fingerprint (always attempted)
    try:
        result = identify_by_fingerprint(audio_path)
        if result:
            return result
    except RuntimeError:
        pass

    # Tier 2 — text search with strict guards
    if " - " in stem and not has_derivative_marker(stem):
        result = identify_by_text(stem)
        if result:
            return result

    return None
