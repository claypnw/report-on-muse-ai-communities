#!/usr/bin/env python3
"""Fold report-page skip notes into the standing skip list.

The standing list is ``skip-list-current.txt``. It is a source in its own
right: once a GitHub SKIP note has been folded into it, the note can be
purged without putting the story back. Owner SKIP and UNSKIP issues are
applied over the standing lines in creation-date order, with one guard —
an issue word older than the date already standing on a title's line
(its fourth field, the date skipped) does not move that title. The Menu
app list is then unioned in as a current snapshot, and a title standing
on both the folded list and the app list is written once, on its app
line.

Every input is read before anything is written, and the output is
replaced atomically, so a failed read leaves the standing file whole.

Use:
  fold_skip_list.py --current LIST --output LIST [--app-file LINES]
                    [--issues-file ISSUES.json]

Without --issues-file the live repository is read through
fetch_skip_issues.py. On success the program prints three count lines:
EVENTS (owner SKIP/UNSKIP notes read), FOLDED (of those, the ones whose
word was applied over the standing list), and SKIPS (lines written).
Any failure prints the reason on stderr and exits 1.
"""
import argparse
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_skip_issues

DATE_SEP = " | "


def parse_line(line):
    """One 4-field list line -> (title, line, standing_date).

    The standing date is the fourth field (the date skipped). A line
    that does not split into four fields is kept whole as its title,
    with no standing date."""
    parts = line.rsplit(DATE_SEP, 3)
    if len(parts) == 4:
        return parts[0].strip(), line, parts[3].strip()
    return line.strip(), line, ""


def read_lines(path):
    """The non-empty lines of a list file. A missing file reads empty."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return [line.strip() for line in handle if line.strip()]
    except FileNotFoundError:
        return []


def issue_events(issues):
    """Owner SKIP/UNSKIP words from issue objects, oldest first.

    The same rules as fetch_skip_issues.skip_titles_from_issues: owner
    only, pull requests never count, closed issues still count."""
    events = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        if "pull_request" in issue:
            continue
        user = issue.get("user") or {}
        if user.get("login") != fetch_skip_issues.OWNER:
            continue
        title = issue.get("title") or ""
        created = issue.get("created_at") or ""
        date = created[:10]
        if title.startswith(fetch_skip_issues.SKIP_PREFIX):
            story = title[len(fetch_skip_issues.SKIP_PREFIX):].strip()
            if story:
                events.append((created, "skip", story, date))
        elif title.startswith(fetch_skip_issues.UNSKIP_PREFIX):
            story = title[len(fetch_skip_issues.UNSKIP_PREFIX):].strip()
            if story:
                events.append((created, "unskip", story, date))
    events.sort(key=lambda e: e[0])
    return events


def fold(current_lines, app_lines, issues):
    """Fold the three sources. Returns (lines, events, folded)."""
    entries = {}  # title -> (line, standing_date); insertion ordered
    for line in current_lines:
        title, whole, date = parse_line(line)
        if title:
            entries[title] = (whole, date)

    events = issue_events(issues)
    folded = 0
    for _created, kind, story, date in events:
        standing = entries.get(story)
        standing_date = standing[1] if standing else ""
        if standing_date and date and date < standing_date:
            continue  # an older word does not move a newer standing line
        if kind == "skip":
            entries[story] = (DATE_SEP.join([story, date, date, date]), date)
        else:
            entries.pop(story, None)
        folded += 1

    for line in app_lines:
        title, whole, date = parse_line(line)
        if title:
            entries[title] = (whole, date)

    return [line for line, _date in entries.values()], events, folded


def main():
    parser = argparse.ArgumentParser(
        description="Fold issue skip words into the standing skip list.")
    parser.add_argument("--current", required=True,
                        help="the standing list file (also a source)")
    parser.add_argument("--output", required=True,
                        help="where the folded list is written")
    parser.add_argument("--app-file", default=None,
                        help="a file holding the Menu app's list lines")
    parser.add_argument("--issues-file", default=None,
                        help="read issues from a saved JSON payload "
                             "instead of the live repository")
    args = parser.parse_args()

    try:
        current_lines = read_lines(args.current)
        app_lines = read_lines(args.app_file) if args.app_file else []
    except OSError as exc:
        print(f"ERROR: could not read a list file: {exc}", file=sys.stderr)
        return 1

    if args.issues_file:
        try:
            with open(args.issues_file, "r", encoding="utf-8") as handle:
                issues = json.load(handle)
        except Exception as exc:
            print(f"ERROR: could not read {args.issues_file}: {exc}",
                  file=sys.stderr)
            return 1
        if not isinstance(issues, list):
            print(f"ERROR: {args.issues_file} does not hold a list of issues",
                  file=sys.stderr)
            return 1
    else:
        try:
            issues = fetch_skip_issues.fetch_all_issues()
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    lines, events, folded = fold(current_lines, app_lines, issues)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    try:
        fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".fold-", text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line + "\n")
        os.replace(tmp_path, args.output)
    except OSError as exc:
        print(f"ERROR: could not write {args.output}: {exc}", file=sys.stderr)
        return 1

    print(f"EVENTS {len(events)}")
    print(f"FOLDED {folded}")
    print(f"SKIPS {len(lines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
