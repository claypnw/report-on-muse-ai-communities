#!/usr/bin/env python3
"""Build the AI community report newspaper page (index.html) from the standing
report file report-on-muse-ai-communities.md.

Shape: DELIVERY-SHAPE.md — masthead, counts line, the full-record PDF
link, then Part 1 Topics and Part 2 Problems as newspaper articles in
three columns (CSS column-width), entries in standing-file order. Near
the top of the page, under the full-record line, stands the
whole-report listen entry — a "Listen to the whole report" button
that starts the story player at story 1 — with the newest standing
combined edition file, podcast/ai-stories-<date>.mp3 (the file the
AI stories podcast job makes each night from that check's new and
changed stories), kept as a plain one-file link under it (the
admin's order, 2026-11-06). The player carries the approved
seven-button set (the admin's order, 2026-11-10): Start of story or story before,
Back 10 seconds, Play, Pause, Forward 10 seconds, Next story, Stop,
with a "Story N of
M" line, a now-playing title line naming the story now playing, and a
time line — stepping through every story on the page that has a
standing recording, in page order. The pop-up form is the standard
(the admin's order, 2026-11-10): the bar does not stand open while
anyone is only reading; each story keeps its Listen link and the
whole-report listen entry stands at the top as the way to start from
story 1; tapping any Listen starts the player at that story and pops
the bar up as a floating window pinned to the top right of the
screen; Stop, or the last story ending, hides it again. The player
follows the sound on the page: each story carries its player number
by its title, the playing story's whole article carries a light
background, the page scrolls the playing article's top to the top of
the screen when the story changes, and inside the playing article the
sentence being read is lit from build-time sentence timings — the
recording's measured length spread across its sentences in proportion
to their word counts — with a gentle scroll that keeps the lit
sentence in view while the story plays (never while paused). A story
whose recording has no measured length carries no sentence timings,
and the article follow alone applies to it (the admin's Skip order, 2026-11-09,
widened to the full control set the same day, the set he approved on
the test-stand mockup, player-mockup-2026-11-09.html). No standing combined
file, no button, never a dead control. A story carries a button-styled
"Listen" link beside its title only when the story-audio manifest
records a recording for it and that MP3 stands in the audio directory
at the recorded byte size — no standing recording, no button, never a
dead control. Any whole-report block carried in the old shell is
removed and rebuilt fresh each run, so its target is always the newest
standing combined file, and the retired combined block's script is
removed with it.

The page shell (head, CSS, masthead, headline, part headers, colophon)
is carried over from the standing index.html; the articles are
regenerated from the report file. Rendering rules, matched line-for-line
against the first newspaper build of 2026-11-01:
- entry body paragraphs and indented sub-bullets become <p> in file order,
  with bare URLs linkified as <a href="URL">link</a>;
- "Last activity:" on a problem becomes a <p> after the body;
- Source / Sources bullets collect into the .sources div at the foot of
  the article, URLs linkified with the URL itself as the text;
- Re-check bullets stay in the body stream, in file order;
- First seen / Last updated / State bullets are not printed, except that a
  State containing "solved" marks the article solved.
"""
import argparse, html, json, re, subprocess, sys
from pathlib import Path

BASE = Path.home() / "workspace/learning/community-check"
SRC = BASE / "report-on-muse-ai-communities.md"
PAGE = BASE / "index.html"
MANIFEST = BASE / "story-audio-manifest.json"
AUDIO_DIR = BASE / "story-audio"
PODCAST_DIR = BASE / "podcast"

sys.path.insert(0, str(BASE))
from story_audio_common import assign_entry_slugs

def esc(text):
    return html.escape(text)

def linkify(text, label=None):
    def rep(m):
        url = m.group(0)
        return f'<a href="{url}">{label if label is not None else url}</a>'
    return re.sub(r'https?://[^\s)]+', rep, esc(text))

def parse_entries(md_text):
    """Return (topics, problems, quiet): lists of entry dicts in file order."""
    groups = {"topics": [], "problems": [], "quiet": []}
    group = None
    entry = None
    para = []

    def flush_para():
        nonlocal para
        if entry is not None and para:
            entry["body"].append(" ".join(para))
        para = []

    def flush_entry():
        nonlocal entry
        flush_para()
        if entry is not None and group is not None:
            groups[group].append(entry)
        entry = None

    for ln in md_text.splitlines():
        if ln.startswith("## "):
            flush_entry()
            head = ln[3:].strip()
            group = "topics" if head.startswith("Part 1") else "problems" if head.startswith("Part 2") else group
            continue
        if ln.startswith("### "):
            flush_entry()
            title = ln[4:].strip()
            if title == "Quiet problems":
                group = "quiet"
                entry = None
                continue
            entry = {"title": title, "body": [], "sources": [], "last_activity": "", "solved": False}
            continue
        if entry is None:
            continue
        if ln.startswith("  - "):
            flush_para()
            entry["body"].append(ln[4:].strip())
            continue
        if ln.startswith("- "):
            flush_para()
            t = ln[2:].strip()
            if t.startswith("First seen:"):
                pass
            elif t.startswith("Last updated:"):
                pass
            elif t.startswith("Last activity:"):
                entry["last_activity"] = t
            elif t.startswith("State:"):
                if "solved" in t.lower():
                    entry["solved"] = True
            elif t.startswith("Re-check"):
                entry["body"].append(t)
            elif t.startswith("Source"):
                entry["sources"].append(t)
            else:
                entry["sources"].append(t)
            continue
        if ln.strip() == "":
            flush_para()
            continue
        para.append(ln.strip())
    flush_entry()
    return groups["topics"], groups["problems"], groups["quiet"]

def load_recordings(manifest_path, audio_dir):
    """Return {slug: repository-relative MP3 path} for recordings that stand.

    A recording stands only when the manifest names the expected file for
    its slug and the MP3 in the audio directory has exactly the recorded
    byte size. Anything missing or mismatched yields no link.
    """
    try:
        data = json.loads(manifest_path.read_text())
        records = data["stories"]
    except Exception:
        return {}
    standing = {}
    if not isinstance(records, dict):
        return {}
    for slug, record in records.items():
        if not isinstance(record, dict):
            continue
        filename = f"story-audio/{slug}.mp3"
        if record.get("filename") != filename:
            continue
        try:
            size = int(record.get("size_bytes"))
        except (TypeError, ValueError):
            continue
        mp3 = audio_dir / f"{slug}.mp3"
        if mp3.is_file() and mp3.stat().st_size == size:
            standing[slug] = filename
    return standing

PLAYER_JS_TEMPLATE = """(function () {
  var TRACKS = __PLAYLIST__;
  var audio = document.getElementById('edition-audio');
  var nowEl = document.getElementById('now-playing');
  var titleEl = document.getElementById('now-title');
  var timeEl = document.getElementById('time-line');
  var idx = 0, done = false;
  var curArt = null, litSpan = null;
  var face = document.querySelector('.whole-player .wp-face');
  var popOpen = false;
  function fmt(s) {
    if (!isFinite(s) || s < 0) s = 0;
    s = Math.floor(s);
    return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2);
  }
  function showLine() {
    if (done) {
      nowEl.textContent = 'All ' + TRACKS.length + ' stories are done';
      titleEl.textContent = '';
    } else {
      nowEl.textContent = 'Story ' + (idx + 1) + ' of ' + TRACKS.length;
      titleEl.textContent = TRACKS[idx].title;
    }
    timeEl.textContent = fmt(audio.currentTime) + ' of ' + fmt(audio.duration);
    if ('mediaSession' in navigator) {
      try {
        navigator.mediaSession.metadata = new MediaMetadata({ title: TRACKS[idx].title, artist: 'AI community report' });
      } catch (e) {}
    }
  }
  function setLit(span) {
    if (litSpan === span) { return; }
    if (litSpan) { litSpan.classList.remove('sent-on'); }
    litSpan = span;
    if (litSpan) { litSpan.classList.add('sent-on'); }
  }
  function markSentence() {
    var tr = TRACKS[idx];
    if (done || !curArt || !tr || !tr.ends) { setLit(null); return; }
    var t = audio.currentTime, k = -1;
    if (t >= tr.t0) {
      k = tr.ends.length - 1;
      for (var i = 0; i < tr.ends.length; i++) {
        if (t < tr.ends[i]) { k = i; break; }
      }
    }
    if (k < 0) { setLit(null); return; }
    var spans = curArt.querySelectorAll('.sent');
    var span = spans[k] || null;
    var changed = span !== litSpan;
    setLit(span);
    if (changed && span && !audio.paused && !audio.ended) {
      var r = span.getBoundingClientRect();
      if (r.bottom < 8 || r.top > window.innerHeight - 8) {
        span.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }
  function markArticle(follow) {
    if (curArt) { curArt.classList.remove('playing'); curArt = null; }
    setLit(null);
    if (!face || !face.classList.contains('open')) { return; }
    var head = document.getElementById('story-' + TRACKS[idx].slug);
    curArt = head ? head.closest('article') : null;
    if (curArt) {
      curArt.classList.add('playing');
      if (follow && head) {
        head.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
    markSentence();
  }
  function sizeOpen() {
    if (!popOpen || !face) { return 0; }
    var h = face.offsetHeight;
    document.documentElement.style.setProperty('--wp-top', (h + 12) + 'px');
    return h;
  }
  function setOpen(on) {
    if (!face) { return; }
    if (on === popOpen) { if (on) { sizeOpen(); } return; }
    popOpen = on;
    if (on) {
      face.classList.add('open');
      var h = sizeOpen();
      markArticle(false);
      var head = document.getElementById('story-' + TRACKS[idx].slug);
      if (head && !done) {
        var r = head.getBoundingClientRect();
        if (r.top < h + 6 && r.bottom > 0) {
          head.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    } else {
      face.classList.remove('open');
      document.documentElement.style.setProperty('--wp-top', '12px');
      markArticle(false);
    }
  }
  function load(i, autoplay, follow) {
    idx = i; done = false;
    audio.src = TRACKS[i].href;
    audio.load();
    showLine();
    markArticle(follow);
    if (autoplay) { audio.play(); }
  }
  function goBegin() {
    if (done) { load(0, false, false); return; }
    if (audio.currentTime <= 5 && idx > 0) {
      load(idx - 1, !audio.paused, true);
    } else {
      audio.currentTime = 0; showLine(); markSentence();
    }
  }
  function goNext() {
    if (done) { load(0, true, true); return; }
    if (idx < TRACKS.length - 1) { load(idx + 1, true, true); }
  }
  document.getElementById('btn-play').addEventListener('click', function () {
    if (done) { load(0, true, true); return; }
    audio.play();
  });
  document.getElementById('btn-pause').addEventListener('click', function () {
    audio.pause();
  });
  document.getElementById('btn-stop').addEventListener('click', function () {
    audio.pause(); load(0, false, false); setOpen(false);
  });
  var startAll = document.getElementById('btn-start-all');
  if (startAll) {
    startAll.addEventListener('click', function () {
      setOpen(true); load(0, true, true);
    });
  }
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a.story-listen') : null;
    if (!a) { return; }
    var slug = a.getAttribute('data-story');
    for (var i = 0; i < TRACKS.length; i++) {
      if (TRACKS[i].slug === slug) {
        ev.preventDefault();
        setOpen(true);
        load(i, true, true);
        return;
      }
    }
  });
  document.getElementById('btn-begin').addEventListener('click', goBegin);
  document.getElementById('btn-back').addEventListener('click', function () {
    audio.currentTime = Math.max(0, audio.currentTime - 10); showLine(); markSentence();
  });
  document.getElementById('btn-fwd').addEventListener('click', function () {
    var d = audio.duration;
    if (isFinite(d) && audio.currentTime + 10 >= d) {
      if (idx < TRACKS.length - 1) { load(idx + 1, !audio.paused, true); }
      else { audio.currentTime = d; }
    } else {
      audio.currentTime = Math.min(d || 0, audio.currentTime + 10);
    }
    showLine(); markSentence();
  });
  document.getElementById('btn-next').addEventListener('click', goNext);
  audio.addEventListener('timeupdate', function () { showLine(); markSentence(); });
  audio.addEventListener('seeked', markSentence);
  audio.addEventListener('loadedmetadata', showLine);
  audio.addEventListener('play', function () { setOpen(true); });
  window.addEventListener('resize', function () { if (popOpen) { sizeOpen(); } });
  audio.addEventListener('ended', function () {
    if (idx < TRACKS.length - 1) { load(idx + 1, true, true); }
    else { done = true; showLine(); markSentence(); setOpen(false); }
  });
  if ('mediaSession' in navigator) {
    try {
      navigator.mediaSession.setActionHandler('nexttrack', goNext);
      navigator.mediaSession.setActionHandler('previoustrack', goBegin);
    } catch (e) { /* older browser: buttons still work */ }
  }
  load(0, false, false);
})();
"""

def load_playlist(date_str, recordings):
    """The playlist file for an edition, podcast/ai-stories-<date>.playlist.json
    (written by the podcast job): a JSON list of {title, slug, href} in
    edition order. Returns the track list only when every entry's slug
    stands in the recordings map with that entry's href as its standing
    recording — otherwise None, so the page falls back to the combined
    file's bare link (never a player with a dead track)."""
    path = PODCAST_DIR / f"ai-stories-{date_str}.playlist.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None
    if not isinstance(data, list) or not data:
        return None
    tracks = []
    for item in data:
        if not isinstance(item, dict):
            return None
        slug, title, href = item.get("slug"), item.get("title"), item.get("href")
        if not slug or not title or recordings.get(slug) != href:
            return None
        tracks.append({"title": title, "slug": slug, "href": href})
    return tracks

_ABBREV = {"mr", "mrs", "ms", "dr", "st", "vs", "etc", "e.g", "i.e",
           "u.s", "u.k", "no", "fig", "approx"}

def split_sentences(text):
    """Split one page paragraph into its sentences, each keeping its
    own ending punctuation. A plain punctuation rule with an
    abbreviation guard — exactness beyond this is not needed, since
    the sentence timings are proportional by word count anyway. The
    same split feeds both the printed sentence spans and the timing
    weights, so the lit sentence and the timing list never disagree."""
    text = " ".join((text or "").split())
    if not text:
        return []
    out, start = [], 0
    for m in re.finditer(r'[.!?]+["\u201d\u2019)\]]*\s+', text):
        end = m.end()
        nxt = text[end:end + 1]
        if not nxt or not (nxt.isupper() or nxt.isdigit() or nxt in '"\u201c('):
            continue
        wm = re.search(r"([A-Za-z][A-Za-z.]*)$", text[:m.start()])
        w = wm.group(1).lower() if wm else ""
        if len(w) == 1 or w in _ABBREV:
            continue
        out.append(text[start:end].strip())
        start = end
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return [s for s in out if s]

def probe_duration(mp3_path):
    """The recording's measured length in seconds (ffprobe), or None
    when it cannot be measured. A story with no measured length gets
    no sentence timings; the article follow alone applies to it —
    never a broken state."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(mp3_path)],
            capture_output=True, text=True, timeout=30)
        return float(r.stdout.strip())
    except Exception:
        return None

def _svg(inner):
    return ('<svg viewBox="0 0 48 48" aria-hidden="true" '
            f'focusable="false">{inner}</svg>')


_W = 'fill="#fff"'
# The seven white shapes, drawn exact (the admin's picture,
# 2026-11-10): story jumps carry a bar; the 10-second jumps carry a
# small "10" under the triangles, no bar. The block below is ONE
# black rounded bar with all seven buttons in one row inside it —
# no separate boxes, no grid, no colored or emoji icons.
ICON_BEGIN = _svg(
    f'<rect x="5" y="11" width="5" height="26" {_W}/>'
    f'<polygon points="25,11 10,24 25,37" {_W}/>'
    f'<polygon points="41,11 26,24 41,37" {_W}/>')
ICON_BACK = _svg(
    f'<polygon points="23,7 9,20 23,33" {_W}/>'
    f'<polygon points="40,7 26,20 40,33" {_W}/>'
    f'<text x="24" y="45" font-size="11" font-weight="bold" '
    f'font-family="Arial, Helvetica, sans-serif" '
    f'text-anchor="middle" {_W}>10</text>')
ICON_PLAY = _svg(f'<polygon points="17,10 38,24 17,38" {_W}/>')
ICON_PAUSE = _svg(
    f'<rect x="15" y="11" width="6.5" height="26" {_W}/>'
    f'<rect x="26.5" y="11" width="6.5" height="26" {_W}/>')
ICON_FWD = _svg(
    f'<polygon points="8,7 22,20 8,33" {_W}/>'
    f'<polygon points="25,7 39,20 25,33" {_W}/>'
    f'<text x="24" y="45" font-size="11" font-weight="bold" '
    f'font-family="Arial, Helvetica, sans-serif" '
    f'text-anchor="middle" {_W}>10</text>')
ICON_NEXT = _svg(
    f'<polygon points="7,11 22,24 7,37" {_W}/>'
    f'<polygon points="23,11 38,24 23,37" {_W}/>'
    f'<rect x="39" y="11" width="5" height="26" {_W}/>')
ICON_STOP = _svg(f'<rect x="12" y="12" width="24" height="24" {_W}/>')

# The bar's styles. The .wp-bar selectors outrank the older player
# rules wherever those still stand in the standing page's shell.
BAR_CSS = (
    '  .whole-player { text-align: center; margin: 14px auto 0; max-width: 980px; }\n'
    '  .whole-player .wp-bar { display: flex; flex-wrap: nowrap; '
    'align-items: flex-start; background: #111; border-radius: 60px; '
    'padding: 12px 14px; }\n'
    '  .whole-player .wp-bar .wp-btn { flex: 1 1 0; width: auto; min-width: 0; '
    'min-height: 0; margin: 0; padding: 3px 1px; background: transparent; '
    'border: none; border-radius: 16px; color: #fff; cursor: pointer; '
    'font-family: Arial, Helvetica, sans-serif; line-height: 1.25; }\n'
    '  .whole-player .wp-bar .wp-btn:active { background: #333; }\n'
    '  .whole-player .wp-bar .wp-btn .sym { display: block; line-height: 0; }\n'
    '  .whole-player .wp-bar .wp-btn .sym svg { width: 32px; height: 32px; }\n'
    '  .whole-player .wp-bar .wp-btn .word { display: block; font-size: 11px; '
    'font-weight: 400; margin-top: 3px; color: #fff; }\n'
    '  .whole-player #now-playing { font-weight: bold; margin: 10px 0 0; }\n'
    '  .whole-player .wp-time { margin: 2px 0 8px; '
    'font-variant-numeric: tabular-nums; }\n')

# The first follow-along styles (2026-11-10, superseded the same day
# by POPUP_CSS below when the pop-up form became the standard). Kept
# verbatim so a build can strip this exact block back out of a shell
# that carries it.
FOLLOW_CSS = (
    '  .whole-player #now-title { font-weight: bold; font-size: 1.12em; margin: 2px 0 0; }\n'
    '  .whole-player .wp-face.floating { position: fixed; top: 0; left: 0; right: 0; '
    'margin: 0 auto; max-width: 980px; z-index: 80; background: #efe6cb; '
    'border-bottom: 2px solid #8a6d3b; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.35); '
    'padding: 6px 8px 2px; }\n'
    '  .story-num { font-weight: bold; color: #7a1f1f; }\n'
    '  article.entry.playing { background: #fdf0c0; box-shadow: inset 0 0 0 2px #c89212; }\n'
    '  .sent-on { background: #ffd75e; }\n'
    '  h3[id^="story-"], .sent { scroll-margin-top: var(--wp-top, 12px); }\n')

# The pop-up form (the admin's settled standard, 2026-11-10): the
# bar does not stand open while anyone is only reading — the face
# (the SAME bar and its lines, one copy) stands hidden until a Listen
# tap pops it up as a floating window pinned to the top right of the
# screen, where it stays while listening; Stop, or the last story
# ending, hides it again. Its width is capped by the screen, so it
# stands fully on screen and tappable at phone width too. The rest
# is the follow-along set: the now-playing title line, the player
# number by a story's title, the light background over the whole
# article now playing, and the lit sentence inside it. Backgrounds
# and inset shadows only: the marks never move text around. The
# --wp-top variable is set by the player script to the open face's
# height, so followed content scrolls clear of the window.
POPUP_CSS = (
    '  .whole-player #now-title { font-weight: bold; font-size: 1.12em; margin: 2px 0 0; }\n'
    '  .whole-player .wp-face { display: none; }\n'
    '  .whole-player .wp-face.open { display: block; position: fixed; top: 10px; right: 10px; '
    'width: min(460px, calc(100vw - 20px)); z-index: 80; background: #efe6cb; '
    'border: 2px solid #8a6d3b; border-radius: 0.4rem; '
    'box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4); padding: 8px 10px 4px; }\n'
    '  .story-num { font-weight: bold; color: #7a1f1f; }\n'
    '  article.entry.playing { background: #fdf0c0; box-shadow: inset 0 0 0 2px #c89212; }\n'
    '  .sent-on { background: #ffd75e; }\n'
    '  h3[id^="story-"], .sent { scroll-margin-top: var(--wp-top, 12px); }\n')


def _btn(btn_id, icon, word):
    return (f'    <button class="wp-btn" id="{btn_id}" type="button">'
            f'<span class="sym">{icon}</span>'
            f'<span class="word">{word}</span></button>\n')


def whole_report_block(whole_href, tracks):
    """The whole-report listen block for the newest standing combined
    edition file (podcast/ai-stories-<date>.mp3), or "" when none stands
    — no standing file, no button, never a dead control. When a playlist
    file stands for that edition (podcast/ai-stories-<date>.playlist.json,
    every track verified against the story-audio manifest), the block is
    the playlist player instead: the approved seven-button set
    (2026-11-10) — Start of story or story before, Back 10 seconds,
    Play, Pause, Forward 10 seconds, Next story, Stop — with a
    "Story N of M" line, a now-playing title line, and a time line
    under the bar, stepping through the edition's per-story recordings
    in edition order, with the combined file kept as a plain link
    under the player (the admin's Skip order, 2026-11-09, widened to
    the full control set the same day; the look is the admin's own
    picture, 2026-11-10: one black rounded bar, all seven in one row,
    plain white SVG shapes with the plain word in small white text
    under each). The pop-up form is the standard (the admin's order,
    2026-11-10): the bar does not stand open while anyone is only
    reading — the block shows the whole-report listen entry (the way
    to start from story 1) and the one-file line, and the bar and its
    lines ride hidden in one .wp-face wrapper until a Listen tap —
    the entry's, or any story's own Listen link — starts the player
    and pops that same face up as a floating window pinned to the
    top right of the screen; Stop, or the last story ending, hides
    it again. The same bar moved, never a second copy. The player
    script carries the edition-audio marker and rides inside this
    block, so the shell cleanups remove it whole on the next build."""
    if not tracks:
        if not whole_href:
            return "", None
        block = (f'\n  <div class="listen">\n'
                 f'    <a class="whole-listen" href="{whole_href}">&#9654; Listen to the whole report</a>\n'
                 f'  </div>')
        return block, whole_href
    script = PLAYER_JS_TEMPLATE.replace("__PLAYLIST__", json.dumps(tracks, indent=2))
    alt_line = ""
    if whole_href:
        alt_line = (f'    <p class="wp-alt">Or hear this edition as one file: '
                    f'<a href="{whole_href}">the whole report in one recording</a></p>\n')
    block = (f'\n  <div class="listen whole-player">\n'
             f'    <button class="whole-listen" id="btn-start-all" type="button">&#9654; Listen to the whole report</button>\n'
             + alt_line
             + f'    <div class="wp-face">\n'
             f'    <div class="wp-bar">\n'
             + _btn('btn-begin', ICON_BEGIN, 'Start of story or story before')
             + _btn('btn-back', ICON_BACK, 'Back 10 seconds')
             + _btn('btn-play', ICON_PLAY, 'Play')
             + _btn('btn-pause', ICON_PAUSE, 'Pause')
             + _btn('btn-fwd', ICON_FWD, 'Forward 10 seconds')
             + _btn('btn-next', ICON_NEXT, 'Next story')
             + _btn('btn-stop', ICON_STOP, 'Stop')
             + f'    </div>\n'
             f'    <p id="now-playing">Story 1 of {len(tracks)}</p>\n'
             f'    <p id="now-title">{esc(tracks[0]["title"])}</p>\n'
             f'    <p class="wp-time" id="time-line">0:00 of 0:00</p>\n'
             f'    </div>\n'
             f'    <audio id="edition-audio" preload="metadata"></audio>\n'
             f'<script>\n{script}</script>\n'
             f'  </div>')
    return block, whole_href

def render_entry(e, kind, recording_href=None, num=None, anchor_slug=None,
                 sent_paras=None):
    cls = "entry solved" if e["solved"] else "entry"
    tag = ' <span class="solved-tag">Solved</span>' if e["solved"] else ""
    listen = ""
    if recording_href:
        # The data-story mark lets the player script start the player
        # at this story when the link is tapped (the pop-up form,
        # 2026-11-10); the href stays as the plain road to the
        # recording when no script runs.
        story_attr = f' data-story="{anchor_slug}"' if anchor_slug else ""
        listen = (f' <a class="story-listen" href="{esc(recording_href)}"{story_attr} '
                  f'aria-label="Listen to {esc(e["title"])}">&#9654; Listen</a>')
    # A playlist entry (the follow-along set, 2026-11-10): its player
    # number stands by its title — the same N the player shows — and
    # its title carries the anchor the player follows. The number is
    # an added mark; no article word changes.
    num_span = f'<span class="story-num">{num}.</span> ' if num else ""
    id_attr = f' id="story-{anchor_slug}"' if anchor_slug else ""
    out = [f'<article class="{cls}">',
           f'<h3{id_attr}>{num_span}{esc(e["title"])}{tag}{listen}</h3>']
    for j, p in enumerate(e["body"]):
        sents = (sent_paras[j]
                 if sent_paras is not None and j < len(sent_paras) else None)
        if sents:
            out.append("<p>" + " ".join(
                f'<span class="sent">{linkify(s, label="link")}</span>'
                for s in sents) + "</p>")
        else:
            out.append(f"<p>{linkify(p, label='link')}</p>")
    if kind in ("problems", "quiet") and e["last_activity"]:
        sents = (sent_paras[len(e["body"])]
                 if sent_paras is not None
                 and len(sent_paras) > len(e["body"]) else None)
        if sents:
            out.append("<p>" + " ".join(
                f'<span class="sent">{esc(s)}</span>' for s in sents) + "</p>")
        else:
            out.append(f"<p>{esc(e['last_activity'])}</p>")
    if e["sources"]:
        out.append('<div class="sources">')
        for s in e["sources"]:
            out.append(f"<p>{linkify(s)}</p>")
        out.append("</div>")
    out.append("</article>")
    return "\n".join(out)

def main():
    parser = argparse.ArgumentParser(description="Build the newspaper page")
    parser.add_argument("output", nargs="?", type=Path, default=PAGE)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--audio-dir", type=Path, default=AUDIO_DIR)
    args = parser.parse_args()
    out_path = args.output
    topics, problems, quiet = parse_entries(SRC.read_text())
    ordered = topics + problems + quiet
    slugs = assign_entry_slugs(ordered)
    slug_by_id = {id(entry): slug for entry, slug in zip(ordered, slugs)}
    recordings = load_recordings(args.manifest, args.audio_dir)
    # The follow-along set (2026-11-10): the player's track list is
    # computed ONCE here — every entry with a standing recording, in
    # page order (topics, problems, quiet problems) — and everything
    # derives from that one ordered list: the player's tracks, each
    # article's player number, and the sentence timings, so the
    # numbers on the page and the numbers in the player can never
    # disagree, and every story's Listen link can start the player
    # at that story. The newest combined edition file stands as the
    # one-file link at the top.
    whole_href = None
    edition_files = sorted(PODCAST_DIR.glob("ai-stories-*.mp3"))
    if edition_files:
        whole_href = f"podcast/{edition_files[-1].name}"
    entry_by_slug = {}
    kind_by_slug = {}
    for kind_name, group_entries in (("topics", topics),
                                     ("problems", problems),
                                     ("quiet", quiet)):
        for e in group_entries:
            s = slug_by_id[id(e)]
            entry_by_slug[s] = e
            kind_by_slug[s] = kind_name
    tracks = []
    for e in ordered:
        s = slug_by_id[id(e)]
        if recordings.get(s):
            tracks.append({"title": e["title"], "slug": s,
                           "href": recordings[s]})
    plans = {}
    if tracks:
        for i, tr in enumerate(tracks):
            e = entry_by_slug[tr["slug"]]
            plan = {"num": i + 1, "sent_paras": None}
            texts = list(e["body"])
            if kind_by_slug[tr["slug"]] in ("problems", "quiet") \
                    and e["last_activity"]:
                texts.append(e["last_activity"])
            paras = [split_sentences(t) for t in texts]
            dur = probe_duration(args.audio_dir / f"{tr['slug']}.mp3")
            if dur:
                counts = [max(1, len(e["title"].split()))]
                counts += [max(1, len(s.split()))
                           for para in paras for s in para]
                total = sum(counts)
                edges, acc = [], 0.0
                for c in counts:
                    acc += dur * c / total
                    edges.append(round(acc, 2))
                tr["t0"] = edges[0]
                tr["ends"] = edges[1:]
                plan["sent_paras"] = paras
            plans[tr["slug"]] = plan
    solved = sum(1 for e in topics + problems + quiet if e["solved"])
    n_problems = len(problems) + len(quiet)
    print(f"parsed: {len(topics)} topics, {n_problems} problems ({len(quiet)} quiet), {solved} solved")

    old = PAGE.read_text()
    arts = [m.span() for m in re.finditer(r'<article class="[^"]*">.*?</article>', old, re.S)]
    assert arts, "standing page holds no articles — shell source is not the newspaper page"
    # Shell segments are found from the standing page's own part headers, so
    # any edition's counts work: the Part 2 furniture sits between the last
    # topic article and the first problem article; the quiet furniture sits
    # between the last problem article and the first quiet article.
    pos_part2 = old.index('<h2 class="part">Part 2')
    pos_quiet = old.index('<h3 class="subhead">Quiet problems</h3>')
    i_part2 = next(i for i, s in enumerate(arts) if s[0] > pos_part2)
    i_quiet = next(i for i, s in enumerate(arts) if s[0] > pos_quiet)
    seg_head = old[:arts[0][0]]
    seg_part2 = old[arts[i_part2 - 1][1]:arts[i_part2][0]]
    seg_quiet = old[arts[i_quiet - 1][1]:arts[i_quiet][0]]
    seg_tail = old[arts[-1][1]:]
    assert "Part 2" in seg_part2 and "Quiet problems" in seg_quiet
    # A whole-report listen block carried in the old shell is removed
    # exactly, leaving the masthead, counts line, headline, standfirst,
    # and full-record line untouched — then the block is rebuilt fresh
    # below, against the newest standing combined edition file.
    # The player block carries a nested bar <div>, so its strip must
    # run to the block's script end, not the first </div>; the plain
    # fallback link block (no script) takes the short form.
    seg_head, listen_blocks = re.subn(
        r'\s*<div class="listen[^"]*">.*?</script>\s*</div>', "", seg_head, count=1, flags=re.S)
    if not listen_blocks:
        seg_head, listen_blocks = re.subn(
            r'\s*<div class="listen[^"]*">.*?</div>', "", seg_head, count=1, flags=re.S)
    # The whole-report button (the admin's order, 2026-11-06): one button
    # near the top, under the full-record line, playing the whole edition
    # through the combined file the podcast job made most recently.
    whole_block, whole_href = whole_report_block(whole_href, tracks)
    if whole_block:
        m_rec = re.search(r'(<p class="record-line">.*?</p>)', seg_head, re.S)
        if m_rec:
            seg_head = seg_head[:m_rec.end()] + whole_block + seg_head[m_rec.end():]
        else:
            seg_head = seg_head.replace(
                '<h2 class="headline">', whole_block + '\n  <h2 class="headline">', 1)
        # Its button style is part of the shell. Add it once; later
        # builds read the generated page as their shell and must not
        # stack a second copy.
        if ".whole-listen" not in seg_head:
            whole_listen_css = (
                '  .listen a.whole-listen { display: inline-block; '
                'font-size: clamp(1.2rem, 4vw, 1.6rem); font-weight: bold; '
                'padding: 0.7rem 1.6rem; background: #7a1f1f; color: #fff8ea; '
                'border: 2px solid #5c1515; border-radius: 0.4rem; '
                'text-decoration: none; line-height: 1.5; }\n'
                '  .listen a.whole-listen:active { background: #5c1515; }\n')
            seg_head = seg_head.replace("</style>", whole_listen_css + "</style>", 1)
        # The playlist player's styles ride the same one-time pattern
        # (the admin's Skip order, 2026-11-09): added only on a build
        # whose block is the player, and never stacked twice.
        if "whole-player" in whole_block and ".wp-bar {" not in seg_head:
            seg_head = seg_head.replace("</style>", BAR_CSS + "</style>", 1)
        # The bar look's styles (2026-11-10, the admin's picture):
        # one black rounded bar, one row, white shapes and words.
        # Guarded by the .wp-bar rule marker so shells built with an
        # older player gain them once.
        if "whole-player" in whole_block and ".wp-bar {" not in seg_head:
            seg_head = seg_head.replace("</style>", BAR_CSS + "</style>", 1)
        # A shell carrying the first follow-along styles loses them
        # here — POPUP_CSS carries the set now (2026-11-10).
        if FOLLOW_CSS in seg_head:
            seg_head = seg_head.replace(FOLLOW_CSS, "", 1)
        # The pop-up styles ride the same one-time pattern, under
        # their own guard.
        if "whole-player" in whole_block and ".wp-face.open {" not in seg_head:
            seg_head = seg_head.replace("</style>", POPUP_CSS + "</style>", 1)
    # Its dedicated script rides in the tail of the old shell. Remove a
    # script block only when it is the combined edition control's script.
    # The playlist player's script (2026-11-09) carries the same
    # edition-audio marker and rides inside the .listen block in the
    # head, which the listen-block cleanup above removes whole; this
    # tail pass still strips any marked script that lands in the tail.
    seg_tail = re.sub(
        r'\s*<script>(?:(?!</script>).)*(?:listen-btn|edition-audio)'
        r'(?:(?!</script>).)*</script>',
        "", seg_tail, flags=re.S)
    # The per-story control's style is part of the new shell. Add it once;
    # later builds read the generated page as their shell and must not
    # stack a second copy.
    if ".story-listen" not in seg_head:
        story_listen_css = (
            '  .story-listen { display: inline-block; margin-left: 0.45rem; '
            'padding: 0.12rem 0.55rem; background: #7a1f1f; color: #fff8ea; '
            'border: 1.5px solid #5c1515; border-radius: 0.35rem; '
            'font-size: 0.78rem; font-weight: bold; line-height: 1.35; '
            'text-decoration: none; vertical-align: middle; white-space: nowrap; }\n'
            '  .story-listen:active { background: #5c1515; }\n')
        seg_head = seg_head.replace("</style>", story_listen_css + "</style>", 1)
    # The counts line in the head is mechanical: roll it to tonight's counts.
    seg_head = re.sub(
        r"In this report: \d+ topics and \d+ problems from the Muse AI communities\. \d+ problems? solved so far\.",
        f"In this report: {len(topics)} topics and {n_problems} problems from the Muse AI communities. {solved} problem{'s' if solved != 1 else ''} solved so far.",
        seg_head)
    # The full-record PDF link rolls to the newest night PDF on disk.
    night_pdfs = sorted(BASE.glob("report-on-muse-ai-communities-*-night.pdf"))
    if night_pdfs:
        seg_head = re.sub(r'href="report-on-muse-ai-communities-[^"]*-night\.pdf"',
                          f'href="{night_pdfs[-1].name}"', seg_head)

    def render_with_plan(e, kind):
        slug = slug_by_id[id(e)]
        plan = plans.get(slug)
        return render_entry(
            e, kind, recordings.get(slug),
            num=plan["num"] if plan else None,
            anchor_slug=slug if plan else None,
            sent_paras=plan["sent_paras"] if plan else None)

    doc = (seg_head
           + "\n".join(render_with_plan(e, "topics") for e in topics)
           + seg_part2
           + "\n".join(render_with_plan(e, "problems") for e in problems)
           + seg_quiet
           + "\n".join(render_with_plan(e, "quiet") for e in quiet)
           + seg_tail)
    out_path.write_text(doc)
    print(f"wrote {out_path} ({len(doc)} bytes)")
    print(f"story listen links: {doc.count('class=\"story-listen\"')}")
    if tracks:
        n_timed = sum(1 for t in tracks if "ends" in t)
        print(f"follow: {len(plans)} of {len(tracks)} player stories "
              f"numbered, {n_timed} with sentence timings, "
              f"{doc.count('class=\"story-num\"')} numbers printed, "
              f"{doc.count('class=\"sent\"')} sentence spans")
    print(f"whole-report button: {whole_href if whole_href else 'none — no combined edition file stands'}")

if __name__ == "__main__":
    main()
