# A- C13B0 Automation v1

A- source: README blob b44236b3e2521045755e2ecf440bcd35ab7ba7c1, particularly lines 790–850, 2329–2398, 2905–2911 and 3093–3109. This implementation preserves the README. It indexes actual tracked source paths at an exact remote default-branch SHA, watches the newest 30 workflow runs per repository (not an exhaustive history), stores attempts and checkpoints in private SQLite, and implements the fixed GH-1 sequence with ordinary SHA-256 receipts. GH-1 is a reversible transform, not encryption or authentication.

Requires Python 3 and authenticated GitHub CLI (`gh`). No npm, paid API, Cloudflare service, device storage scanning or ADB required. Remote observation is read-only. It does not rerun failures, execute repository README snippets, modify credentials, merge or deploy. Existing Moltnook repository-engine remains the signed build/repair path. Local status is not production acceptance.

Run tests: `python -m unittest -v` in this directory. Run `python automation.py once`, `python automation.py loop --interval 300`, `python automation.py status`, `python automation.py index`, or `python automation.py hash FILE`. Runtime state is in `~/.infinity/a-automation/ledger.sqlite3`. A `stop` file requests graceful loop shutdown. Delete it before restarting. Local runtime logs and database must not be committed.
