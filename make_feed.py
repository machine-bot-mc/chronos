"""Build the Chronos podcast feed from whatever episodes are in site/episodes/.

Run after a new episode lands. Keeps the newest KEEP episodes, deletes older
files, and rewrites feed.xml so it lists exactly what is still there.
"""
import os, re, glob, html, datetime, subprocess, json, sys

KEEP = 60                      # episodes retained; older files are deleted
SITE = os.path.dirname(os.path.abspath(__file__))   # repo root
EPDIR = os.path.join(SITE, "episodes")

# These two get filled in once MC has his repo. Nothing else needs changing.
GH_USER = os.environ.get("CHRONOS_GH_USER", "machine-bot-mc")
GH_REPO = os.environ.get("CHRONOS_GH_REPO", "chronos")
BASE = f"https://{GH_USER}.github.io/{GH_REPO}"

TITLE = "Chronos"
SUBTITLE = "A daily briefing, narrated."
DESC = ("A personal daily audio digest. Researched and narrated each morning, "
        "with every claim attributed to a named source.")
AUTHOR = "Chronos"
EMAIL = "chronos@example.invalid"   # required by some apps; never receives mail

def duration_seconds(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout.strip()
    return int(float(out)) if out else 0

def hhmmss(sec):
    return f"{sec//3600:02d}:{(sec%3600)//60:02d}:{sec%60:02d}"

def rfc2822(d, hour=7, minute=0):
    # Podcast apps sort on this. Stamped in Toronto local time, DST handled by the tz database.
    from zoneinfo import ZoneInfo
    dt = datetime.datetime(d.year, d.month, d.day, hour, minute, tzinfo=ZoneInfo("America/Toronto"))
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")

def episode_date(fname):
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", fname)
    if not m:
        return None
    return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

def load_titles():
    path = os.path.join(SITE, "titles.json")
    return json.load(open(path)) if os.path.exists(path) else {}

def prune(files):
    """Newest KEEP survive. Returns survivors, deleted filenames."""
    files = sorted(files, key=lambda p: episode_date(p), reverse=True)
    keep, drop = files[:KEEP], files[KEEP:]
    for p in drop:
        os.remove(p)
    return keep, [os.path.basename(p) for p in drop]

def build():
    files = [p for p in glob.glob(os.path.join(EPDIR, "*.mp3")) if episode_date(p)]
    if not files:
        print("no episodes found — nothing to do"); return None
    keep, dropped = prune(files)
    titles = load_titles()

    items = []
    for p in keep:
        name = os.path.basename(p)
        d = episode_date(name)
        secs = duration_seconds(p)
        size = os.path.getsize(p)
        subject = titles.get(name, "")
        title = f"{d.strftime('%A, %B %-d, %Y')}"
        if subject:
            title += f" — {subject}"
        items.append(f"""    <item>
      <title>{html.escape(title)}</title>
      <description>{html.escape(SUBTITLE)}</description>
      <pubDate>{rfc2822(d)}</pubDate>
      <enclosure url="{BASE}/episodes/{name}" length="{size}" type="audio/mpeg"/>
      <guid isPermaLink="false">chronos-{d.isoformat()}</guid>
      <itunes:duration>{hhmmss(secs)}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")

    from zoneinfo import ZoneInfo
    _n = datetime.datetime.now(ZoneInfo("America/Toronto"))
    now = rfc2822(_n.date(), _n.hour, _n.minute)
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{html.escape(TITLE)}</title>
    <link>{BASE}/</link>
    <description>{html.escape(DESC)}</description>
    <language>en-ca</language>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>{html.escape(AUTHOR)}</itunes:author>
    <itunes:summary>{html.escape(DESC)}</itunes:summary>
    <itunes:type>episodic</itunes:type>
    <itunes:explicit>false</itunes:explicit>
    <itunes:image href="{BASE}/cover.png"/>
    <itunes:category text="News"/>
    <itunes:owner>
      <itunes:name>{html.escape(AUTHOR)}</itunes:name>
      <itunes:email>{EMAIL}</itunes:email>
    </itunes:owner>
{chr(10).join(items)}
  </channel>
</rss>
"""
    with open(os.path.join(SITE, "feed.xml"), "w") as f:
        f.write(feed)
    print(f"feed.xml written | {len(keep)} episodes listed | {len(dropped)} deleted")
    if dropped:
        print("  deleted:", ", ".join(dropped))
    return feed

if __name__ == "__main__":
    build()
