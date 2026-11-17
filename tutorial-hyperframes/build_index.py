"""Builds tutorial-hyperframes/index.html (v2, see STORYBOARD.md) from the skit's composition: same balcony scene,
characters, lip-sync and emotes. On top of that, the tutorial now happens *inside Quill's face-screen*: three
"portals" unmask from the projected screen rectangle to the full frame while the camera pushes into it.
No cards, corner marks, tracked-caps labels or end card (motionmaxxing "never ship").

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


def sub(s, a, b):
    assert a in s, a[:80]
    return s.replace(a, b, 1)


# ---------------- HTML: Quill's screen (portal), the part-2 face, captions
html = '''<div id="portal"><div id="pscreen" data-ui="terminal"><div id="pin">
          <div id="term" class="mono"></div>
          <div id="ask"><div id="askBox" class="mono"></div><div id="work" class="mono"></div></div>
          <div id="pv"><div id="pvFrame"><div id="pvTitle">Your Intro</div><div id="pvSub">made with HyperFrames</div></div></div>
          <div id="file"><div class="fi"><i></i></div><div class="fn mono">my-video.mp4</div></div>
        </div></div></div>
        <div id="face2" class="mono"><span>part 2 →</span></div>
        <div id="cap"></div>
      </div>

      '''
s = cut(s, '<div id="ttFrame"></div>', '<audio id="mix"', html)

# ---------------- CSS: drop the skit's popups, add the screen world
s = cut(s, "      /* hook: the mystery file", "      /* html -> mp4 */")
s = cut(s, "      /* volcano mini-video */", "      .emote {")
s = re.sub(r"      #mark \{[^\n]*\n", "", s)
css = '''
      /* Quill's screen, full frame: same navy as his face, cyan = Quill acting */
      #portal { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; overflow: hidden; clip-path: inset(50% 50% 50% 50%); }
      #pscreen { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0;
        background: radial-gradient(ellipse 120% 70% at 50% 38%, #142540 0%, #0a1220 62%, #060b14 100%); }
      #pscreen::after { content: ""; position: absolute; inset: 0; background: repeating-linear-gradient(0deg, rgba(255,255,255,0.025) 0 2px, rgba(0,0,0,0) 2px 6px); }
      #pin { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 50% 40%; }
      #term { position: absolute; left: 64px; top: 0; font-size: 64px; line-height: 96px; color: #e2e8f0; white-space: pre; }
      #term .cm { color: #64748b; } #term .ps { color: #5eead4; } #term .k { color: #5eead4; }
      .caret { display: inline-block; width: 36px; height: 70px; vertical-align: -12px; background: #5eead4; }
      #ask { position: absolute; left: 50px; width: 980px; top: 440px; }
      #askBox { border: 4px solid #5eead4; border-radius: 30px; padding: 36px 40px; font-size: 64px; line-height: 94px; color: #f1f5f9; white-space: pre-wrap; min-height: 260px; }
      #askBox .gt { color: #5eead4; } #askBox .sl { color: #5eead4; }
      #work { margin-top: 44px; font-size: 54px; color: #5eead4; opacity: 0; }
      #pv { position: absolute; left: 315px; top: 520px; width: 450px; height: 800px; border-radius: 34px; overflow: hidden; background: #F4F1EA; opacity: 0; transform-origin: 50% 50%; }
      #pvFrame { position: absolute; inset: 0; }
      #pvTitle { position: absolute; left: 0; width: 450px; top: 330px; text-align: center; font-size: 66px; font-weight: 900; color: #0F0F0F; letter-spacing: -0.03em; }
      #pvSub { position: absolute; left: 0; width: 450px; top: 420px; text-align: center; font-size: 28px; font-weight: 700; color: #2563EB; }
      #file { position: absolute; left: 240px; top: 790px; width: 600px; text-align: center; opacity: 0; }
      #file .fi { width: 190px; height: 230px; margin: 0 auto; border-radius: 22px; background: #5eead4; position: relative; }
      #file .fi i { position: absolute; left: 72px; top: 78px; border-left: 64px solid #0a1220; border-top: 38px solid transparent; border-bottom: 38px solid transparent; }
      #file .fn { margin-top: 26px; font-size: 52px; color: #f1f5f9; }
      #face2 { position: absolute; left: 0; top: 0; width: 100px; height: 60px; opacity: 0; background: #0a1220; border-radius: 30%; display: flex; align-items: center; justify-content: center; color: #5eead4; white-space: nowrap; transform-origin: 0 0; }
      /* captions: word by word, speaker colour on the active word, inside the TikTok safe zone */
      #cap { position: absolute; left: 90px; width: 840px; top: 1430px; text-align: center; }
      #cap .ch { display: inline-block; padding: 12px 28px 16px; border-radius: 26px; background: rgba(6, 9, 20, 0.72); font-size: 56px; line-height: 70px; font-weight: 800; color: rgba(255,255,255,0.9); }
      #cap .on.quill { color: #5eead4; } #cap .on.dev { color: #F59E0B; }
    </style>'''
s = s.replace("\n    </style>", css, 1)

# ---------------- JS: drop skit-only setup and the volcano
s = s.replace('      $("ttZ").innerHTML = SVG.zzz; $("ttZ").style.cssText = "position:absolute;left:0;top:0;width:150px;height:150px;";\n', "")
s = s.replace('''      const frames = $("frames");
      for (let i = 0; i < 16; i++) { const f = document.createElement("div"); f.className = "fr"; f.style.left = i * 78 + "px"; frames.appendChild(f); }
''', "")
s = cut(s, "      /* volcano mini-video: rumble", "      /* the desk monitor")
s = s.replace("if (t < LINES[3].s || t >= LINES[15].s) {", "if (t < LINES[3].s) {")
s = s.replace('mx.fillText("final_final_v3.mp4", 258, 200);', 'mx.fillText("hyperframes", 280, 200);')

# camera: a dolly that is already moving at frame 0, and a slightly tighter ending
s = sub(s, "        quillClose: [[0.0, 0.78, 1.35], [0.34, 0.62, 0]],",
        "        quillClose: [[0.0, 0.78, 1.35], [0.34, 0.62, 0]],\n        quillPush: [[0.02, 0.8, 1.75], [0.34, 0.62, 0]],\n        quillEnd: [[0.05, 0.76, 1.5], [0.34, 0.62, 0]],")
s = sub(s, '        if (now === "hookPunch")',
        '        if (now === "quillPush") { const u = 1 - Math.pow(1 - clamp(t / 4.0, 0, 1), 2); p = [0.02, 0.8 - 0.02 * u, 1.75 - 0.4 * u]; }\n        if (now === "hookPunch")')

hud = r'''function hud(t) {
        $("dim").style.opacity = 0;
        // ---------- Quill's screen as a portal ----------
        const pi = D.portals.findIndex(([a, b]) => t >= a - 0.12 && t < b), P = D.portals[pi];
        const expoOut = (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * clamp(x, 0, 1)));
        const easeIn = (x) => clamp(x, 0, 1) ** 3;
        let k = 0;
        if (P) {
          const [a, b] = P;
          k = t < b - D.SHUT ? expoOut((t - a) / D.OPEN) : 1 - easeIn((t - (b - D.SHUT)) / D.SHUT);
          if (t < a) k = 0;
        }
        window.__portalK = k;
        const R = screenRect();
        const full = { x: -24, y: -24, w: 1128, h: 1968 };
        const lerpR = (A, B, u) => ({ x: A.x + (B.x - A.x) * u, y: A.y + (B.y - A.y) * u, w: A.w + (B.w - A.w) * u, h: A.h + (B.h - A.h) * u });
        const rr = lerpR(R, full, k), rad = (1 - k) * R.h * 0.45;
        const on = P && t >= P[0] - 0.12 && R.w > 1;
        $("portal").style.clipPath = on ? `inset(${rr.y.toFixed(1)}px ${(1080 - rr.x - rr.w).toFixed(1)}px ${(1920 - rr.y - rr.h).toFixed(1)}px ${rr.x.toFixed(1)}px round ${rad.toFixed(1)}px)` : "inset(50% 50% 50% 50%)";
        const sc = on ? Math.max(rr.w / 1080, 0.05) : 1;
        $("pscreen").style.transform = on ? `translate(${rr.x.toFixed(1)}px, ${(rr.y + rr.h / 2 - 960 * sc).toFixed(1)}px) scale(${sc.toFixed(4)})` : "";

        // a slow push while inside the screen, so a held line still has a living camera
        if (P) { const cz = clamp((t - P[0]) / (P[1] - P[0]), 0, 1); $("pin").style.transform = `scale(${(1 + 0.06 * cz).toFixed(4)}) translateY(${(-24 * cz).toFixed(1)}px) rotate(${(0.6 * Math.sin(t * 0.9)).toFixed(3)}deg)`; }
        // ---------- what is on the screen ----------
        const rows = D.rows.filter((r) => r[0] === pi);
        const blink = Math.floor(t * 2.4) % 2 === 0;
        const caret = '<span class="caret"></span>';
        // terminal rows (portal 0 and 2)
        let html = "", cur = -1, caretCol = 0, n = 0, lineNo = 0;
        const termRows = rows.filter((r) => r[1] !== "prompt");
        termRows.forEach((r, ri) => {
          const [, kind, text, times] = r;
          const shown = times.filter((x) => x <= t).length;
          if (shown === 0 && ri > 0 && t < times[0]) return;
          if (ri > 0) { html += "\n"; lineNo++; if (kind === "cmd" && termRows[ri - 1][1] === "comment") { html += "\n"; lineNo++; } }
          const body = text.slice(0, shown).replace(/&/g, "&amp;").replace(/</g, "&lt;");
          html += kind === "comment" ? `<span class="cm">${body}</span>` : `<span class="ps">$ </span>${body}`;
          cur = lineNo; caretCol = (kind === "comment" ? 0 : 2) + shown; n = shown;
        });
        if (termRows.length && cur >= 0) html += blink || n < 1 ? caret : "";
        $("term").innerHTML = html;
        // pan along a long line (the camera follows the caret; text cropped by the frame edge) and scroll down the lines
        const CW = 64 * 0.6;
        const panAt = (tt) => {
          let col = 0;
          termRows.forEach((r) => { const s = r[3].filter((x) => x <= tt).length; if (s > 0 && s < r[2].length + 1 && tt >= r[3][0]) col = (r[1] === "comment" ? 0 : 2) + s; });
          return Math.max(0, 64 + col * CW - 880);
        };
        let pan = 0; for (let j = 0; j < 8; j++) pan += panAt(t - j * 0.03) / 8;
        const topY = pi === 2 ? 300 : 560 - Math.max(0, cur - 3) * 96;
        $("term").style.transform = `translate(${(-pan).toFixed(1)}px, ${topY}px)`;
        $("term").style.opacity = termRows.length ? 1 : 0;

        // the prompt (portal 1), typed as Quill says it
        const pr = rows.find((r) => r[1] === "prompt");
        $("ask").style.opacity = pr ? 1 : 0;
        if (pr) {
          const shown = pr[3].filter((x) => x <= t).length;
          const txt = pr[2].slice(0, shown).replace("/hyperframes", '<span class="sl">/hyperframes</span>');
          $("askBox").innerHTML = `<span class="gt">&gt; </span>${txt}${blink || shown < pr[2].length ? caret : ""}`;
          const [w0, w1] = D.working, wOn = t >= w0 && t < w1;
          $("work").style.opacity = wOn ? 1 : 0;
          $("work").textContent = "✻ " + ["Working", "Working.", "Working..", "Working..."][Math.floor((t - w0) * 4) % 4 < 0 ? 0 : Math.floor((t - w0) * 4) % 4];
        }
        // preview -> render -> file (portal 2)
        const pvOn = pi === 2 && t >= D.previewAt;
        const pvU = pvOn ? expoOut((t - D.previewAt) / 0.5) : 0;
        const into = t >= D.fileAt - 0.2 ? easeIn((t - (D.fileAt - 0.2)) / 0.2) : 0;     // the preview collapses into the file
        $("pv").style.opacity = pvOn && into < 1 ? 1 : 0;
        $("pv").style.transform = `translateY(${(120 * (1 - pvU) + 60 * into).toFixed(1)}px) scale(${((1.12 - 0.12 * pvU) * (1 - 0.7 * into)).toFixed(4)})`;
        const ft = clamp((t - D.previewAt - 0.25) / 1.1, 0, 1);       // the title fades in: exactly what the prompt asked for
        $("pvTitle").style.opacity = ft; $("pvTitle").style.transform = `translateY(${(26 * (1 - ft)).toFixed(1)}px)`;
        $("pvSub").style.opacity = clamp((t - D.previewAt - 0.9) / 0.6, 0, 1);
        const fOn = pi === 2 && t >= D.fileAt, fu = fOn ? expoOut((t - D.fileAt) / 0.35) : 0;
        $("file").style.opacity = fOn ? 1 : 0;
        $("file").style.transform = `scale(${(2.6 - 1.6 * fu).toFixed(4)})`;     // lands from oversize, decelerating, no bounce

        // ---------- the ending: Quill's own screen says "part 2" ----------
        const f2 = t >= D.part2 ? expoOut((t - D.part2) / 0.3) : 0;
        $("face2").style.opacity = t >= D.part2 ? 1 : 0;
        if (t >= D.part2) {
          const h = R.h * 0.9, w = R.w * 0.92;
          $("face2").style.width = w + "px"; $("face2").style.height = h + "px";
          $("face2").style.fontSize = Math.min(h * 0.34, w / (8 * 0.66)).toFixed(1) + "px";
          const z = 1.12 - 0.12 * f2;
          $("face2").style.transform = `translate(${(R.x + R.w / 2 - (w * z) / 2).toFixed(1)}px, ${(R.y + R.h / 2 - (h * z) / 2).toFixed(1)}px) scale(${z.toFixed(4)})`;
        }

        // ---------- captions: word by word, chunked, speaker colour on the active word ----------
        const li = lineAt(t), L = LINES[li], capOn = t >= L.s - 0.05 && t < L.e + 0.25;
        $("cap").style.opacity = capOn ? 1 : 0;
        if (capOn) {
          const ws = L.words, chunks = [[]];
          ws.forEach((w, j) => { chunks[chunks.length - 1].push(j); if (/[.,!?]$/.test(w.w) || chunks[chunks.length - 1].length >= 4) chunks.push([]); });
          const act = Math.max(0, ws.findIndex((w) => t < w.e) === -1 ? ws.length - 1 : ws.findIndex((w) => t < w.e));
          const ch = chunks.find((c) => c.includes(act)) || chunks[0];
          $("cap").innerHTML = '<span class="ch">' + ch.map((j) => `<span class="${j === act && t >= ws[j].s ? "on " + L.who : ""}">${ws[j].w}</span>`).join(" ") + "</span>";
        }
      }

      // Quill's face-screen rectangle on the frame (projected corners of the screen pivot)
      const _v = new THREE.Vector3();
      function screenRect() {
        quill.group.updateMatrixWorld(true);
        let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
        for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
          _v.set(sx * 0.125, sy * 0.085, 0.02); quill.screen.localToWorld(_v); _v.project(camera);
          if (_v.z > 1) return { x: 540, y: 960, w: 0, h: 0 };
          const px = (_v.x + 1) / 2 * 1080, py = (1 - _v.y) / 2 * 1920;
          x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py);
        }
        return { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
      }

      // Quill's screen light: cyan wash that swells before the first dive and during every dive approach
      const qLight = new THREE.PointLight(0x5eead4, 0, 0.7, 2); scene.add(qLight);
      const _n = new THREE.Vector3(), _q = new THREE.Quaternion();

      function renderAt'''
s = cut(s, "function hud(t) {", "(t) {\n        monitorAt(t);", hud)

# camera push into Quill's screen around each dive, screen light, and skip the 3D draw while the screen covers the frame
s = sub(s, '''        const [cp, cl] = camAt(t);
        camera.position.set(...cp); camera.lookAt(...cl);
        renderer.render(scene, camera);
        hud(t);''', '''        let [cp, cl] = camAt(t);
        const dp = D.portals.find(([a, b]) => t >= a - 0.12 && t < b);
        quill.group.updateMatrixWorld(true);
        quill.screen.getWorldPosition(_v); quill.screen.getWorldQuaternion(_q); _n.set(0, 0, 1).applyQuaternion(_q);
        if (dp) {
          const [a, b] = dp, Q = [[0.0, 0.78, 1.35], [0.34, 0.62, 0]];
          const into = clamp((t - (a - 0.12)) / (D.OPEN + 0.12), 0, 1) ** 2, out = t > b - D.SHUT ? (t - (b - D.SHUT)) / D.SHUT : 0;
          const u = into * (1 - 0.6 * out);
          const tgt = [_v.x + _n.x * 0.16, _v.y + _n.y * 0.16, _v.z + _n.z * 0.16];
          cp = Q[0].map((x, j) => x + (tgt[j] - x) * u); cl = Q[1].map((x, j) => x + ([_v.x, _v.y, _v.z][j] - x) * u);
        }
        camera.position.set(...cp); camera.lookAt(...cl);
        const glow = (t >= D.glow[0] && t < D.glow[1] + D.OPEN) ? clamp((t - D.glow[0]) / (D.glow[1] - D.glow[0]), 0, 1) : (dp ? 1 : 0);
        qLight.position.set(_v.x + _n.x * 0.25, _v.y + _n.y * 0.25, _v.z + _n.z * 0.25); qLight.intensity = (dp || D.shots[beatAt(D.shots, t)][1].startsWith("quill")) ? 1.5 * glow : 0;   // only while the camera is on Quill
        hud(t);
        if ((window.__portalK || 0) < 0.999) renderer.render(scene, camera);   // fully inside the screen: no 3D draw needed''')
s = s.replace('const pop = ["vplayer", ...D.cards.map((c) => c[0])].map($)', 'const pop = D.cards.map((c) => c[0]).map($)')
s = sub(s, "return p < 0.18 || p > 0.88 ? 0.45 : p < 0.3 || p > 0.72 ? 0.62 : 0.95;", "return p < 0.14 || p > 0.9 ? 0.05 : p < 0.32 || p > 0.7 ? 0.45 : 0.95;   // closed / small / wide per syllable")
s = s.replace("skit-hyperframes", "tutorial-hyperframes")
s = re.sub(r'data-duration="38\.36"', f'data-duration="{DUR:.2f}"', s)
s = s.replace("tl.to({}, { duration: 38.36 }, 0);", f"tl.to({{}}, {{ duration: {DUR:.2f} }}, 0);")
for bad in ["38.36", '<div id="mark">', 'id="sub"']:
    assert bad not in s, (bad, s[max(0, s.index(bad) - 80):s.index(bad) + 40])
(ROOT / "tutorial-hyperframes/index.html").write_text(s)
print("wrote tutorial-hyperframes/index.html", len(s.splitlines()), "lines")
