#!/usr/bin/env python3
"""Parse report-on-muse-ai-communities.md into replacestories JSON, excluding skip-list titles.
Output: /tmp/stories.json  {"stories":[...]} matching menu-2 replacestories schema.
Body = paragraph text joined. sourceLine = bullet lines starting with Source:/Sources: flattened.
"""
import json, re
from pathlib import Path
base = Path.home()/"workspace/learning/community-check"
src = (base/"report-on-muse-ai-communities.md").read_text()
skip_file = base/"skip-list/skip-list-current.txt"
skips=set()
if skip_file.exists():
    for ln in skip_file.read_text().splitlines():
        t=ln.split("|")[0].strip()
        if t: skips.add(t)
lines=src.splitlines()
stories=[]
kind=None
entry=None
def flush():
    global entry
    if entry is None: return
    if entry["title"] not in skips:
        # join paras
        entry["body"]=" ".join(entry.pop("paras"))
        stories.append(entry)
    entry=None
i=0
cur=None
while i < len(lines):
    ln=lines[i]
    if ln.startswith("## Part 1"): flush(); cur="topic"; i+=1; continue
    if ln.startswith("## Part 2"): flush(); cur="problem"; i+=1; continue
    if ln.startswith("New and different things people are doing") or ln.startswith("Problems people are reporting with Muse, ordered"): i+=1; continue
    if ln.startswith("### "):
        flush()
        t=ln[4:].strip()
        if t=="Quiet problems":
            entry=None; i+=1; continue
        entry={"kind":cur,"title":t,"paras":[],"sourceLine":"","firstSeen":"","lastDate":"","state":""}
        i+=1; continue
    if entry is not None:
        if ln.startswith("- Source"):
            # a source block: the line itself may carry a source, and/or
            # indented bullets below it carry one source each; later
            # "- Sources (added ...)" blocks append to the same line
            head=ln[2:].strip()
            head=re.sub(r"^Sources?\s*(\([^)]*\))?:\s*","",head)
            parts=[head] if head else []
            i+=1
            while i < len(lines) and lines[i].startswith("  - "):
                parts.append(lines[i].strip()[2:]); i+=1
            txt=" · ".join(parts)
            if entry["sourceLine"]:
                entry["sourceLine"]+=" · "+txt
            else:
                entry["sourceLine"]=txt
            continue
        if ln.startswith("- First seen:"):
            entry["firstSeen"]=ln.split(":",1)[1].strip() if ":" in ln else ""; i+=1; continue
        if ln.startswith("- Last updated:") or ln.startswith("- Last activity:"):
            # value may contain parenthetical; take date YYYY-MM-DD prefix
            v=ln.split(":",1)[1].strip()
            m=re.match(r"(\d{4}-\d{2}-\d{2})",v)
            entry["lastDate"]=m.group(1) if m else v; i+=1; continue
        if ln.startswith("- State:"):
            entry["state"]=ln.split(":",1)[1].strip(); i+=1; continue
        if ln.strip() and not ln.startswith("- ") and not ln.startswith("#"):
            entry["paras"].append(ln.strip()); i+=1; continue
    i+=1
flush()
Path("/tmp/stories.json").write_text(json.dumps({"stories":stories},ensure_ascii=False,indent=1))
print(f"{len(stories)} stories written, skips excluded: {sorted(skips)}")
for s in stories: print(s["kind"], "|", s["title"], "|", s["firstSeen"], s["lastDate"], "|", s["state"][:60])
