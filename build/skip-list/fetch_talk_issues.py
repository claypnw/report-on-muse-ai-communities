#!/usr/bin/env python3
"""Fetch the new "talk about this story" notes for the Report on Muse
AI Communities.

The talk button on the report page opens a ready-filled GitHub issue in
claypnw/report-on-muse-ai-communities titled "TALK: <exact story
title>". This program reads ALL issues in that repository (open and
closed) through the GitHub connector credential route — the same route
fetch_skip_issues.py and github_publish.py use: a stand-in value rides
on each request and Muse swaps in the stored key only on a request to
api.github.com. The key is never read, printed, or stored by this
program.

What counts as a NEW talk note:
  - The issue was written by the repository owner (login "claypnw").
  - The title starts with "TALK: " and names a story after the marker.
  - The issue number is not listed in the state file
    (talk-brought.txt, one number per line, beside this program):
    a number in that file means the story was already brought into
    the main chat.
  - Pull requests (which the issues list also returns) never count.
  - A closed TALK issue still counts if it was never brought: closing
    an issue is housekeeping, not a withdrawal.

Output: one line per new talk note, in the form
"TALKNEW <issue-number> <story title>", in creation-date order.
No new notes prints nothing and exits 0. Any read failure prints
nothing on stdout, prints the reason on stderr, and exits 1 — a
caller hook treats exit 1 as "no wake", so a failed read must never
look like a new note.

Use:
  fetch_talk_issues.py                  read the live repository
  fetch_talk_issues.py --mark N         record issue N as brought
                                        (prints "MARKED N")
  fetch_talk_issues.py --from-file F    read a saved JSON payload
                                        instead (a list of issue
                                        objects in the GitHub API's
                                        shape; the self-test road)
  fetch_talk_issues.py --state-file F   use F as the state file
                                        instead of talk-brought.txt
                                        (the self-test road)
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

OWNER = "claypnw"
REPO = "report-on-muse-ai-communities"
HOST = "api.github.com"

TALK_PREFIX = "TALK: "

DEFAULT_STATE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "talk-brought.txt")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def api_get(path, timeout=60):
    """One GET against the GitHub API. Returns (status, body)."""
    url = f"https://{HOST}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "claypnw-talk-issue-fetch",
    }
    request = urllib.request.Request(url, headers=headers, method="GET")
    add_surrogate_to_request(request, "custom.github", allowed_hosts=[HOST])
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, read_json_response(response)
    except urllib.error.HTTPError as err:
        try:
            body = json.loads(err.read().decode("utf-8", "replace"))
        except Exception:
            body = {}
        return err.code, body
    except (urllib.error.URLError, OSError) as err:
        return 0, {"message": f"no answer from {HOST}: {err}"}


def fetch_all_issues():
    """Every issue in the repository, open and closed, all pages."""
    issues = []
    page = 1
    while True:
        status, body = api_get(
            f"/repos/{OWNER}/{REPO}/issues?state=all&per_page=100&page={page}")
        if status != 200 or not isinstance(body, list):
            message = body.get("message", "no message") if isinstance(body, dict) \
                else "not a list"
            raise RuntimeError(f"issues read failed — answer {status}: {message}")
        issues.extend(body)
        if len(body) < 100:
            return issues
        page += 1


def read_brought_numbers(state_file):
    """The issue numbers already brought. A missing file is empty."""
    brought = set()
    try:
        with open(state_file, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    brought.add(int(line))
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    return brought


def new_talk_notes(issues, brought):
    """The filtering, shared by the live road and the file road.

    Returns [(issue_number, story_title), ...] in creation-date order
    for every owner TALK issue whose number is not in `brought`."""
    notes = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        if "pull_request" in issue:
            continue
        user = issue.get("user") or {}
        if user.get("login") != OWNER:
            continue
        title = issue.get("title") or ""
        if not title.startswith(TALK_PREFIX):
            continue
        story = title[len(TALK_PREFIX):].strip()
        if not story:
            continue
        number = issue.get("number")
        if not isinstance(number, int):
            continue
        if number in brought:
            continue
        created = issue.get("created_at") or ""
        notes.append((created, number, story))
    notes.sort(key=lambda n: (n[0], n[1]))
    return [(number, story) for _, number, story in notes]


def mark_brought(state_file, number):
    """Append `number` to the state file unless it is already there.

    Guards against a state file whose last line has no trailing
    newline: the new number starts on its own line, never glued onto
    the previous entry."""
    if number in read_brought_numbers(state_file):
        return
    needs_newline = False
    try:
        with open(state_file, "rb") as handle:
            handle.seek(0, os.SEEK_END)
            if handle.tell() > 0:
                handle.seek(-1, os.SEEK_END)
                needs_newline = handle.read(1) != b"\n"
    except FileNotFoundError:
        pass
    with open(state_file, "a", encoding="utf-8") as handle:
        if needs_newline:
            handle.write("\n")
        handle.write(f"{number}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Print the new TALK notes, one per line, or mark "
                    "one as brought.")
    parser.add_argument("--from-file", default=None,
                        help="read a saved JSON payload of issues instead "
                             "of the live repository")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE,
                        help="state file of brought issue numbers "
                             "(default: talk-brought.txt beside this "
                             "program)")
    parser.add_argument("--mark", type=int, default=None, metavar="N",
                        help="record issue N as brought and exit")
    args = parser.parse_args()

    if args.mark is not None:
        try:
            mark_brought(args.state_file, args.mark)
        except OSError as exc:
            print(f"ERROR: could not mark {args.mark} in "
                  f"{args.state_file}: {exc}", file=sys.stderr)
            return 1
        print(f"MARKED {args.mark}")
        return 0

    if args.from_file:
        try:
            with open(args.from_file, "r", encoding="utf-8") as handle:
                issues = json.load(handle)
        except Exception as exc:
            print(f"ERROR: could not read {args.from_file}: {exc}",
                  file=sys.stderr)
            return 1
        if not isinstance(issues, list):
            print(f"ERROR: {args.from_file} does not hold a list of issues",
                  file=sys.stderr)
            return 1
    else:
        try:
            issues = fetch_all_issues()
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    try:
        brought = read_brought_numbers(args.state_file)
    except OSError as exc:
        print(f"ERROR: could not read state file {args.state_file}: {exc}",
              file=sys.stderr)
        return 1

    for number, story in new_talk_notes(issues, brought):
        print(f"TALKNEW {number} {story}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
