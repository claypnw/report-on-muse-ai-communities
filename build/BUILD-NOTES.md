# Build notes — AI community report machinery

These programs, from the community check's working folder on Muse's side, make this site's pieces:
- `build/build_newspaper_page.py` — builds the newspaper page (index.html) from the check's state.
- `build/make_report_pdf.py` — builds the nightly report PDF from the same state.
- `build/build_stories_json.py` — builds the story list the audio and pages read.
- `build/story_audio_common.py` and `build/make_story_audio.py` — make the AI stories podcast audio and its playlist.
- `build/skip-list/` — the skip-list programs (fetch_skip_list.py, fetch_skip_issues.py, fetch_talk_issues.py, fold_skip_list.py) keep the list of sources and items the check skips.
The check itself is agent-run each night; these are the programs its steps call.
