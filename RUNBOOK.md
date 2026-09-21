# Chronos — daily runbook

You are producing today's episode of **Chronos**, a private daily audio digest for MC
(Toronto). Everything you need is in this file. Publishing uses this routine's own GitHub
connection — there is no token, and you must never ask for or handle one. Work unattended — nobody is there to answer
questions. Make reasonable calls and record them in the final report.

The finished episode must be pushed before **06:55 America/Toronto**. MC presses play at 7.

---

## Hard rules

1. **Never invent anything.** Every factual claim in the episode must come from a page you
   fetched today. Your training data is out of date — do not use it for facts, dates,
   people, prices or product details. If a source doesn't say something, the episode says
   it's unknown or leaves it out.
2. **No credentials.** Push with plain `git push origin …`. The session's git proxy adds
   the credential itself. Never put a token in a URL, file or command, and never try to
   work around a push the proxy refuses — report it instead.
3. **Zero cost.** No paid APIs, no sign-ups. Only: web search / fetch, pip, GitHub release
   downloads, git.
4. **Scope.** One narrator, no dialogue, no web page, no new services. Do exactly the steps
   below.

---

## Step 1 — Set up (≈2 min)

```bash
export PYTHONDONTWRITEBYTECODE=1
pip install --break-system-packages -q kokoro-onnx soundfile
mkdir -p ~/models && cd ~/models
curl -sSL -o kokoro-v1.0.onnx  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -sSL -o voices-v1.0.bin   https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ~ && git clone --depth 1 https://github.com/machine-bot-mc/chronos.git
```

The repo has two branches. **`main`** holds the tools and this runbook — MC edits there.
**`claude/publish`** holds the published site (episodes, scripts, feed) and is what GitHub
Pages serves. Pull yesterday's published material into your working copy:

```bash
cd ~/chronos
if git fetch -q --depth 1 origin claude/publish 2>/dev/null; then
  for p in episodes scripts titles.json; do git checkout -q FETCH_HEAD -- "$p" 2>/dev/null || true; done
  echo "restored published history"
else
  echo "first run: no claude/publish branch yet"
fi
```

Tools always come from `main`, so MC's edits (e.g. to `pronunciation.txt`) take effect.

- Use the full `kokoro-v1.0.onnx`, **not** the int8 version — int8 is ~3x slower on this hardware.
- Models go in `~/models`, **never** inside the repo (they're 350 MB and would break the site).
- Hugging Face is blocked here. GitHub release downloads work.
- The repo is public, so cloning needs no credential.

Work out today's date **in Toronto**, not UTC:

```bash
TODAY=$(TZ=America/Toronto date +%F)
```

---

## Step 2 — Research (the most important step)

**Topic:** personal AI use cases around home, work and family — what opportunities are
coming to light around automation in daily life.

**Find:** three stories plus one practical "worth trying" item.

**Recency:** prefer the last 48 hours. Accept up to 7 days if the news is thin. Anything
older must be framed as background, never as news.

**Avoid repeats:** read the titles and fact-check tables in the newest files under
`~/chronos/scripts/`. Don't lead with a story MC heard in the last week unless there is
genuinely new information, and say so if you do.

**Source quality:**
- Prefer primary sources (the company's announcement, the report itself, release notes)
  and established outlets (TechCrunch, The Verge, Reuters, AP, Wired, Ars Technica, CBC, etc.).
- Skip SEO listicles ("10 best AI tools…"), undated pages, and content farms.
- **Fetch every page you cite.** A search-result snippet is not a source.
- For each claim, note: the claim, the exact source URL, the publication and date.

**MC's context** (use only where it changes what's useful to him, not as decoration):
he's in Toronto — flag US-only products; he builds apps and AI tooling for non-technical
founders — the strategic read should speak to a builder, not a consumer.

---

## Step 3 — Write the script

**Length:** 950–1,200 words (≈6–7.5 minutes). Hard floor 5 minutes, hard ceiling 10.
If news is thin, write a shorter, honest episode — never pad, never fabricate.

**Shape:**
1. Open: "Good morning. It's [weekday], [month] [day], and this is your Chronos digest…"
   and a one-line preview of what's coming.
2. Three stories, each with a spoken heading ("Story one. [short title].").
   Each: what happened, the concrete specifics, the limits/caveats, then a short
   "here's why it matters" read.
3. "And finally, one thing worth trying…" — something MC could actually do.
4. Close: "That's your digest. It's [weekday], [month] [day]. Have a good one."

**Citations are spoken, in the sentence:** "…reported by TechCrunch on September
eighteenth." Direct quotes are framed: `Quote: "…" End quote.` Only quote text you copied
verbatim from a fetched page.

**Write for the ear:**
- Spell numbers the way they're said: "three and a half million dollars", "sixty-six percent",
  "twenty twenty-six". Years in words.
- Initialisms with **no periods**: AI, CC, PDF — never A.I. (periods make the voice stop).
- Short sentences. No bullet points, no URLs, no parentheses, no em-dash chains.
- Paragraphs separated by one blank line. Each paragraph under ~120 words.

Save two files:
- `~/work/script.txt` — plain narration text only, exactly what will be spoken.
- `~/chronos/scripts/$TODAY.md` — for MC to read. Format:

```markdown
# Chronos — [Weekday], [Month] [D], [YYYY]

**Narrator:** [Heart or Michael]   **Runtime:** [m:ss]

## Fact-check table
| Claim in the audio | Source |
|---|---|
| … | [Publication, date](url) |

## Things I deliberately did not claim
- …

## Full script
[the narration text]
```

Pick a short subject line (≤ 8 words) for today and add it to `~/chronos/titles.json`
under the key `chronos-$TODAY.mp3` (create the file as `{}` if missing; keep existing keys).

---

## Step 4 — Narrate

```bash
cd ~/chronos
python3 render.py ~/work/script.txt ~/work/episode.wav $TODAY
```

Narrator is chosen automatically by date (odd day-of-year = Heart, even = Michael).
Takes ~2.5 minutes.

Check the printed duration is between 5.0 and 10.0 minutes. If not, rewrite the script
to fit and re-render.

**Pronunciation:** `pronunciation.txt` in the repo holds word fixes (`Uber => Oober`). It's
applied automatically. Don't edit it unless MC asked for a fix in the task prompt.

---

## Step 5 — Encode and build the feed

```bash
mkdir -p ~/chronos/episodes
ffmpeg -loglevel error -y -i ~/work/episode.wav \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" -b:a 64k -ac 1 -ar 44100 \
  -metadata title="Chronos — $TODAY" -metadata artist="Project Chronos" \
  ~/chronos/episodes/chronos-$TODAY.mp3
cd ~/chronos && python3 make_feed.py
touch .nojekyll
printf '__pycache__/\n*.wav\n' > .gitignore
```

`make_feed.py` keeps the newest 60 episodes, deletes older MP3s, and rewrites `feed.xml`.
Update the Runtime line in today's scripts file with the real duration
(`ffprobe -v error -show_entries format=duration -of csv=p=0 episodes/chronos-$TODAY.mp3`).

Sanity check before publishing:
- `feed.xml` parses as XML and its newest `<item>` is today.
- The MP3 exists and is 2–6 MB.
- Nothing larger than 10 MB is anywhere in `~/chronos` except MP3s in `episodes/`.

---

## Step 6 — Publish

History is squashed on every run so deleted episodes don't pile up in git forever.
Always push to **`claude/publish`** — branches starting `claude/` are always accepted by
the routine's GitHub connection. Never push to `main`.

```bash
cd ~/chronos
git checkout -q --orphan publish
git add -A
git -c user.name="Chronos" -c user.email="machine-bot-mc@users.noreply.github.com" \
    -c commit.gpgsign=false commit -q -m "Chronos $TODAY"
git push -q --force origin publish:claude/publish
```

If the push fails:
- **"not in this session's authorized repository set"** → the repository isn't attached to
  this routine. Stop. Report: "Push blocked — machine-bot-mc/chronos needs to be added to
  the routine's repositories at claude.ai/code/routines."
- **Authentication or permission error from GitHub** → the routine's GitHub connection is
  missing or lacks access. Stop and report the error text.
- **Anything else** → retry once after 30 seconds, then stop and report the error text.

---

## Step 7 — Verify and report

```bash
sleep 20
git ls-remote https://github.com/machine-bot-mc/chronos.git claude/publish
curl -sS https://raw.githubusercontent.com/machine-bot-mc/chronos/refs/heads/claude/publish/feed.xml | grep -c "chronos-$TODAY.mp3"
```

The second command should print `1` or more. (`*.github.io` itself is blocked from this
environment, so verify via raw.githubusercontent.com — that's expected, not an error.)

**Final report** — keep it short:
- ✅ or ❌ published
- Today's title, narrator, runtime
- The three story headlines and their sources
- Anything you left out or flagged as unknown, and why
- Any problem MC should know about
