#!/usr/bin/env python3
"""Shared story-audio identity and narration rules.

Both the newspaper builder and the narration helper use this module so a
story receives the same slug, narration text, and hash in either program.

Slug rule: Unicode-normalize the title, fold it to ASCII, lowercase it,
replace every run of non-alphanumeric characters with one hyphen, trim
hyphens, and cap the result at 80 characters. An empty result becomes
"story". Entries are assigned slugs in page order (topics, problems, then
quiet problems); the first entry using a base slug keeps it and later
collisions receive the shortest available numeric suffix (-2, -3, ...).

Narration rule: the story title, followed by its body paragraphs in file
order, followed by its Last activity line only for a problem or quiet
problem (the kinds whose pages print that line). Source lines and links
are excluded. Markdown links contribute their visible words but never
their URLs; bare URLs are removed.
"""

import hashlib
import html
import re
import unicodedata

_URL_RE = re.compile(r"https?://[^\s)]+|www\.[^\s)]+", re.I)
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((?:[^)(]+|\([^)]*\))+\)")
_SOURCE_PREFIX_RE = re.compile(
    r"^(?:[-*]\s*)?(?:"
    r"r/[A-Za-z0-9_]+(?:\s*\((?:original|crossposted)[^)]*\))?"
    r"|Meta Community Forums"
    r"|Built with Muse(?:\s*\([^)]*\))?"
    r"|TechSpot"
    r"|AndroidPure(?:\s*\([^)]*\))?"
    r"|Reddit"
    r")\s+—\s+",
    re.I,
)


def slugify_title(title):
    """Return the deterministic base slug for one story title."""
    folded = unicodedata.normalize("NFKD", title or "")
    folded = folded.encode("ascii", "ignore").decode("ascii").lower()
    folded = folded.replace("&", " and ")
    slug = re.sub(r"[^a-z0-9]+", "-", folded).strip("-")
    slug = slug[:80].rstrip("-")
    return slug or "story"


def assign_entry_slugs(entries):
    """Assign collision-free slugs to entry dicts in the supplied order."""
    used = set()
    next_suffix = {}
    slugs = []
    for entry in entries:
        base = slugify_title(entry.get("title", ""))
        candidate = base
        suffix = next_suffix.get(base, 2)
        while candidate in used:
            candidate = f"{base}-{suffix}"
            suffix += 1
        next_suffix[base] = suffix
        used.add(candidate)
        slugs.append(candidate)
    return slugs


def _clean_markdown_and_urls(text):
    """Keep speakable words; drop link targets and bare URLs."""
    text = html.unescape(text or "")
    # Repeat because a link label can itself contain a nested bracketed
    # fragment in the report's prose. The URL is discarded each time.
    for _ in range(3):
        cleaned = _MD_LINK_RE.sub(r"\1", text)
        if cleaned == text:
            break
        text = cleaned
    text = _URL_RE.sub("", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("`", "")
    text = re.sub(r"(?<!\w)\*|\*(?!\w)", "", text)
    # A parenthetical that held only a source locator and its URL is not
    # story prose once the URL is gone.
    text = re.sub(
        r"\(\s*(?:r/[A-Za-z0-9_]+|Meta Community Forums)?\s*[,;]?\s*\)",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return re.sub(r"\s+", " ", text).strip()


def is_source_citation(paragraph):
    """True when a parser-classified body paragraph is really a source line."""
    text = (paragraph or "").strip()
    if not text:
        return True
    if text.lower().startswith(("source:", "sources:")):
        return True
    if _URL_RE.fullmatch(text):
        return True
    return bool(_SOURCE_PREFIX_RE.match(text))


def clean_narration_paragraph(paragraph):
    """Return a speakable paragraph, or None for a source citation."""
    if is_source_citation(paragraph):
        return None
    cleaned = _clean_markdown_and_urls(paragraph)
    return cleaned or None


def narration_text(entry, kind):
    """Build the exact narration text used for both speech and hashing."""
    parts = []
    title = _clean_markdown_and_urls(entry.get("title", ""))
    if title:
        parts.append(title)
    for paragraph in entry.get("body", []):
        cleaned = clean_narration_paragraph(paragraph)
        if cleaned:
            parts.append(cleaned)
    if kind in ("problems", "quiet") and entry.get("last_activity"):
        cleaned = _clean_markdown_and_urls(entry["last_activity"])
        if cleaned:
            parts.append(cleaned)
    return "\n\n".join(parts)


def narration_hash(entry, kind):
    """SHA-256 of the exact narration text, encoded as UTF-8."""
    return hashlib.sha256(narration_text(entry, kind).encode("utf-8")).hexdigest()
