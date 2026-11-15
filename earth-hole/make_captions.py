"""Turn assets/words.json (word timings) into captions.js: short upper-case chunks, numbers as digits."""
import json
import sys
from pathlib import Path

words = json.loads(Path(sys.argv[1]).read_text())
NUMBERS = {("twenty-eight", "thousand"): "28,000", ("thirty-eight",): "38"}
HOT = {"FASTER", "FASTER.", "WEIGHTLESS.", "SUN.", "28,000", "38"}

tokens, i = [], 0
while i < len(words):
    for keys, digits in NUMBERS.items():
        got = tuple(w["w"].lower().strip(".,?!") for w in words[i:i + len(keys)])
        if got == keys:
            tokens.append({"w": digits, "s": words[i]["s"], "e": words[i + len(keys) - 1]["e"]})
            i += len(keys)
            break
    else:
        tokens.append(dict(words[i]))
        i += 1

chunks, cur = [], []
for tok in tokens:
    cur.append(tok)
    text = " ".join(t["w"] for t in cur)
    if tok["w"][-1] in ".,?!" or len(cur) == 2 or len(text) >= 11:
        chunks.append(cur)
        cur = []
if cur:
    chunks.append(cur)

out = []
for n, ch in enumerate(chunks):
    text = " ".join(t["w"] for t in ch).upper().rstrip(",")
    end = ch[-1]["e"] + 0.15
    if n + 1 < len(chunks) and chunks[n + 1][0]["s"] - ch[-1]["e"] < 0.6:
        end = chunks[n + 1][0]["s"]
    out.append({"t": text.rstrip("."), "s": ch[0]["s"], "e": round(end, 3), "hot": any(w in HOT for w in text.split())})

Path(sys.argv[2]).write_text("window.CAPTIONS = " + json.dumps(out) + ";\n")
print(len(out), "caption chunks;", " | ".join(c["t"] for c in out[:12]))
