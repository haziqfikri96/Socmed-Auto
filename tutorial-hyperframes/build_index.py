"""Builds tutorial-hyperframes/index.html from the skit's composition: same 3D balcony scene, characters,
camera, lip-sync and emotes, with the skit-only parts (volcano, sleep clip, file icon) swapped for tutorial cards.

usage (from the repo root): python tutorial-hyperframes/build_index.py   (after build_direction.py)
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
s = (ROOT / "skit-hyperframes/index.html").read_text()
DUR = json.loads((ROOT / "tutorial-hyperframes/direction.json").read_text())["DUR"]


def cut(s, a, b, new=""):
    i = s.index(a); j = s.index(b, i)
    return s[:i] + new + s[j:]


# ---- HTML: tutorial cards in place of the skit's popups
cards = '''<div class="card" id="cTitle"><div class="tk">THE FULL</div><div class="tb">HYPERFRAMES<br />TUTORIAL</div><div class="tt30">⏱ 30 seconds</div></div>
        <div class="card" id="cReq"><h3>STEP 0 · <b>YOU NEED</b></h3>
          <div class="feat" id="rq0"><i style="background:#16A34A">⬢</i>Node.js 22+<em>✓</em></div>
          <div class="feat" id="rq1"><i style="background:#7C3AED">▶</i>FFmpeg<em>✓</em></div>
        </div>
        <div class="card" id="cInst"><h3>STEP 1 · <b>INSTALL IN CLAUDE CODE</b></h3><div id="instBody" class="term mono"></div></div>
        <div class="card" id="cAsk"><h3>STEP 2 · <b>JUST ASK</b></h3>
          <div class="bub you"><span class="lb">YOU</span><div id="askText"></div></div>
          <div class="bub ai" id="askAI"><span class="lb">CLAUDE</span><div id="askAIText"></div></div>
        </div>
        <div class="card" id="cRun"><h3>STEP 3 · <b>PREVIEW → RENDER</b></h3><div id="runBody" class="term mono"></div>
          <div id="mini2"><div id="mini2T">Hello!</div></div></div>
        <div class="card" id="cCta"><div id="ctaA">That's it.</div>
          <span class="tag" id="tg0" style="background:#16A34A">FREE</span><span class="tag" id="tg1" style="background:#7C3AED">OPEN SOURCE</span><span class="tag" id="tg2" style="background:#334155">by HeyGen</span>
          <div id="ctaB">FOLLOW FOR<br /><b>PART 2</b></div><div id="ctaC">making your first video →</div></div>

        '''
s = cut(s, '<div id="ttFrame"></div>', '<div id="sub">', cards)

# ---- CSS: drop the skit-only blocks, add the tutorial cards
s = cut(s, "      /* hook: the mystery file", "      /* html -> mp4 */")
s = cut(s, "      /* volcano mini-video */", "      .emote {")
css = '''
      #cTitle { text-align: center; top: 340px; }
      #cTitle .tk { font-size: 40px; font-weight: 800; color: #94A3B8; letter-spacing: 0.2em; }
      #cTitle .tb { font-size: 104px; line-height: 104px; font-weight: 900; letter-spacing: -0.04em; color: #2DD4BF; margin: 10px 0 18px; }
      #cTitle .tt30 { display: inline-block; padding: 10px 26px; border-radius: 999px; background: #F59E0B; color: #1a1205; font-size: 34px; font-weight: 900; }
      .term { border-radius: 22px; background: #0B1020; padding: 24px 22px; font-size: 30px; line-height: 50px; color: #E2E8F0; white-space: pre-wrap; word-break: break-all; min-height: 200px; }
      .term .p, .term .ok { color: #4ADE80; } .term .h { color: #A3B1C6; } .term .cur { background: #E2E8F0; color: #0B1020; }
      .bub { position: relative; border-radius: 26px; padding: 50px 28px 24px; font-size: 36px; line-height: 50px; font-weight: 800; margin: 10px 0 18px; }
      .bub .lb { position: absolute; left: 24px; top: 12px; font-size: 22px; letter-spacing: 0.14em; font-weight: 900; }
      .bub.you { background: #1E293B; margin-left: 60px; } .bub.you .lb { color: #F59E0B; }
      .bub.ai { background: rgba(45, 212, 191, 0.14); border: 2px solid rgba(45, 212, 191, 0.5); margin-right: 60px; font-size: 30px; line-height: 44px; } .bub.ai .lb { color: #2DD4BF; }
      .bub .sl { color: #C084FC; }
      #mini2 { margin: 20px auto 0; width: 300px; height: 300px; border-radius: 22px; background: linear-gradient(160deg, #2563EB, #7C3AED); position: relative; overflow: hidden; opacity: 0; }
      #mini2T { position: absolute; left: 0; width: 300px; top: 118px; text-align: center; font-size: 52px; font-weight: 900; }
      #cCta { text-align: center; }
      #ctaA { font-size: 64px; font-weight: 900; margin-bottom: 18px; }
      #ctaB { font-size: 60px; line-height: 64px; font-weight: 900; letter-spacing: -0.02em; margin: 22px 0 10px; } #ctaB b { color: #2DD4BF; font-size: 110px; line-height: 116px; }
      #ctaC { font-size: 36px; font-weight: 800; color: #94A3B8; }
    </style>'''
s = s.replace("\n    </style>", css, 1)

# ---- JS: drop skit-only setup and the volcano
s = s.replace('      $("ttZ").innerHTML = SVG.zzz; $("ttZ").style.cssText = "position:absolute;left:0;top:0;width:150px;height:150px;";\n', "")
s = s.replace('''      const frames = $("frames");
      for (let i = 0; i < 16; i++) { const f = document.createElement("div"); f.className = "fr"; f.style.left = i * 78 + "px"; frames.appendChild(f); }
''', "")
s = cut(s, "      /* volcano mini-video: rumble", "      /* the desk monitor")
s = s.replace("if (t < LINES[3].s || t >= LINES[15].s) {", "if (t < LINES[3].s) {")
s = s.replace('mx.fillText("final_final_v3.mp4", 258, 200);', 'mx.fillText("hyperframes", 280, 200);')

hud = r'''function hud(t) {
        let blur = 0;
        for (const [id, a, b] of D.cards) {
          const v = t >= a && t < b, el = $(id);
          el.style.opacity = v ? seg(t, a, a + 0.12) * (1 - seg(t, b - 0.15, b)) : 0;
          el.style.transform = v ? `scale(${((0.86 + 0.14 * springIn(t, a, 0.45)) * (1 + 0.025 * clamp((t - a) / Math.max(0.5, b - a), 0, 1))).toFixed(4)})` : "";
          if (v) blur = Math.max(blur, seg(t, a, a + 0.15) * (1 - seg(t, b - 0.15, b)));
        }
        $("dim").style.opacity = (0.35 * blur).toFixed(3);   // flat dim, no per-frame blur filter
        const cur = Math.floor(t * 3) % 2 ? '<span class="cur">&nbsp;</span>' : " ";

        // step 0: requirements pop on their words
        [D.nodeAt, D.ffAt].forEach((a, i) => { $("rq" + i).style.opacity = t >= a ? 1 : 0; $("rq" + i).style.transform = `translateX(${((1 - springIn(t, a, 0.35)) * 60).toFixed(1)}px)`; });

        // step 1: the two install commands type out as Quill says them
        const C1 = "claude plugin marketplace add heygen-com/hyperframes", C2 = "claude plugin install hyperframes@hyperframes";
        const n1 = Math.floor(clamp((t - D.T1) / 1.1, 0, 1) * C1.length), n2 = Math.floor(clamp((t - D.T2) / 0.85, 0, 1) * C2.length);
        const wrap = (c, n, at) => (n > at ? c.slice(0, at) + "\n  " + c.slice(at + 1, n) : c.slice(0, n));
        let term = `<span class="h"># in Claude Code</span>\n<span class="p">$</span> ${wrap(C1, n1, 29)}`;
        if (t >= D.T2) term += `\n<span class="p">$</span> ${wrap(C2, n2, 21)}`;
        if (t >= D.T2 + 1.0) term += `\n<span class="ok">✓ Installed hyperframes</span>`;
        $("instBody").innerHTML = term + cur;

        // step 2: the prompt types into the chat, then Claude answers
        const a0 = D.cards[3][1], P = "Using /hyperframes, make a 10-second intro with a fade-in title";
        const np = Math.floor(clamp((t - a0 - 0.1) / 1.9, 0, 1) * P.length);
        $("askText").innerHTML = P.slice(0, np).replace("/hyperframes", '<span class="sl">/hyperframes</span>') + (np < P.length ? cur : "");
        const aiOn = t >= a0 + 2.3;
        $("askAI").style.opacity = aiOn ? 1 : 0; $("askAI").style.transform = `scale(${springIn(t, a0 + 2.3, 0.35).toFixed(3)})`;
        const steps = ["✍️ writing index.html", "✓ checked: 0 errors", "✓ ready to preview"];
        $("askAIText").innerHTML = steps.filter((_, k) => t >= a0 + 2.3 + k * 0.6).join("<br />");

        // step 3: preview, then render
        let run = `<span class="p">$</span> npx hyperframes preview`;
        if (t >= D.previewAt + 0.4) run += `\n<span class="ok">✓ live at localhost:3002</span>`;
        if (t >= D.renderAt) run += `\n<span class="p">$</span> npx hyperframes render`;
        if (t >= D.renderAt + 0.6) run += `\n<span class="ok">✓ my-video.mp4</span>`;
        $("runBody").innerHTML = run + cur;
        const m0 = D.previewAt + 0.4, mu = t < m0 ? 0 : smooth((((t - m0) % 1.4) + 1.4) % 1.4 / 0.7);
        $("mini2").style.opacity = t >= m0 ? 1 : 0; $("mini2").style.transform = `scale(${springIn(t, m0, 0.35).toFixed(3)})`;
        $("mini2T").style.opacity = mu; $("mini2T").style.transform = `translateY(${(30 * (1 - mu)).toFixed(1)}px)`;

        // CTA tags on "free" and "open source"
        [D.freeAt, D.openAt, D.openAt + 0.5].forEach((a, i) => { $("tg" + i).style.opacity = t >= a ? 1 : 0; $("tg" + i).style.transform = `scale(${springIn(t, a, 0.3)})`; });

        // subtitles + speaker badge (inside the safe zone)
        const i = lineAt(t), L = LINES[i], on = t >= L.s - 0.05 && t < L.e + 0.2;
        $("sub").style.opacity = on ? 1 : 0;
        $("who").textContent = L.who === "dev" ? "SHICHI" : "QUILL"; $("who").className = L.who;
        $("line").textContent = L.text;
      }

      function renderAt'''
s = cut(s, "function hud(t) {", "(t) {\n        monitorAt(t);", hud)
s = s.replace('const pop = ["vplayer", ...D.cards.map((c) => c[0])].map($)', 'const pop = D.cards.map((c) => c[0]).map($)')
s = s.replace("skit-hyperframes", "tutorial-hyperframes")
s = re.sub(r'data-duration="38\.36"', f'data-duration="{DUR:.2f}"', s)
s = s.replace("tl.to({}, { duration: 38.36 }, 0);", f"tl.to({{}}, {{ duration: {DUR:.2f} }}, 0);")
assert "38.36" not in s
(ROOT / "tutorial-hyperframes/index.html").write_text(s)
print("wrote tutorial-hyperframes/index.html", len(s.splitlines()), "lines")
