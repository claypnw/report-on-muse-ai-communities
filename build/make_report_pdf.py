#!/usr/bin/env python3
"""Build the readable PDF of the Report on Muse AI Communities from report-on-muse-ai-communities.md.
Formatting standard set by the admin 2026-10-22: all the information, laid out like a
regular report — bold titles, underlined part headers, bullets for the facts,
highlights that pop. Nothing in the record is dropped."""
import html, re, sys, urllib.parse
from datetime import date, datetime
from pathlib import Path

SRC = Path.home() / "workspace/learning/community-check/report-on-muse-ai-communities.md"
OUT = Path.home() / "workspace/your_files/report-on-muse-ai-communities-2026-10-22.pdf"

# TEST BUILD (2026-10-30): newspaper form — the Morning Scroll palette
# (parchment #f7f0dc, ink #241a10, card cream #fffaf5, rule brown #8a6d3b,
# accent red #7a1f1f on part headers) and each Part's entries laid in 3
# newspaper columns via a .cols wrapper (see render()).
CSS_BASE = """
body { font-family: 'DejaVu Sans', sans-serif; line-height: 1.45; color: #241a10; background: #f7f0dc; }
h1 { font-size: 20pt; margin: 0 0 4pt 0; border-bottom: 3px solid #8a6d3b; padding-bottom: 6pt; }
.about { background: #efe6cb; border-left: 4px solid #8a6d3b; padding: 8pt 10pt; font-size: 9.5pt; margin: 10pt 0 16pt 0; }
.summary { background: #f9efd2; border: 1.5px solid #8a6d3b; padding: 8pt 10pt; font-weight: bold; margin: 0 0 16pt 0; }
h2 { font-size: 15pt; margin: 20pt 0 4pt 0; text-decoration: underline; color: #7a1f1f; }
.part-note { font-style: italic; margin: 0 0 10pt 0; }
.cols { column-count: 3; column-rule: 1px solid #8a6d3b; }
.entry { background: #fffaf5; border: 1px solid #8a6d3b; border-radius: 4pt; padding: 9pt 11pt; margin: 0 0 10pt 0; page-break-inside: avoid; break-inside: avoid; overflow-wrap: break-word; }
.entry.solved { background: #e2ead3; border-color: #5f7a4d; }
.entry h3 { font-size: 12pt; margin: 0 0 5pt 0; border-bottom: 1.5px solid #8a6d3b; padding-bottom: 3pt; }
.entry p { margin: 0 0 6pt 0; }
.entry ul { margin: 4pt 0 0 0; padding-left: 16pt; }
.entry li { margin: 2pt 0; }
.entry li ul { margin: 2pt 0 2pt 0; }
a { color: #7a1f1f; }
.state { font-weight: bold; }
.dates { color: #6b5a43; margin: 2pt 0; }
.skip { display: block; margin: 4pt 0 8pt 0; }
.quiet { font-style: italic; }
"""

CSS_WEB = CSS_BASE + """
body { font-size: 10.5pt; margin: 0; padding: 28px 34px; }
.cols { column-gap: 26px; }
.dates { font-size: 10.5pt; }
.skip { font-size: 11pt; }
.removebtn { display: inline-block; background: #fffaf5; border: 1.5px solid #8a6d3b; color: #7a1f1f; padding: 3pt 10pt; border-radius: 4pt; text-decoration: none; font-weight: bold; }
.talkbtn { display: inline-block; background: #fffaf5; border: 1.5px solid #8a6d3b; color: #7a1f1f; padding: 3pt 10pt; border-radius: 4pt; text-decoration: none; font-weight: bold; margin-left: 8pt; }
"""

CSS_PDF = CSS_BASE + """
@page { size: Letter; margin: 0.7in 0.75in; background: #f7f0dc; }
body { font-size: 9.5pt; }
.cols { column-gap: 14pt; column-rule: 0.5pt solid #8a6d3b; }
.entry h3 { font-size: 11pt; }
.dates { font-size: 9.5pt; }
.skip { font-size: 10pt; }
"""

def md_link(text):
    def rep(m):
        label, url = m.group(1), m.group(2)
        return f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(label)}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rep, text)

def inline(text):
    t = html.escape(text)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(https?://[^\s)]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    return t

def linkify_urls(text):
    return re.sub(r'(https?://[^\s)]+)', r'<a href="\1" target="_blank" rel="noopener">link</a>', text)

def render(web=False, skip_entries=None, program_url=""):
    lines = SRC.read_text().splitlines()
    out = []
    title = "Report on Muse AI Communities"
    about, body = [], []
    mode = "about"
    entry = None  # dict with title, paras, bullets
    topics = problems = solved = 0

    def entry_dates(e):
        first = last = ""
        for b in e["bullets"]:
            t = b.lstrip("- ").strip()
            if t.startswith("First seen:"): first = t.split(":", 1)[1].strip()
            if t.startswith("Last updated:"): last = t.split(":", 1)[1].strip()
            if t.startswith("Last activity:"): last = t.split(":", 1)[1].strip()
        return first, last

    skip_titles = {t for (t, f, l, d) in (skip_entries or [])}

    # TEST BUILD: entries flow inside a .cols wrapper (3 newspaper columns);
    # part headers, part notes, and the quiet-problems header close it so
    # they span the full width.
    in_cols = False

    def open_cols():
        nonlocal in_cols
        if not in_cols:
            body.append('<div class="cols">')
            in_cols = True

    def close_cols():
        nonlocal in_cols
        if in_cols:
            body.append("</div>")
            in_cols = False

    # SORTING (the admin, 2026-10-30): within each part — and within the
    # Quiet problems section — the most recent story stands at the top and
    # the oldest at the bottom, ordered by each entry's last date (Last
    # updated / Last activity). Entries are collected per group while
    # parsing and rendered, sorted, when the group closes. An entry whose
    # last date is missing or unreadable sorts as the oldest (date.min),
    # and the stable sort keeps such entries in their file order.
    groups = {"topics": [], "problems": [], "quiet": []}
    cur_group = "topics"

    def last_date_key(e):
        _, last = entry_dates(e)
        s = last.strip()
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
        if m:
            try:
                return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                pass
        for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return date.min

    def flush_entry():
        nonlocal entry
        if entry is None:
            return
        # A story on the admin's skip list is left out of the page and its counts.
        if web and entry["title"] in skip_titles:
            entry = None
            return
        groups[cur_group].append(entry)
        entry = None

    def render_group(name):
        nonlocal topics, problems, solved
        es = groups[name]
        groups[name] = []
        es = sorted(es, key=last_date_key, reverse=True)
        for entry in es:
            if entry["kind"] == "topics": topics += 1
            else: problems += 1
            if entry["solved"]: solved += 1
            cls = "entry solved" if entry["solved"] else "entry"
            open_cols()
            body.append(f'<div class="{cls}"><h3>{html.escape(entry["title"])}</h3>')
            if web:
                first, last = entry_dates(entry)
                dlabel = "Last updated" if entry["kind"] == "topics" else "Last activity"
                body.append(f'<p class="dates">First seen: {html.escape(first)} &middot; {dlabel}: {html.escape(last)}</p>')
                # TEST BUILD (2026-10-30): the GitHub-note road replaces the dead
                # checkbox. The button opens a ready-filled issue in the report's
                # own repository (claypnw/report-on-muse-ai-communities): the
                # issue title carries the fixed marker "SKIP: " plus the story's
                # exact title, and the issue body names the story and its part.
                # No Google program address is wired anywhere.
                part_label = "Part 1 (topics)" if entry["kind"] == "topics" else "Part 2 (problems)"
                issue_title = "SKIP: " + entry["title"]
                issue_body = ("Remove this story from the AI community report.\n\n"
                              f"Story: {entry['title']}\nPart: {part_label}\n\n"
                              "Opened from the 'Remove this story' button on the report page.")
                issue_url = ("https://github.com/claypnw/report-on-muse-ai-communities/issues/new"
                             "?title=" + urllib.parse.quote(issue_title, safe="")
                             + "&body=" + urllib.parse.quote(issue_body, safe=""))
                # TALK BUTTON (the admin, 2026-10-30): a second button beside
                # Remove, on the same GitHub-note road. It opens a ready-filled
                # issue titled "TALK: " plus the story's exact title, carrying
                # the story's own text (paragraphs and bullets, plain), so the
                # story lands in the main chat for discussion. GitHub issue
                # URLs cannot grow without bound: if the whole URL would pass
                # 7,000 characters, the story text is cut at the last whole
                # sentence that fits and the body ends with a pointer line.
                talk_title = "TALK: " + entry["title"]
                story_parts = list(entry["paras"])
                if entry["bullets"]:
                    story_parts.append("\n".join(entry["bullets"]))
                story_text = "\n\n".join(story_parts)
                talk_head = ("https://github.com/claypnw/report-on-muse-ai-communities/issues/new"
                             "?title=" + urllib.parse.quote(talk_title, safe="") + "&body=")
                talk_body = story_text + "\n\n— From the AI community report page (Talk button)"
                talk_url = talk_head + urllib.parse.quote(talk_body, safe="")
                if len(talk_url) > 7000:
                    notice = "\n\n[The rest of this story stands on the report page.]"
                    cuts = [m.end() for m in re.finditer(r"[.!?](?=\s|$)", story_text)]
                    best = 0
                    for c in cuts:
                        if len(talk_head + urllib.parse.quote(story_text[:c] + notice, safe="")) <= 7000:
                            best = c
                        else:
                            break
                    if best:
                        talk_body = story_text[:best] + notice
                    else:
                        keep = 0
                        for c in range(len(story_text), 0, -1):
                            if len(talk_head + urllib.parse.quote(story_text[:c] + notice, safe="")) <= 7000:
                                keep = c
                                break
                        talk_body = story_text[:keep] + notice
                    talk_url = talk_head + urllib.parse.quote(talk_body, safe="")
                body.append(f'<p class="skip"><a class="removebtn" href="{html.escape(issue_url, quote=True)}" target="_blank" rel="noopener">Remove this story</a><a class="talkbtn" href="{html.escape(talk_url, quote=True)}" target="_blank" rel="noopener">Talk about this story</a></p>')
            for p in entry["paras"]:
                body.append(f"<p>{inline(p)}</p>")
            if entry["bullets"]:
                body.append("<ul>")
                for b in entry["bullets"]:
                    if b.startswith("  - "):
                        body.append(f'<li style="list-style:none"><ul><li>{inline(b[4:])}</li></ul></li>')
                    else:
                        txt = b[2:]
                        if txt.startswith("State:"):
                            txt = 'State: <span class="state">' + txt[len("State:"):].strip() + "</span>"
                            body.append(f"<li>{txt}</li>")
                        else:
                            body.append(f"<li>{inline(txt)}</li>")
                body.append("</ul>")
            body.append("</div>")

    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            title = ln[2:].strip(); i += 1; continue
        if ln.startswith("## "):
            flush_entry(); render_group(cur_group); close_cols(); mode = "body"
            head = ln[3:].strip()
            body.append(f"<h2>{html.escape(head)}</h2>")
            if head.startswith("Part 1"): cur = "topics"; cur_group = "topics"
            elif head.startswith("Part 2"): cur = "problems"; cur_group = "problems"
            i += 1; continue
        if ln.startswith("### "):
            flush_entry(); mode = "body"
            t = ln[4:].strip()
            if t == "Quiet problems":
                render_group(cur_group)
                cur_group = "quiet"
                close_cols()
                body.append('<h2 style="font-size:12.5pt">Quiet problems</h2>')
                entry = None; i += 1
                # following italic note
                note = []
                i += 0
                while i < len(lines) and (lines[i].strip() == "" or lines[i].startswith("_")):
                    if lines[i].startswith("_"): note.append(lines[i].strip("_ "))
                    i += 1
                body.append(f'<p class="quiet">{" ".join(note)}</p>')
                continue
            entry = {"title": t, "paras": [], "bullets": [], "solved": False, "kind": cur}
            i += 1; continue
        if ln.strip() == "":
            i += 1; continue
        if ln.startswith("- ") or ln.startswith("  - "):
            if entry is not None:
                entry["bullets"].append(ln)
                if "State:" in ln and "solved" in ln.lower(): entry["solved"] = True
            i += 1; continue
        # paragraph text (join wrapped lines)
        para = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "- ", "  - ")):
            para.append(lines[i].strip()); i += 1
        text = " ".join(para)
        if mode == "about":
            about.append(text)
        elif entry is not None:
            entry["paras"].append(text)
        else:
            close_cols()
            body.append(f'<p class="part-note">{inline(text)}</p>')
    flush_entry()
    render_group(cur_group)
    close_cols()

    doc = ["<html><head><meta charset='utf-8'><title>Report on Muse AI Communities</title><style>", CSS_WEB if web else CSS_PDF, "</style></head><body>"]
    doc.append(f"<h1>{html.escape(title)}</h1>")
    doc.append(f'<div class="summary">In this report: {topics} topics and {problems} problems from the Muse AI communities. {solved} problem solved so far.</div>')
    doc.extend(body)
    if web and skip_entries:
        doc.append('<h2 style="font-size:12.5pt">Stories you have told me to skip</h2>')
        doc.append('<div class="about">These stories are left out of the report. Take the check off to put a story back.<br><br>')
        for (t, f, l, d) in skip_entries:
            te = html.escape(t); tq = html.escape(t, quote=True)
            line = f'{te} — first seen {html.escape(f)}, last date {html.escape(l)}, skipped {html.escape(d)}'
            if program_url:
                doc.append(f'<label class="skip"><input type="checkbox" class="unskipbox" data-title="{tq}" checked> {line} <span class="skipnote"></span></label><br>')
            else:
                doc.append(f'<label class="skip"><input type="checkbox" checked disabled> {line} (the skip program is not set up yet)</label><br>')
        doc.append('</div>')
    if about:
        # the admin, 2026-10-22: the standing-record note is kept, and it goes at the
        # bottom of the report — he wants to see it, not first thing.
        doc.append('<h2 style="font-size:12.5pt">About this report</h2>')
        doc.append('<div class="about">' + "<br>".join(html.escape(a) for a in about) + "</div>")
    if web:
        doc.append(f'''<script>
var SKIP_URL = "{program_url}";
function postSkip(data) {{
  // The skip program's answer cannot be read back by the page, so a finished
  // send is marked "Sent" only — the list read at the next run is the proof.
  return fetch(SKIP_URL, {{method: "POST", mode: "no-cors", body: JSON.stringify(data)}});
}}
document.addEventListener("change", function(ev) {{
  var box = ev.target;
  var note = box.parentElement ? box.parentElement.querySelector(".skipnote") : null;
  if (box.classList.contains("skipbox") && box.checked) {{
    box.disabled = true;
    postSkip({{action: "skip", title: box.dataset.title, first: box.dataset.first, last: box.dataset.last}})
      .then(function() {{ if (note) note.textContent = "Sent. This story leaves the report when the skip list is read at the next run. If it is still here after that run, the skip did not land."; }})
      .catch(function() {{ box.checked = false; box.disabled = false; alert("The skip did not go through. Try again in a moment."); }});
  }}
  if (box.classList.contains("unskipbox") && !box.checked) {{
    box.disabled = true;
    postSkip({{action: "unskip", title: box.dataset.title}})
      .then(function() {{ if (note) note.textContent = "Sent. This story comes back in the next report."; }})
      .catch(function() {{ box.checked = true; box.disabled = false; alert("Putting the story back did not go through. Try again in a moment."); }});
  }}
}});
</script>''')
    doc.append("</body></html>")
    return "\n".join(doc)

def read_skip_file(path):
    entries = []
    try:
        for ln in Path(path).read_text().splitlines():
            parts = [p.strip() for p in ln.split("|")]
            if len(parts) == 4 and parts[0]:
                entries.append(tuple(parts))
    except FileNotFoundError:
        pass
    return entries

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "page":
        base = Path.home() / "workspace/learning/community-check/skip-list"
        url_file = base / "program-url.txt"
        url = url_file.read_text().strip() if url_file.exists() else ""
        if len(sys.argv) > 2 and sys.argv[2] == "sample":
            skips = read_skip_file(base / "test-sample.txt")
        else:
            skips = read_skip_file(base / "skip-list-current.txt")
        Path("/tmp/report-page.html").write_text(render(web=True, skip_entries=skips, program_url=url))
        print("wrote /tmp/report-page.html")
    else:
        Path("/tmp/report-on-muse-ai-communities.html").write_text(render())
        print("wrote /tmp/report-on-muse-ai-communities.html")
