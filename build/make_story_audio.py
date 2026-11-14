#!/usr/bin/env python3
"""Make per-story recordings for the AI community report newspaper page.

A recording is made only when its story is absent from the manifest, its
narration words have changed, or its recorded MP3 no longer stands at the
recorded size. Narration is the story title and body words (plus the Last
activity line for problems and quiet problems), with source lines and all
link targets excluded; see story_audio_common.py for the shared rules.

The voice road matches the edition readings on record: /opt/hatch/bin/tts
synthesize-script, one voice, Alex (avocado_v2:MAI_01), at standard speed.
Each finished MP3 is verified by byte size and ffprobe duration before
the manifest is updated for that story.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from build_newspaper_page import parse_entries
from story_audio_common import assign_entry_slugs, narration_hash, narration_text

DEFAULT_REPORT = BASE / "report-on-muse-ai-communities.md"
DEFAULT_MANIFEST = BASE / "story-audio-manifest.json"
DEFAULT_AUDIO_DIR = BASE / "story-audio"
TTS = "/opt/hatch/bin/tts"
VOICE_ID = "avocado_v2:MAI_01"
SPEAKER = "Alex"


def load_manifest(path):
    if not path.exists():
        return {"version": 1, "stories": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("stories"), dict):
        raise ValueError(f"manifest has no stories object: {path}")
    data.setdefault("version", 1)
    return data


def save_manifest(path, manifest):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2, sort_keys=False)
            fh.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def probe_mp3(path):
    """Return (byte_size, duration_seconds), verified from the file itself."""
    size = path.stat().st_size
    if size <= 0:
        raise ValueError("recording is empty")
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json", str(path),
        ],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise ValueError(f"ffprobe failed: {(result.stderr or result.stdout).strip()}")
    duration = float(json.loads(result.stdout)["format"]["duration"])
    if duration <= 0:
        raise ValueError("recording has no positive duration")
    return size, duration


def synthesize(narration, destination, work_dir):
    """Speak one story to a temporary MP3, verify it, then move it in place."""
    paragraphs = [p.strip() for p in narration.split("\n\n") if p.strip()]
    if not paragraphs:
        raise ValueError("narration text is empty")
    script_path = work_dir / "script.txt"
    script_path.write_text(
        "".join(f"{SPEAKER}: {paragraph}\n" for paragraph in paragraphs),
        encoding="utf-8",
    )
    temp_audio = work_dir / "recording.mp3"
    result = subprocess.run(
        [
            TTS, "synthesize-script",
            "--script", str(script_path),
            "--speaker", f"{SPEAKER}={VOICE_ID}",
            "--output", str(temp_audio),
            "--speed", "100",
        ],
        capture_output=True, text=True, timeout=1800,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"TTS failed with exit code {result.returncode}: {detail[-800:]}")
    # The synthesizer's final JSON line, when present, must also say ok.
    for line in reversed((result.stdout or "").strip().splitlines()):
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if isinstance(payload, dict) and "ok" in payload and not payload["ok"]:
            raise RuntimeError("TTS reported ok=false")
        break
    size, duration = probe_mp3(temp_audio)
    os.replace(temp_audio, destination)
    # Read the size again at the final path: the manifest records the file
    # that actually stands beside the page build, not the temp file.
    final_size, final_duration = probe_mp3(destination)
    if final_size != size or abs(final_duration - duration) > 0.05:
        raise ValueError("recording changed while being moved into place")
    return final_size, final_duration


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--audio-dir", type=Path, default=DEFAULT_AUDIO_DIR)
    parser.add_argument(
        "--slug", action="append", dest="slugs",
        help="make only this slug (repeatable); default is every story",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="list each selected story's slug and recording state, then exit",
    )
    args = parser.parse_args(argv)

    topics, problems, quiet = parse_entries(args.report.read_text(encoding="utf-8"))
    ordered = (
        [(entry, "topics") for entry in topics]
        + [(entry, "problems") for entry in problems]
        + [(entry, "quiet") for entry in quiet]
    )
    slugs = assign_entry_slugs([entry for entry, _kind in ordered])
    manifest = load_manifest(args.manifest)
    records = manifest["stories"]
    wanted = set(args.slugs or [])

    made = []
    skipped = []
    failed = []

    for (entry, kind), slug in zip(ordered, slugs):
        if wanted and slug not in wanted:
            continue
        digest = narration_hash(entry, kind)
        filename = f"story-audio/{slug}.mp3"
        destination = args.audio_dir / f"{slug}.mp3"
        record = records.get(slug)
        standing = False
        if record and record.get("narration_hash") == digest \
                and record.get("filename") == filename and destination.exists():
            try:
                standing = destination.stat().st_size == int(record.get("size_bytes", -1))
            except (TypeError, ValueError):
                standing = False
        if args.list:
            state = "standing" if standing else "needs-recording"
            print(f"{state}\t{slug}\t{entry['title']}")
            continue
        if standing:
            skipped.append(slug)
            continue

        try:
            args.audio_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(
                prefix=".story-audio-", dir=str(args.audio_dir.parent)
            ) as work:
                size, duration = synthesize(
                    narration_text(entry, kind), destination, Path(work)
                )
            records[slug] = {
                "title": entry["title"],
                "narration_hash": digest,
                "filename": filename,
                "size_bytes": size,
            }
            # The manifest moves only after this recording stands verified,
            # and it moves as each recording lands.
            save_manifest(args.manifest, manifest)
            made.append(slug)
            print(f"made\t{slug}\t{size} bytes\t{duration:.3f} seconds")
        except Exception as exc:
            failed.append((slug, str(exc)))
            print(f"FAILED\t{slug}\t{exc}", file=sys.stderr)

    if args.list:
        return 0
    print(
        f"summary: {len(made)} made, {len(skipped)} already standing, "
        f"{len(failed)} failed"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
