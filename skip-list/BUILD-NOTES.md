# Skip list build — notes

Ordered by the admin, 2026-10-22 (his go in chat, then the button tap "Build the checkbox and the skip list").

## What it is

On the Report on Muse AI Communities web page, each story (topic or problem)
carries a checkbox: "Do not include this story again." A check sends the story
to a small program in the admin's Google account, which writes it to a skip list.
The Daily website review of AI reads the list at the start of every run and
leaves those stories out of the report, even if they are still out there.
At the bottom of the page, a section "Stories you have told me to skip" lists
what is on the list; taking a check off there puts a story back.

## Pieces

1. The page — `make_report_pdf.py` in the parent folder, `page` form:
   each story box shows its title, a dates line (first seen, last updated,
   taken from the record's own bullets), and the checkbox. A story is named
   by its exact title in the record. Until the program's address is set in
   `program-url.txt`, every checkbox sits off with the note "the skip program
   is not set up yet" — the page never pretends a check went somewhere.
   The send uses a finished-send-counts-as-sent road (the program's answer
   cannot be read back by the page; same road as the family album doorbell);
   the proof either way is the next run's fetched list.
2. The program — `skip_program.gs` in this folder: runs in the admin's Google
   account at deploy time. Holds one Sheet named "Skip list", one row per
   story: Title | First seen | Last updated | Date skipped. A repeated skip
   adds no second row. The read key is set at deploy and kept only in
   `program-key.txt` on Dude's side.
3. The list format — plain lines, one per story:
   `Title | First seen | Last updated | Date skipped`
   The job's fetched copy lives at `skip-list-current.txt` in this folder.
4. The job wiring — NOT YET SAVED. It goes in only after the program is live
   and the end-to-end hand test passes (the admin's standard: first runs by hand).
   Planned step 0 for the Daily website review of AI: fetch the list with the
   key, save it as `skip-list-current.txt`; leave out every story whose title
   is on the list; the dated log carries one line, "Skipped by the admin's list: N"
   with the titles; the publish step rebuilds the page form with the fetched
   list and replaces index.html in the repository.

## First check — SEND BACK, and the fixes (2026-10-22)

The pre-production check (a fresh reviewer, the admin's standing rule) sent the
first build back with 9 findings. All 9 are answered in the build except
finding 6, which is the admin's decision (see the end of this section).

1. Apostrophe titles broke the send code (titles sat inside quoted script
   strings). Fixed: titles and dates now ride in data attributes on the
   checkbox; one listener reads them. Both apostrophe titles in today's
   record come out escaped and whole.
2. A skipped story still showed in the page and its counts. Fixed: in the
   page form, a story on the list is left out of the body and the counts;
   it shows only in the bottom put-it-back section.
3. Problems name their second date "Last activity," not "Last updated," and
   the page showed it blank. Fixed: the dates line uses the right name for
   each kind, and the skip sends that date.
4. A check could be lost while the page looked settled. Fixed: the box is
   locked while the send runs; a failed send restores the box and says so;
   a finished send marks the box "Sent" with the words "If it is still here
   after that run, the skip did not land" — the list read at the next run
   is the stated proof, never the click itself.
5. Two checks landing together could write two rows; a sheet without its
   header hid its first story. Fixed: the program takes a lock before it
   reads and writes, and it puts the header in if it is missing.
6. OPEN — the admin's decision: the report page is public, so the program's
   address is public with it; anyone who finds the address could send a
   skip or a put-back. The harm is bounded (the list shows at the bottom of
   the page, and the run's log counts skips), and there is no way to ask
   the page for a secret without printing the secret on the public page.
   The admin accepts it in writing, or the build changes shape.
7. A wrong key's answer could be mistaken for an empty list. Fixed:
   `fetch_skip_list.py` in this folder keeps four outcomes apart — valid
   list written (an empty list counts), no settings, bad answer, no
   answer — and a failed fetch never writes over the known list.
8. The sample claim could not be rebuilt from the stated road. Fixed:
   `python3 make_report_pdf.py page sample` builds from `test-sample.txt`.
9. The bottom put-it-back boxes ignored the not-set-up state. Fixed: with
   no program address, both sets of boxes sit off with the same wording.

## Hand tests so far (2026-10-22)

- Page form built from today's record: 27 checkboxes (16 topics + 11
  problems), all off with the not-set-up note; dates line present on the
  entries. Counts read from the built file, and page 1 looked at as a
  picture: title, dates, checkbox, story, bullets in that order. Sample
  list kept as `test-sample.txt` — it is a test piece, not the admin's list;
  the live list starts empty.
- After the fixes, with the sample list (its title corrected to the
  record's exact full title): the sample story is out of the body, the
  page counts read 15 topics, and the story shows once in the bottom
  section. With a test program address: 26 working skip boxes and 1
  put-it-back box; the test address was taken back out afterward.
- Fetch program, tested against a stand-in program on this machine, five
  cases: no settings (stops, code 3); good key (list written, OK 2);
  empty list (written empty, OK 0); wrong key (BAD ANSWER, code 4, the
  old list untouched); program unreachable (NO ANSWER, code 5, the old
  list untouched).
- Print form unchanged: the PDF carries no checkboxes (a printed page cannot
  send a check), and its counts still read 16 topics and 11 problems.

## Deploy (needs the admin at his Chrome — his own Google account)

Written as its own step list when the code clears review, checked against
his screen at that time: make a Sheet, open its program editor, paste
`skip_program.gs`, set the read key, deploy as a web program open to anyone
with the address, copy the address into `program-url.txt` and the key into
`program-key.txt` on Dude's side. Then the hand test: skip one story from
the live page, fetch the list, see the story on it; put it back; fetch
again; then save the job wiring and hand-run the check once.

## Finding 6 — closed (2026-10-22)

The admin accepted the public address in writing in the main chat at 4:07 PM
Arizona time: "Go ahead with the public address." The deploy may proceed.

## Secrets note (2026-10-22)

`program-key.txt` and `program-url.txt` in this folder are NOT escrow
material — same class as the doorbell secret keys. The master program file
keeps the placeholder SET-AT-DEPLOY; the key lives only in the paste copy
The admin put into his account and in `program-key.txt` on Dude's side.

## Road changed — built in Muse instead (the admin, 2026-10-22, 4:13–4:16 PM)

The admin's preference: keep the application close to where it is developed. The
lists will live in a Muse app (a page with its own stored records, in his
Muse environment), with a menu as its front door. The Google program above
is the road not taken — kept here as the record of the design that cleared
review. Nothing was deployed to Google; the 12 steps were sent and paused,
and the paste copy and the read key were deleted the same day (the key was
never used anywhere).

## 2026-10-30 — the road Clay chose: the button in the report's own repository
- The Google deploy is STOPPED for good. It would run a copy of production in Google, against Clay's rule (2026-10-15): one source of production, GitHub. Raised by Clay 2026-10-30; the assistant had presented the Google road as fine without naming the clash — recorded here as the miss it was.
- The master program file and these notes were published into claypnw/report-on-muse-ai-communities (skip-list/) on 2026-10-30, commits 00cf1833 and e5f09d05, VERDICT: PASS. The Google program stays in the repository as the design record; it is not deployed.
- CHOSEN ROAD (Clay's tap, 2026-10-30 06:48): each story on the report page carries a button; the button opens a ready-filled note (a GitHub issue) in claypnw/report-on-muse-ai-communities in Clay's Chrome, where he is signed in; he taps Submit; the nightly job reads the notes there — only notes written by the repository owner count — and leaves those stories out from the next run on.
- First step is a test-stand proof: the job's read of the notes (the GitHub token's Issues read is the unproven piece), and the button on the TEST page only. The live page is touched only after the proof passes and Clay approves the tested page.
