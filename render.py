"""Narrate a plain-text script into a WAV.

usage: python3 render.py SCRIPT.txt OUT.wav [YYYY-MM-DD]

Narrator alternates by date: even day-of-year = Michael, odd = Heart.
Paragraphs are separated by blank lines. Models are read from $CHRONOS_MODELS
(default ~/models) and must never be placed inside the repo.
"""
import os, re, sys, time, datetime
from zoneinfo import ZoneInfo
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from speech import for_speech

MODELS = os.environ.get("CHRONOS_MODELS", os.path.expanduser("~/models"))
day = (datetime.date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3
       else datetime.datetime.now(ZoneInfo("America/Toronto")).date())
VOICE = "af_heart" if day.timetuple().tm_yday % 2 else "am_michael"

k = Kokoro(os.path.join(MODELS, "kokoro-v1.0.onnx"), os.path.join(MODELS, "voices-v1.0.bin"))
paras = [p.strip() for p in open(sys.argv[1], encoding="utf-8").read().split("\n\n") if p.strip()]

def chunks(p, limit=380):
    sents = re.split(r"(?<=[.!?]) +", p); out, cur = [], ""
    for s in sents:
        if len(cur) + len(s) < limit: cur = (cur + " " + s).strip()
        else:
            if cur: out.append(cur)
            cur = s
    if cur: out.append(cur)
    return out

parts, t0, sr = [], time.time(), 24000
for i, p in enumerate(paras):
    cs = chunks(for_speech(p))
    for j, c in enumerate(cs):
        s, sr = k.create(c, voice=VOICE, speed=1.0, lang="en-us")
        parts.append(s)
        if j < len(cs) - 1: parts.append(np.zeros(int(sr * 0.05), dtype=s.dtype))
    if i < len(paras) - 1: parts.append(np.zeros(int(sr * 0.40), dtype=parts[-1].dtype))

audio = np.concatenate(parts)
sf.write(sys.argv[2], audio, sr)
print(f"date {day} | voice {VOICE} | synth {time.time()-t0:.0f}s | audio {len(audio)/sr/60:.2f} min")
