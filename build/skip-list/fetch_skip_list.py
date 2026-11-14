#!/usr/bin/env python3
"""Fetch the skip list for the Report on Muse AI Communities.

Reads the program address from program-url.txt and the read key from
program-key.txt in this folder, asks the skip program for the list, and
writes the answer to skip-list-current.txt ONLY when the answer is a valid
list (an empty answer is a valid empty list). Four outcomes, kept apart:

  exit 0, "OK <n>"     a valid list was written (n stories, may be 0)
  exit 3, "NO SETTINGS" the address or key file is missing or empty
  exit 4, "BAD ANSWER"  the answer was not a list (wrong key, program down) —
                        the old list file is left exactly as it was
  exit 5, "NO ANSWER"   the program could not be reached — old list kept

A failed fetch never overwrites the known list with "empty."
"""
import sys
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "skip-list-current.txt"


def valid_list(text):
    if text.strip() == "":
        return []
    rows = []
    for ln in text.splitlines():
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) != 4 or not parts[0]:
            return None
        rows.append(ln)
    return rows


def main():
    url_file = BASE / "program-url.txt"
    key_file = BASE / "program-key.txt"
    url = url_file.read_text().strip() if url_file.exists() else ""
    key = key_file.read_text().strip() if key_file.exists() else ""
    if not url or not key:
        print("NO SETTINGS")
        return 3
    sep = "&" if "?" in url else "?"
    try:
        with urllib.request.urlopen(f"{url}{sep}key={key}", timeout=30) as r:
            text = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"NO ANSWER ({e})")
        return 5
    rows = valid_list(text)
    if rows is None:
        print("BAD ANSWER")
        return 4
    OUT.write_text("".join(r + "\n" for r in rows))
    print(f"OK {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
