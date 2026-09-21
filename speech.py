"""Turn a written script into what the narrator should actually be fed.

Two jobs:
1. Collapse dotted initialisms (A.I. -> AI) so the voice doesn't stop between letters.
2. Apply the word fixes listed in pronunciation.txt (e.g. Uber => Oober).
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))

def load_fixes(path=os.path.join(HERE, "pronunciation.txt")):
    fixes = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=>" not in line:
            continue
        a, b = [x.strip() for x in line.split("=>", 1)]
        if a and b:
            fixes.append((a, b))
    return fixes

_DOTTED = re.compile(r"\b(?:[A-Za-z]\.){2,}")

def _collapse_initialisms(text):
    out, pos = [], 0
    for m in _DOTTED.finditer(text):
        core = m.group(0).replace(".", "")
        rest = text[m.end():]
        ends_sentence = rest.strip() == "" or re.match(r'\s+["“(]?[A-Z]', rest) is not None
        out.append(text[pos:m.start()])
        out.append(core + ("." if ends_sentence else ""))
        pos = m.end()
    out.append(text[pos:])
    return "".join(out)

def for_speech(text, fixes=None):
    if fixes is None:
        fixes = load_fixes()
    text = _collapse_initialisms(text)
    for a, b in fixes:
        text = re.sub(r"\b" + re.escape(a) + r"\b", b, text, flags=re.IGNORECASE)
    return text
