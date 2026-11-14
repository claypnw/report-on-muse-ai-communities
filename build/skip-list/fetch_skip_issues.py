#!/usr/bin/env python3
"""Fetch the issue-road skip titles for the Report on Muse AI Communities.

The story-removal button on the report page opens a ready-filled GitHub
issue in claypnw/report-on-muse-ai-communities titled "SKIP: <exact story
title>". This program reads ALL issues in that repository (open and
closed) through the GitHub connector credential route — the same route
github_publish.py uses: a stand-in value rides on each request and Muse
swaps in the stored key only on a request to api.github.com. The key is
never read, printed, or stored by this program.

What counts:
  - Only issues written by the repository owner (login "claypnw").
  - A title starting with "SKIP: " adds the story title after the marker.
  - A title starting with "UNSKIP: " removes that story title.
  - Issues are applied in creation-date order, so the latest word wins
    when both a SKIP and an UNSKIP exist for the same story.
  - A closed SKIP issue still counts: closing an issue is housekeeping,
    not an unskip. Only an UNSKIP issue puts a story back.
  - Pull requests (which the issues list also returns) never count.

Output: the surviving story titles, one per line, on stdout, in the
order their winning SKIP issues were created. An empty set prints
nothing and exits 0. Any read failure prints the reason on stderr and
exits 1 — a partial list is never printed as if it were the whole list.

Use:
  fetch_skip_issues.py                  read the live repository
  fetch_skip_issues.py --from-file F    read a saved JSON payload instead
                                        (a list of issue objects in the
                                        GitHub API's shape; the self-test
                                        road)
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

OWNER = "claypnw"
REPO = "report-on-muse-ai-communities"
HOST = "api.github.com"

SKIP_PREFIX = "SKIP: "
UNSKIP_PREFIX = "UNSKIP: "


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def api_get(path, timeout=60):
    """One GET against the GitHub API. Returns (status, body)."""
    url = f"https://{HOST}{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "claypnw-skip-issue-fetch",
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


def skip_titles_from_issues(issues):
    """The filtering, shared by the live road and the file road.

    Returns the surviving story titles ordered by the creation date of
    the SKIP issue that put each one in."""
    events = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        if "pull_request" in issue:
            continue
        user = issue.get("user") or {}
        if user.get("login") != OWNER:
            continue
        title = issue.get("title") or ""
        created = issue.get("created_at") or ""
        if title.startswith(SKIP_PREFIX):
            story = title[len(SKIP_PREFIX):].strip()
            if story:
                events.append((created, "skip", story))
        elif title.startswith(UNSKIP_PREFIX):
            story = title[len(UNSKIP_PREFIX):].strip()
            if story:
                events.append((created, "unskip", story))
    events.sort(key=lambda e: e[0])
    standing = {}
    for created, kind, story in events:
        if kind == "skip":
            standing[story] = created
        else:
            standing.pop(story, None)
    return [story for story, _ in sorted(standing.items(), key=lambda kv: kv[1])]


def main():
    parser = argparse.ArgumentParser(
        description="Print the issue-road skip titles, one per line.")
    parser.add_argument("--from-file", default=None,
                        help="read a saved JSON payload of issues instead "
                             "of the live repository")
    args = parser.parse_args()

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

    for story in skip_titles_from_issues(issues):
        print(story)
    return 0


if __name__ == "__main__":
    sys.exit(main())
