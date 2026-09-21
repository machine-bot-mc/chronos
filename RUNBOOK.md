# Chronos — daily runbook

You are producing today's episode of **Chronos**, a private daily audio digest for MC
(Toronto). The scheduled task that started you supplies one secret: a GitHub token.
Everything else you need is in this file. Work unattended — nobody is there to answer
questions. Make reasonable calls and record them in the final report.

The finished episode must be pushed before **06:55 America/Toronto**. MC presses play at 7.

---

## Hard rules

1. **Never invent anything.** Every factual claim in the episode must come from a page you
   fetched today. Your training data is out of date — do not use it for facts, dates,
   people, prices or product details. If a source doesn't say something, the episode says
   it's unknown or leaves it out.
2. **The token is secret.** Never print it, echo it, write it to any file, put it in a
   commit, or include it in your report. Use it only inside the single `git push` command
   in Step 6.
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

- Use the full `kokoro-v1.0.onnx`, **not** the int8 version — int8 is ~3x slower on this hardware.
- Models go in `~/models`, **never** inside the repo (they're 350 MB and would break the site).
- Hugging Face is blocked here. GitHub release downloads work.
- Clone anonymously — the repo is public. The token is only needed to push.

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

History is squashed on every run so deleted episodes don't accumulate in git forever.
Everything currently in the folder — including any edits MC made on GitHub — is kept.

```bash
cd ~/chronos
git checkout -q --orphan publish
git add -A
git -c user.name="machine-bot-mc" -c user.email="machine-bot-mc@users.noreply.github.com" \
    -c commit.gpgsign=false commit -q -m "Chronos $TODAY"
git push -q --force "https://x-access-token:${CHRONOS_TOKEN}@github.com/machine-bot-mc/chronos.git" publish:main
```

(`CHRONOS_TOKEN` is set from the value in your task prompt. Set it with `export` in the
same command as the push if your shell doesn't persist variables between calls.)

If the push fails:
- **401 / 403 / "Invalid username or token"** → the token has expired or been revoked.
  Stop. Report: "Token rejected — MC needs to create a new one and paste it into the task."
- **Anything else** → retry once after 30 seconds, then stop and report the error text
  (with the token removed).

---

## Step 7 — Verify and report

```bash
sleep 20
git ls-remote https://github.com/machine-bot-mc/chronos.git main
curl -sS https://raw.githubusercontent.com/machine-bot-mc/chronos/main/feed.xml | grep -c "chronos-$TODAY.mp3"
```

The second command should print `1` or more. (`*.github.io` itself is blocked from this
environment, so verify via raw.githubusercontent.com — that's expected, not an error.)

**Final report** — keep it short:
- ✅ or ❌ published
- Today's title, narrator, runtime
- The three story headlines and their sources
- Anything you left out or flagged as unknown, and why
- Any problem MC should know about

Never include the token in the report.
