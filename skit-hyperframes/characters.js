/*
 * Low-poly skit characters (original designs), built from Three.js primitives with flat shading.
 *
 *   import { createDev, createBot } from "./characters.js";
 *   const dev = createDev(THREE);   // ~1.0 units tall, feet at y = 0, facing +z
 *   const bot = createBot(THREE);   // floating sidekick, ~0.55 units tall, hovers above y = 0
 *   scene.add(dev.group, bot.group);
 *   dev.pose("point"); dev.face({ talk: 0.6, blink: 0, mood: "happy" });
 *   bot.face({ mood: "wide", talk: 0.4 }); bot.update(t);   // update(t) = idle hover, antenna pulse
 *
 * Everything is a function of the values you pass in (no internal clocks), so it renders the same
 * frame every time in HyperFrames.
 */

const flat = (THREE, color, extra = {}) =>
  new THREE.MeshStandardMaterial({ color, flatShading: true, roughness: 0.75, metalness: 0.0, ...extra });

function addMesh(THREE, parent, geo, mat, pos = [0, 0, 0], rot = [0, 0, 0], scale = [1, 1, 1]) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(...pos); m.rotation.set(...rot); m.scale.set(...scale);
  m.castShadow = true; m.receiveShadow = true;
  parent.add(m);
  return m;
}
const pivot = (THREE, parent, pos = [0, 0, 0]) => { const g = new THREE.Group(); g.position.set(...pos); parent.add(g); return g; };
const lerp = (a, b, t) => a + (b - a) * t;

/* ------------------------------------------------------------------ */
/*  Dev: the host, after the user's character sheet                    */
/* ------------------------------------------------------------------ */
export const DEV_POSES = {
  idle: {},
  wave: { armR: [0, 0, -2.4], foreR: [0, 0, -0.5], head: [0, 0, -0.08] },
  point: { armL: [0, -0.4, 1.45], foreL: [0, 0, 0.1], head: [0, 0.25, 0] },
  shrug: { armR: [0, 0, -0.75], foreR: [0, 0, 1.6], armL: [0, 0, 0.75], foreL: [0, 0, -1.6], head: [0, 0, 0.12] },
  facepalm: { armR: [-1.2, 0, -0.35], foreR: [-1.9, 0, 0], head: [0.25, 0, 0] },
  think: { armR: [-0.6, 0, -0.25], foreR: [-2.2, 0, 0.3], head: [0.05, 0, 0.12] },
  cheer: { armR: [0, 0, -2.6], armL: [0, 0, 2.6], foreR: [0, 0, -0.3], foreL: [0, 0, 0.3] },
  typing: { armR: [-1.0, 0, -0.15], foreR: [-0.6, 0, 0.2], armL: [-1.0, 0, 0.15], foreL: [-0.6, 0, -0.2], head: [0.2, 0, 0] },
};
const DEV_JOINTS = ["head", "armR", "foreR", "armL", "foreL", "body"];

export function createDev(THREE, opts = {}) {
  const C = { skin: 0xe2a47c, hair: 0x17151a, tee: 0x1c1c22, pants: 0xc7b08a, shoe: 0x2a3150, sole: 0xe9e6df, eye: 0x1a1210, mouth: 0x7a2e26, glasses: 0x222228 };
  const M = Object.fromEntries(Object.entries(C).map(([k, v]) => [k, flat(THREE, v)]));
  M.hair.roughness = 0.5;
  const group = new THREE.Group();
  const rig = {};

  // legs + shoes
  for (const s of [1, -1]) {
    addMesh(THREE, group, new THREE.CylinderGeometry(0.058, 0.05, 0.25, 6), M.pants, [s * 0.065, 0.165, 0]);
    addMesh(THREE, group, new THREE.BoxGeometry(0.11, 0.06, 0.17), M.shoe, [s * 0.068, 0.04, 0.025]);
    addMesh(THREE, group, new THREE.BoxGeometry(0.115, 0.018, 0.175), M.sole, [s * 0.068, 0.009, 0.025]);
  }
  // body pivot (lets the whole upper body bob / lean)
  rig.body = pivot(THREE, group, [0, 0.29, 0]);
  addMesh(THREE, rig.body, new THREE.CylinderGeometry(0.135, 0.12, 0.08, 7), M.pants, [0, 0.0, 0], [0, 0, 0], [1, 1, 0.78]);
  addMesh(THREE, rig.body, new THREE.CylinderGeometry(0.15, 0.17, 0.3, 7), M.tee, [0, 0.17, 0], [0, Math.PI / 7, 0], [1, 1, 0.78]);
  // chest print
  const pc = document.createElement("canvas"); pc.width = 512; pc.height = 128;
  const px = pc.getContext("2d"); px.fillStyle = "#d8d8d8"; px.font = "bold 96px 'DejaVu Sans', Arial, sans-serif"; px.textAlign = "center"; px.textBaseline = "middle";
  px.fillText(opts.print ?? "Shichi.AI", 256, 70, 500);
  const pt = new THREE.CanvasTexture(pc); pt.colorSpace = THREE.SRGBColorSpace;
  addMesh(THREE, rig.body, new THREE.PlaneGeometry(0.2, 0.05), new THREE.MeshBasicMaterial({ map: pt, transparent: true }), [0, 0.22, 0.128], [0.05, 0, 0]);
  // arms
  for (const [side, s] of [["R", -1], ["L", 1]]) {
    const arm = (rig["arm" + side] = pivot(THREE, rig.body, [s * 0.165, 0.29, 0]));
    addMesh(THREE, arm, new THREE.CylinderGeometry(0.055, 0.05, 0.1, 6), M.tee, [s * 0.01, -0.04, 0]);
    addMesh(THREE, arm, new THREE.CylinderGeometry(0.036, 0.034, 0.1, 6), M.skin, [s * 0.008, -0.11, 0]);
    const fore = (rig["fore" + side] = pivot(THREE, arm, [s * 0.008, -0.16, 0]));
    addMesh(THREE, fore, new THREE.CylinderGeometry(0.034, 0.03, 0.12, 6), M.skin, [0, -0.06, 0]);
    addMesh(THREE, fore, new THREE.IcosahedronGeometry(0.042, 0), M.skin, [0, -0.135, 0.005], [0.3, 0.2, 0]);
  }
  // head
  addMesh(THREE, rig.body, new THREE.CylinderGeometry(0.04, 0.045, 0.06, 6), M.skin, [0, 0.33, 0]);
  rig.head = pivot(THREE, rig.body, [0, 0.35, 0]);
  const H = pivot(THREE, rig.head, [0, 0.19, 0]);
  addMesh(THREE, H, new THREE.IcosahedronGeometry(0.2, 1), M.skin, [0, 0, 0], [0, 0, 0], [1.0, 1.02, 0.92]);
  for (const s of [1, -1]) addMesh(THREE, H, new THREE.IcosahedronGeometry(0.05, 0), M.skin, [s * 0.198, -0.01, -0.01], [0, 0, 0], [0.5, 1, 0.75]);
  // hair: low-poly cap + side-part swoop (part on his right, fringe swept up and over to his left)
  addMesh(THREE, H, new THREE.IcosahedronGeometry(0.212, 1), M.hair, [0, 0.075, -0.045], [0.35, 0, 0], [1.03, 0.82, 0.96]);
  addMesh(THREE, H, new THREE.IcosahedronGeometry(0.12, 0), M.hair, [0.03, 0.2, 0.04], [0.5, 0.3, -0.3], [1.5, 0.5, 1.0]);
  addMesh(THREE, H, new THREE.IcosahedronGeometry(0.09, 0), M.hair, [0.12, 0.17, 0.07], [0.2, 0.6, -0.6], [1.2, 0.5, 0.85]);
  addMesh(THREE, H, new THREE.IcosahedronGeometry(0.07, 0), M.hair, [-0.13, 0.15, 0.05], [0.3, 0, 0.4], [1.0, 0.5, 0.8]);
  for (const s of [1, -1]) addMesh(THREE, H, new THREE.IcosahedronGeometry(0.06, 0), M.hair, [s * 0.185, 0.05, -0.04], [0, 0, 0], [0.45, 1.0, 1.1]);
  // face: big eyes with highlights, brows, mouth (smile + open mouth for talking)
  const face = pivot(THREE, H, [0, 0, 0.17]);
  const eyes = [], lids = [];
  for (const s of [1, -1]) {
    const e = addMesh(THREE, face, new THREE.CircleGeometry(0.034, 10), new THREE.MeshBasicMaterial({ color: C.eye }), [s * 0.072, 0.005, 0.012], [0, s * 0.3, 0], [0.85, 1.1, 1]);
    addMesh(THREE, e, new THREE.CircleGeometry(0.011, 8), new THREE.MeshBasicMaterial({ color: 0xffffff }), [s * 0.01, 0.012, 0.001]);
    eyes.push(e);
    const lid = addMesh(THREE, face, new THREE.PlaneGeometry(0.075, 0.08), M.skin, [s * 0.072, 0.045, 0.016], [0, s * 0.3, 0]);
    lid.geometry.translate(0, -0.04, 0); lids.push(lid);
    addMesh(THREE, face, new THREE.BoxGeometry(0.06, 0.013, 0.01), M.hair, [s * 0.074, 0.066, 0.012], [0, s * 0.3, s * -0.08]);
  }
  const smile = addMesh(THREE, face, new THREE.TorusGeometry(0.03, 0.006, 4, 10, Math.PI * 0.8), new THREE.MeshBasicMaterial({ color: C.mouth }), [0, -0.062, 0.012], [0, 0, Math.PI + Math.PI * 0.1]);
  const mouth = addMesh(THREE, face, new THREE.CircleGeometry(0.03, 10), new THREE.MeshBasicMaterial({ color: 0x3a120e }), [0, -0.07, 0.013], [0, 0, 0], [1.1, 0.01, 1]);
  const glasses = new THREE.Group();
  for (const s of [1, -1]) addMesh(THREE, glasses, new THREE.TorusGeometry(0.045, 0.006, 4, 8), M.glasses, [s * 0.072, 0.005, 0.025], [0, s * 0.3, Math.PI / 8]);
  addMesh(THREE, glasses, new THREE.BoxGeometry(0.04, 0.006, 0.006), M.glasses, [0, 0.01, 0.035]);
  glasses.visible = !!opts.glasses; face.add(glasses);

  function pose(p) {
    const P = typeof p === "string" ? DEV_POSES[p] : p || {};
    for (const j of DEV_JOINTS) { const v = P[j] || [0, 0, 0]; rig[j].rotation.set(v[0], v[1], v[2]); }
    // relaxed arms hang slightly out when not posed
    if (!P.armR) rig.armR.rotation.z = -0.12;
    if (!P.armL) rig.armL.rotation.z = 0.12;
    return api;
  }
  function blend(a, b, t) {
    const A = typeof a === "string" ? DEV_POSES[a] : a, B = typeof b === "string" ? DEV_POSES[b] : b, out = {};
    for (const j of DEV_JOINTS) { const va = A[j] || [0, 0, 0], vb = B[j] || [0, 0, 0]; out[j] = va.map((x, i) => lerp(x, vb[i], t)); }
    return out;
  }
  function face_({ blink = 0, talk = 0, mood = "neutral" } = {}) {
    lids.forEach((l) => (l.scale.y = Math.max(0.001, blink)));
    mouth.scale.y = Math.max(0.01, talk * 0.9);
    smile.visible = talk < 0.15;
    const wide = mood === "wide" ? 1.25 : mood === "happy" ? 0.8 : 1;
    eyes.forEach((e) => { e.scale.y = 1.1 * wide; });
    return api;
  }
  const api = { group, rig, pose, blend, face: face_, glasses, height: 0.98 };
  pose("idle");
  return api;
}

/* ------------------------------------------------------------------ */
/*  Bot: the AI sidekick (original design)                             */
/* ------------------------------------------------------------------ */
export function createBot(THREE) {
  const C = { shell: 0xf1f4f9, trim: 0x14b8a6, screen: 0x0a1220, glow: 0x5eead4, warm: 0xfbbf24 };
  const shell = flat(THREE, C.shell, { roughness: 0.45 });
  const trim = flat(THREE, C.trim, { roughness: 0.5 });
  const glowMat = new THREE.MeshBasicMaterial({ color: C.glow });
  const group = new THREE.Group();
  const body = pivot(THREE, group, [0, 0.36, 0]);           // hovers; bob in update()
  addMesh(THREE, body, new THREE.IcosahedronGeometry(0.2, 1), shell, [0, 0, 0], [0, 0, 0], [1.15, 0.92, 0.95]);
  addMesh(THREE, body, new THREE.TorusGeometry(0.2, 0.02, 5, 14), trim, [0, -0.1, 0], [Math.PI / 2, 0, 0], [1.08, 0.9, 1]);
  // screen face
  const sc = new THREE.Shape(); const w = 0.125, h = 0.085, r = 0.04;
  sc.moveTo(-w + r, -h); sc.lineTo(w - r, -h); sc.quadraticCurveTo(w, -h, w, -h + r); sc.lineTo(w, h - r); sc.quadraticCurveTo(w, h, w - r, h);
  sc.lineTo(-w + r, h); sc.quadraticCurveTo(-w, h, -w, h - r); sc.lineTo(-w, -h + r); sc.quadraticCurveTo(-w, -h, -w + r, -h);
  const screenG = new THREE.ExtrudeGeometry(sc, { depth: 0.02, bevelEnabled: true, bevelSize: 0.008, bevelThickness: 0.008, bevelSegments: 1, curveSegments: 4 });
  const face = pivot(THREE, body, [0, 0.03, 0.2]);
  addMesh(THREE, face, screenG, new THREE.MeshStandardMaterial({ color: C.screen, roughness: 0.25, metalness: 0.2 }), [0, 0, -0.01]);
  // eye sets for each mood
  const eyeSets = {};
  const mk = (name, build) => { const g = new THREE.Group(); g.position.z = 0.022; face.add(g); build(g); eyeSets[name] = g; };
  const pill = (g, x, y, sx, sy) => addMesh(THREE, g, new THREE.CircleGeometry(0.03, 12), glowMat, [x, y, 0], [0, 0, 0], [sx, sy, 1]);
  mk("neutral", (g) => { pill(g, -0.05, 0.012, 0.62, 0.95); pill(g, 0.05, 0.012, 0.62, 0.95); });
  mk("wide", (g) => { pill(g, -0.055, 0.015, 0.85, 0.85); pill(g, 0.055, 0.015, 0.85, 0.85); });
  mk("happy", (g) => { for (const x of [-0.052, 0.052]) addMesh(THREE, g, new THREE.TorusGeometry(0.02, 0.007, 4, 10, Math.PI), glowMat, [x, 0.0, 0]); });
  mk("blink", (g) => { for (const x of [-0.052, 0.052]) addMesh(THREE, g, new THREE.PlaneGeometry(0.042, 0.009), glowMat, [x, 0.012, 0]); });
  mk("sly", (g) => { pill(g, -0.05, 0.005, 0.7, 0.45); pill(g, 0.05, 0.005, 0.7, 0.45); });
  const mouth = addMesh(THREE, face, new THREE.CircleGeometry(0.017, 10), glowMat, [0, -0.045, 0.022], [0, 0, 0], [1.4, 0.15, 1]);
  // ears, antenna
  for (const s of [1, -1]) addMesh(THREE, body, new THREE.CylinderGeometry(0.05, 0.05, 0.04, 8), trim, [s * 0.225, 0.0, 0], [0, 0, Math.PI / 2]);
  addMesh(THREE, body, new THREE.CylinderGeometry(0.008, 0.008, 0.12, 5), trim, [0, 0.235, 0]);
  const bulb = addMesh(THREE, body, new THREE.IcosahedronGeometry(0.03, 0), new THREE.MeshBasicMaterial({ color: C.warm }), [0, 0.305, 0]);
  // floating hands
  const hands = [];
  for (const s of [1, -1]) hands.push(addMesh(THREE, group, new THREE.IcosahedronGeometry(0.045, 0), trim, [s * 0.31, 0.3, 0.04]));
  // thruster glow
  const jet = addMesh(THREE, body, new THREE.ConeGeometry(0.06, 0.16, 7, 1, true),
    new THREE.MeshBasicMaterial({ color: C.glow, transparent: true, opacity: 0.55, depthWrite: false, side: THREE.DoubleSide }), [0, -0.27, 0], [Math.PI, 0, 0]);

  let mood = "neutral";
  function face_({ mood: m = "neutral", blink = 0, talk = 0 } = {}) {
    mood = blink > 0.5 ? "blink" : m;
    for (const k in eyeSets) eyeSets[k].visible = k === mood;
    mouth.scale.set(1.4 - 0.4 * talk, 0.15 + 0.85 * talk, 1);
    return api;
  }
  // hover, hands bob, antenna pulse: deterministic in t; gesture: "none" | "point" | "wave" | "shrug"
  function update(t, gesture = "none", g = 1) {
    body.position.y = 0.36 + 0.018 * Math.sin(t * 2.6);
    body.rotation.z = 0.05 * Math.sin(t * 1.3);
    bulb.material.color.setHex(Math.sin(t * 5) > 0 ? C.warm : 0xfde68a);
    jet.scale.y = 0.85 + 0.2 * Math.abs(Math.sin(t * 9));
    hands.forEach((h, i) => {
      const s = i === 0 ? 1 : -1;
      let x = s * 0.31, y = 0.3 + 0.02 * Math.sin(t * 2.6 + i), z = 0.04;
      if (gesture === "point" && i === 1) { x = lerp(x, -0.42, g); y = lerp(y, 0.42, g); z = lerp(z, 0.12, g); }
      if (gesture === "wave" && i === 0) { x = lerp(x, 0.36, g); y = lerp(y, 0.55 + 0.03 * Math.sin(t * 12), g); }
      if (gesture === "shrug") { y = lerp(y, 0.42, g); x = lerp(x, s * 0.36, g); }
      h.position.set(x, y + (body.position.y - 0.36), z);
    });
    return api;
  }
  const api = { group, face: face_, update, height: 0.6 };
  face_({}); update(0);
  return api;
}
