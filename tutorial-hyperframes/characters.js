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
DEV_POSES.crossArms = { armR: [-0.5, 0, -0.35], foreR: [-1.55, 0.4, 0.9], armL: [-0.5, 0, 0.35], foreL: [-1.55, -0.4, -0.9] };
DEV_POSES.handsHips = { armR: [0, 0, -0.65], foreR: [0, 0, 1.9], armL: [0, 0, 0.65], foreL: [0, 0, -1.9] };
DEV_POSES.recoil = { armR: [-0.4, 0, -0.9], foreR: [-1.2, 0, 0.3], armL: [-0.4, 0, 0.9], foreL: [-1.2, 0, -0.3], body: [-0.12, 0, 0], head: [-0.15, 0, 0] };
DEV_POSES.angry = { armR: [0.1, 0, -0.45], foreR: [-0.3, 0, -0.2], armL: [0.1, 0, 0.45], foreL: [-0.3, 0, 0.2], body: [0.12, 0, 0], head: [0.1, 0, 0] };
DEV_POSES.chinThink = { armR: [-0.9, 0, -0.2], foreR: [-2.3, 0, 0.35], armL: [-0.3, 0, 0.35], foreL: [-1.2, 0, -0.6], head: [0.04, 0, 0.14] };
DEV_POSES.thumbBack = { armR: [0.5, 0, -0.55], foreR: [-1.9, 0, 0.6], head: [0, -0.25, 0.05] };
DEV_POSES.amazed = { armR: [-0.3, 0, -1.2], foreR: [-0.6, 0, 0.4], armL: [-0.3, 0, 1.2], foreL: [-0.6, 0, -0.4], body: [-0.06, 0, 0], head: [-0.1, 0, 0] };
DEV_POSES.sleep = { body: [0.72, 0, 0], head: [0.05, -1.35, 0.35], armR: [-1.15, 0, -0.35], foreR: [-1.35, 0.6, 0.9], armL: [-1.15, 0, 0.35], foreL: [-1.35, -0.6, -0.9] };

/* expression presets: brows (y offset, tilt + = angry inner-down, - = worried), eyes (scale, height, look), whites/pupil for shock,
   lids (upper 0..1, squint = lower lid), mouth shape at rest and while talking, blush, sweat, red (anger flush) */
export const DEV_EXPR = {
  neutral:    { browY: 0, browTilt: 0.08, browAsym: 0, eyeS: 1, eyeY: 1, look: 0, white: 0, pupil: 1, lid: 0, squint: 0, mouth: "flat", talkShape: "talk", blush: 0, sweat: 0, red: 0, stars: 0 },
  happy:      { browY: 0.008, browTilt: -0.05, browAsym: 0, eyeS: 1, eyeY: 0.8, look: 0, white: 0, pupil: 1, lid: 0, squint: 0.45, mouth: "grin", talkShape: "grin", blush: 0.6, sweat: 0, red: 0 },
  confused:   { browY: 0.004, browTilt: 0.02, browAsym: 0.018, eyeS: 1, eyeY: 1, look: 0.004, white: 0, pupil: 1, lid: 0, squint: 0, mouth: "smirk", talkShape: "talk", blush: 0, sweat: 0, red: 0 },
  suspicious: { browY: -0.006, browTilt: 0.2, browAsym: 0.012, eyeS: 1, eyeY: 0.75, look: 0.008, white: 0, pupil: 1, lid: 0.35, squint: 0.3, mouth: "flat", talkShape: "talk", blush: 0, sweat: 0, red: 0 },
  unimpressed:{ browY: -0.004, browTilt: 0.04, browAsym: 0, eyeS: 1, eyeY: 0.9, look: 0, white: 0, pupil: 1, lid: 0.5, squint: 0, mouth: "flat", talkShape: "talk", blush: 0, sweat: 0, red: 0 },
  shock:      { browY: 0.015, browTilt: -0.15, browAsym: 0, eyeS: 1.15, eyeY: 1.05, look: 0, white: 1, pupil: 0.45, lid: 0, squint: 0, mouth: "o", talkShape: "o", blush: 0, sweat: 0, red: 0 },
  curious:    { browY: 0.012, browTilt: -0.08, browAsym: 0.006, eyeS: 1.1, eyeY: 1.05, look: 0, white: 0, pupil: 1, lid: 0, squint: 0, mouth: "smile", talkShape: "talk", blush: 0, sweat: 0, red: 0 },
  hopeful:    { browY: 0.014, browTilt: -0.2, browAsym: 0, eyeS: 1.2, eyeY: 1.1, look: 0, white: 0, pupil: 1, lid: 0, squint: 0, mouth: "o", talkShape: "o", blush: 0.4, sweat: 0, red: 0 },
  worried:    { browY: 0.012, browTilt: -0.28, browAsym: 0, eyeS: 1.05, eyeY: 1.0, look: -0.006, white: 0, pupil: 1, lid: 0, squint: 0, mouth: "wavy", talkShape: "talk", blush: 0, sweat: 1, red: 0 },
  horror:     { browY: 0.015, browTilt: -0.3, browAsym: 0, eyeS: 1.2, eyeY: 1.1, look: 0, white: 1, pupil: 0.35, lid: 0, squint: 0, mouth: "wavy", talkShape: "o", blush: 0.9, sweat: 1, red: 0 },
  starstruck: { browY: 0.016, browTilt: -0.14, browAsym: 0, eyeS: 1.1, eyeY: 1, look: 0, white: 0, pupil: 1, lid: 0, squint: 0, mouth: "grin", talkShape: "grin", blush: 0.7, sweat: 0, red: 0, stars: 1 },
  amazed:     { browY: 0.015, browTilt: -0.12, browAsym: 0, eyeS: 1.18, eyeY: 1.05, look: 0, white: 1, pupil: 0.6, lid: 0, squint: 0, mouth: "grin", talkShape: "grin", blush: 0.5, sweat: 0, red: 0 },
  asleep:     { browY: -0.004, browTilt: -0.05, browAsym: 0, eyeS: 1, eyeY: 1, look: 0, white: 0, pupil: 1, lid: 1, squint: 0, mouth: "o", talkShape: "o", blush: 0.3, sweat: 0, red: 0 },
  angry:      { browY: -0.012, browTilt: 0.38, browAsym: 0, eyeS: 1.0, eyeY: 0.85, look: 0, white: 1, pupil: 0.55, lid: 0.15, squint: 0.15, mouth: "frown", talkShape: "shout", blush: 0, sweat: 0, red: 0.75 },
};

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
  // face: eyes (with whites for shock), upper/lower lids, movable brows, a set of mouth shapes, blush, sweat
  const face = pivot(THREE, H, [0, 0, 0.17]);
  const basic = (c, extra = {}) => new THREE.MeshBasicMaterial({ color: c, ...extra });
  const eyes = [], whites = [], lids = [], lows = [], brows = [];
  for (const s of [1, -1]) {
    const wh = addMesh(THREE, face, new THREE.CircleGeometry(0.046, 12), basic(0xffffff), [s * 0.072, 0.005, 0.009], [0, s * 0.3, 0], [0.9, 1.1, 1]);
    whites.push(wh);
    const e = addMesh(THREE, face, new THREE.CircleGeometry(0.034, 10), basic(C.eye), [s * 0.072, 0.005, 0.012], [0, s * 0.3, 0], [0.85, 1.1, 1]);
    addMesh(THREE, e, new THREE.CircleGeometry(0.011, 8), basic(0xffffff), [s * 0.01, 0.012, 0.001]);
    eyes.push(e);
    const lid = addMesh(THREE, face, new THREE.PlaneGeometry(0.1, 0.1), M.skin, [s * 0.072, 0.06, 0.017], [0, s * 0.3, 0]);
    lid.geometry.translate(0, -0.05, 0); lids.push(lid);
    const low = addMesh(THREE, face, new THREE.PlaneGeometry(0.1, 0.1), M.skin, [s * 0.072, -0.05, 0.017], [0, s * 0.3, 0]);
    low.geometry.translate(0, 0.05, 0); lows.push(low);
    const bp = pivot(THREE, face, [s * 0.074, 0.07, 0.02]); bp.rotation.y = s * 0.3;
    addMesh(THREE, bp, new THREE.BoxGeometry(0.064, 0.015, 0.01), M.hair);
    brows.push(bp);
  }
  const mouthMat = basic(0x3a120e), lipMat = basic(C.mouth);
  const MG = pivot(THREE, face, [0, -0.068, 0.014]);
  const mouths = {
    smile: addMesh(THREE, MG, new THREE.TorusGeometry(0.03, 0.006, 4, 12, Math.PI * 0.8), lipMat, [0, 0.008, 0], [0, 0, Math.PI * 1.1]),
    frown: addMesh(THREE, MG, new THREE.TorusGeometry(0.026, 0.006, 4, 12, Math.PI * 0.7), lipMat, [0, -0.02, 0], [0, 0, Math.PI * 0.15]),
    flat: addMesh(THREE, MG, new THREE.BoxGeometry(0.046, 0.008, 0.004), lipMat, [0, -0.004, 0]),
    smirk: addMesh(THREE, MG, new THREE.TorusGeometry(0.024, 0.006, 4, 10, Math.PI * 0.45), lipMat, [0.012, 0.004, 0], [0, 0, Math.PI * 1.45]),
    o: addMesh(THREE, MG, new THREE.CircleGeometry(0.017, 12), mouthMat, [0, -0.006, 0], [0, 0, 0], [0.85, 1.1, 1]),
    grin: addMesh(THREE, MG, new THREE.CircleGeometry(0.034, 12, Math.PI, Math.PI), mouthMat, [0, 0.008, 0]),
    shout: addMesh(THREE, MG, new THREE.CircleGeometry(0.03, 12), mouthMat, [0, -0.01, 0], [0, 0, 0], [1.25, 1.2, 1]),
    talk: addMesh(THREE, MG, new THREE.CircleGeometry(0.028, 12), mouthMat, [0, -0.004, 0]),
  };
  addMesh(THREE, mouths.grin, new THREE.PlaneGeometry(0.05, 0.009), basic(0xffffff), [0, -0.004, 0.001]);
  addMesh(THREE, mouths.shout, new THREE.CircleGeometry(0.014, 8), basic(0xd9485f), [0, -0.016, 0.001], [0, 0, 0], [1.3, 0.7, 1]);
  const wavyPts = Array.from({ length: 9 }, (_, i) => new THREE.Vector3(-0.026 + i * 0.0065, 0.004 * Math.sin(i * 1.6), 0));
  mouths.wavy = addMesh(THREE, MG, new THREE.TubeGeometry(new THREE.CatmullRomCurve3(wavyPts), 24, 0.0035, 4), lipMat, [0, -0.004, 0]);
  const starShapeD = new THREE.Shape();
  for (let i = 0; i < 10; i++) { const a = Math.PI / 2 + (i * Math.PI) / 5, r = i % 2 ? 0.02 : 0.05; i ? starShapeD.lineTo(r * Math.cos(a), r * Math.sin(a)) : starShapeD.moveTo(r * Math.cos(a), r * Math.sin(a)); }
  const starEyes = [1, -1].map((s) => {
    const st = addMesh(THREE, face, new THREE.ExtrudeGeometry(starShapeD, { depth: 0.006, bevelEnabled: false }), basic(0xfacc15), [s * 0.072, 0.008, 0.016], [0, s * 0.3, 0]);
    addMesh(THREE, st, new THREE.ShapeGeometry(starShapeD), basic(0xfff7c2), [0.006, 0.006, 0.007], [0, 0, 0], [0.45, 0.45, 1]);
    st.visible = false; return st;
  });
  const blush = [1, -1].map((s) => addMesh(THREE, face, new THREE.CircleGeometry(0.03, 10), basic(0xff6b8b, { transparent: true, opacity: 0.55 }), [s * 0.115, -0.038, -0.004], [0, s * 0.55, 0], [1.3, 0.7, 1]));
  const sweat = new THREE.Group(); face.add(sweat); sweat.position.set(-0.16, 0.06, -0.03);
  addMesh(THREE, sweat, new THREE.SphereGeometry(0.02, 8, 6), basic(0x7dd3fc), [0, 0, 0], [0, 0, 0], [0.9, 1.1, 0.6]);
  addMesh(THREE, sweat, new THREE.ConeGeometry(0.017, 0.035, 8), basic(0x7dd3fc), [0, 0.028, 0], [0, 0, 0], [0.9, 1, 0.6]);
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
  // expression = brows, eyes, lids, mouth shape, blush, sweat, flush. Numbers blend; shapes switch halfway.
  function face_({ blink = 0, talk = 0, expr = "neutral", to = null, k = 1, t = 0, mood = null } = {}) {
    if (mood && !DEV_EXPR[expr]) expr = mood;
    const A = DEV_EXPR[expr] || DEV_EXPR.neutral, B = to ? DEV_EXPR[to] || A : A, kk = to ? k : 1;
    const X = {}; for (const key in DEV_EXPR.neutral) X[key] = typeof A[key] === "number" ? lerp(A[key], B[key] ?? A[key], kk) : (kk < 0.5 ? A[key] : B[key]);
    brows.forEach((b, i) => {
      const s = i === 0 ? 1 : -1;
      b.position.y = 0.07 + X.browY + (s === 1 ? X.browAsym : 0);
      b.rotation.z = s * X.browTilt;
    });
    // lids and squints squash the eye itself (flat lid planes show as patches on the faceted head)
    const close = Math.max(blink, X.lid), lidK = (1 - 0.9 * close) * (1 - 0.55 * X.squint);
    eyes.forEach((e, i) => {
      const p = X.white > 0.5 ? X.pupil : 1;
      e.scale.set(0.85 * X.eyeS * p, Math.max(0.08, 1.1 * X.eyeS * X.eyeY * p * lidK), 1);
      e.position.set((i === 0 ? 1 : -1) * 0.072 + X.look, 0.005 - 0.014 * close + 0.006 * X.squint, 0.012);
    });
    const stars = X.stars > 0.5;
    starEyes.forEach((st) => { st.visible = stars; st.rotation.z = 0.25 * Math.sin(t * 7); st.scale.setScalar(1 + 0.12 * Math.abs(Math.sin(t * 9))); });
    eyes.forEach((e) => { if (stars) e.scale.set(0.001, 0.001, 1); });
    whites.forEach((w) => { w.visible = X.white > 0.5 && blink < 0.5 && !stars; w.scale.set(0.9 * X.eyeS, 1.1 * X.eyeS * X.eyeY * (1 - 0.6 * X.lid), 1); });
    lids.forEach((l) => (l.visible = false));
    lows.forEach((l) => (l.visible = false));
    for (const m in mouths) mouths[m].visible = false;
    const shape = talk > 0.12 ? (X.talkShape || "talk") : X.mouth;
    mouths[shape].visible = true;
    if (talk > 0.12) mouths[shape].scale.set(shape === "shout" ? 1.25 : 1, (shape === "shout" ? 0.8 : 0.35) + talk * 0.9, 1);
    blush.forEach((b) => { b.visible = X.blush > 0.05; b.material.opacity = 0.6 * X.blush; });
    sweat.visible = X.sweat > 0.5; sweat.position.y = 0.06 - 0.03 * ((t * 0.8) % 1);
    M.skin.emissive.setRGB(0.55 * X.red, 0.02 * X.red, 0.0);
    return api;
  }
  const api = { group, rig, pose, blend, face: face_, glasses, height: 0.98 };
  pose("idle");
  return api;
}

/* ------------------------------------------------------------------ */
/*  Bot: the AI sidekick "Quill" (original design)                     */
/* ------------------------------------------------------------------ */
/* moods: eye shape, gaze, brows, mouth at rest / while talking, extras and body language */
export const BOT_MOODS = {
  neutral:  { eyes: "pill", browY: 0, browTilt: 0, mouth: "smile", talkShape: "grin" },
  happy:    { eyes: "arc", browY: 0.006, mouth: "grin", talkShape: "grin", bounce: 1.6, bounceSpeed: 1.3 },
  proud:    { eyes: "arc", browY: 0.01, browTilt: -0.15, mouth: "grin", talkShape: "grin", sparkle: true, pitch: -0.18, puff: 1.05 },
  smug:     { eyes: "pill", eyeSY: 0.5, eyeY: -0.004, browAsym: 0.016, browTilt: 0.1, mouth: "smirk", talkShape: "grin", tilt: 0.14 },
  innocent: { eyes: "sparkle", eyeS: 1.15, browY: 0.008, browTilt: -0.25, mouth: "smile", talkShape: "o", tilt: -0.12, sparkle: true },
  excited:  { eyes: "star", eyeS: 1.2, browY: 0.012, mouth: "grin", talkShape: "grin", bounce: 3, bounceSpeed: 2.2, lift: 0.02 },
  wide:     { eyes: "ring", eyeS: 1.15, browY: 0.016, mouth: "o", talkShape: "o" },
  nervous:  { eyes: "pill", eyeS: 0.85, look: 0.022, browY: 0.006, browTilt: -0.3, mouth: "wavy", talkShape: "o", sweat: true, shake: true },
  worried:  { eyes: "pill", eyeS: 0.9, browY: 0.008, browTilt: -0.4, mouth: "wavy", talkShape: "o", sweat: true },
  wince:    { eyes: "wince", browTilt: 0.25, browY: -0.004, mouth: "wavy", talkShape: "o", lean: 0.05, pitch: 0.22, alarm: true },
  sly:      { eyes: "pill", eyeSY: 0.45, browTilt: 0.18, mouth: "smirk", talkShape: "grin", tilt: 0.1 },
  cheeky:   { eyes: "arc", eyeS: 1.05, browY: 0.01, browAsym: 0.014, browTilt: 0.22, mouth: "smile", talkShape: "grin", tilt: 0.16, pitch: -0.08, sparkle: true },
};
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
  // eyes: one group per shape (each holds left + right), so moods can switch shapes and shift the gaze
  const starMat = new THREE.MeshBasicMaterial({ color: 0xfde047 });
  const eyeTypes = {}, EZ = 0.022;
  const eyeGroup = (name, build) => { const g = new THREE.Group(); g.position.z = EZ; face.add(g); for (const sx of [-1, 1]) { const e = new THREE.Group(); e.position.x = sx * 0.052; g.add(e); build(e, sx); } eyeTypes[name] = g; };
  eyeGroup("pill", (e) => addMesh(THREE, e, new THREE.CircleGeometry(0.03, 12), glowMat, [0, 0.012, 0], [0, 0, 0], [0.62, 0.95, 1]));
  eyeGroup("arc", (e) => addMesh(THREE, e, new THREE.TorusGeometry(0.02, 0.007, 4, 10, Math.PI), glowMat, [0, 0.0, 0]));
  eyeGroup("line", (e) => addMesh(THREE, e, new THREE.PlaneGeometry(0.042, 0.009), glowMat, [0, 0.012, 0]));
  eyeGroup("ring", (e, sx) => { addMesh(THREE, e, new THREE.TorusGeometry(0.024, 0.006, 5, 14), glowMat, [0, 0.014, 0]); addMesh(THREE, e, new THREE.CircleGeometry(0.009, 8), glowMat, [0.004 * sx, 0.018, 0]); });
  eyeGroup("sparkle", (e) => { addMesh(THREE, e, new THREE.CircleGeometry(0.03, 14), glowMat, [0, 0.013, 0], [0, 0, 0], [0.85, 1, 1]);
    addMesh(THREE, e, new THREE.CircleGeometry(0.009, 8), new THREE.MeshBasicMaterial({ color: 0x0a1220 }), [0.008, 0.024, 0.001]);
    addMesh(THREE, e, new THREE.CircleGeometry(0.005, 6), new THREE.MeshBasicMaterial({ color: 0x0a1220 }), [-0.008, 0.002, 0.001]); });
  const starShape = new THREE.Shape();
  for (let i = 0; i < 10; i++) { const a = Math.PI / 2 + (i * Math.PI) / 5, r = i % 2 ? 0.012 : 0.03; i ? starShape.lineTo(r * Math.cos(a), r * Math.sin(a)) : starShape.moveTo(r * Math.cos(a), r * Math.sin(a)); }
  eyeGroup("star", (e) => addMesh(THREE, e, new THREE.ShapeGeometry(starShape), starMat, [0, 0.012, 0]));
  eyeGroup("wince", (e, sx) => { for (const d of [1, -1]) addMesh(THREE, e, new THREE.PlaneGeometry(0.036, 0.008), glowMat, [0, 0.012 + d * 0.008, 0], [0, 0, d * sx * 0.45]); });
  // brows: glowing bars above the eyes
  const qBrows = [-1, 1].map((sx) => { const b = pivot(THREE, face, [sx * 0.052, 0.058, EZ]); addMesh(THREE, b, new THREE.PlaneGeometry(0.042, 0.008), glowMat); return b; });
  // mouths
  const qm = (geo, pos, rot = [0, 0, 0], sc = [1, 1, 1]) => addMesh(THREE, face, geo, glowMat, pos, rot, sc);
  const qMouths = {
    smile: qm(new THREE.TorusGeometry(0.018, 0.005, 4, 10, Math.PI * 0.8), [0, -0.035, EZ], [0, 0, Math.PI * 1.1]),
    grin: qm(new THREE.CircleGeometry(0.022, 12, Math.PI, Math.PI), [0, -0.04, EZ]),
    o: qm(new THREE.TorusGeometry(0.011, 0.004, 4, 10), [0, -0.05, EZ]),
    flat: qm(new THREE.PlaneGeometry(0.03, 0.006), [0, -0.048, EZ]),
    smirk: qm(new THREE.TorusGeometry(0.016, 0.005, 4, 10, Math.PI * 0.45), [0.01, -0.036, EZ], [0, 0, Math.PI * 1.45]),
    wavy: qm(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(Array.from({ length: 7 }, (_, i) => new THREE.Vector3(-0.018 + i * 0.006, 0.003 * Math.sin(i * 1.8), 0))), 16, 0.003, 4), [0, -0.048, EZ]),
  };
  // sweat drop + sparkles
  const qSweat = new THREE.Group(); body.add(qSweat); qSweat.position.set(0.19, 0.12, 0.1);
  addMesh(THREE, qSweat, new THREE.SphereGeometry(0.02, 8, 6), new THREE.MeshBasicMaterial({ color: 0x7dd3fc }), [0, 0, 0], [0, 0, 0], [0.9, 1.1, 0.6]);
  addMesh(THREE, qSweat, new THREE.ConeGeometry(0.017, 0.035, 8), new THREE.MeshBasicMaterial({ color: 0x7dd3fc }), [0, 0.028, 0], [0, 0, 0], [0.9, 1, 0.6]);
  const sparkles = [[-0.27, 0.2, 0.1], [0.26, 0.24, 0.06], [0.2, -0.08, 0.14]].map((pos) => {
    const g = new THREE.Group(); body.add(g); g.position.set(...pos);
    addMesh(THREE, g, new THREE.ShapeGeometry(starShape), new THREE.MeshBasicMaterial({ color: 0xfde68a, transparent: true, opacity: 0.95 }), [0, 0, 0], [0, 0, 0], [1.2, 1.2, 1]);
    return g;
  });
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

  let cur = BOT_MOODS.neutral;
  function face_({ mood = "neutral", blink = 0, talk = 0, t = 0 } = {}) {
    const X = (cur = BOT_MOODS[mood] || BOT_MOODS.neutral);
    const eyeT = blink > 0.5 && X.eyes !== "star" && X.eyes !== "wince" ? "line" : X.eyes;
    for (const k in eyeTypes) eyeTypes[k].visible = k === eyeT;
    const g = eyeTypes[eyeT];
    g.position.set(X.look || 0, X.eyeY || 0, EZ);
    g.scale.set(X.eyeS || 1, (X.eyeS || 1) * (X.eyeSY || 1), 1);
    g.rotation.z = eyeT === "star" ? 0.3 * Math.sin(t * 6) : 0;
    qBrows.forEach((b, i) => {
      const sx = i === 0 ? -1 : 1;
      b.visible = X.brows !== false;
      b.position.y = 0.058 + (X.browY || 0) + (sx === 1 ? X.browAsym || 0 : 0) + (X.eyeY || 0);
      b.position.x = sx * 0.052 + (X.look || 0);
      b.rotation.z = -sx * (X.browTilt || 0);
    });
    for (const m in qMouths) qMouths[m].visible = false;
    const shape = talk > 0.12 ? (X.talkShape || "grin") : X.mouth;
    qMouths[shape].visible = true;
    qMouths[shape].scale.set(1, talk > 0.12 ? 0.45 + 0.8 * talk : 1, 1);
    qSweat.visible = !!X.sweat; qSweat.position.y = 0.12 - 0.03 * ((t * 0.8) % 1);
    sparkles.forEach((sp, i) => { sp.visible = !!X.sparkle; const k = Math.abs(Math.sin(t * 4 + i * 2)); sp.scale.setScalar(0.4 + 0.8 * k); sp.rotation.z = t * 2 + i; });
    return api;
  }
  // hover, hands, antenna pulse and mood body language, all deterministic in t; gesture: none | point | wave | shrug | cover | cheer
  function update(t, gesture = "none", g = 1) {
    const X = cur, bounce = X.bounce || 1;
    body.position.y = 0.36 + 0.018 * bounce * Math.abs(Math.sin(t * 2.6 * (X.bounceSpeed || 1))) + (X.lift || 0);
    body.position.x = (X.shake ? 0.006 * Math.sin(t * 40) : 0) + (X.lean || 0);
    body.rotation.z = (X.tilt || 0) + 0.05 * Math.sin(t * 1.3);
    body.rotation.x = X.pitch || 0;
    body.scale.setScalar(X.puff || 1);
    bulb.material.color.setHex(X.alarm ? (Math.sin(t * 14) > 0 ? 0xef4444 : 0xfca5a5) : Math.sin(t * 5) > 0 ? C.warm : 0xfde68a);
    jet.scale.y = 0.85 + 0.2 * Math.abs(Math.sin(t * 9));
    hands.forEach((h, i) => {
      const s = i === 0 ? 1 : -1;
      let x = s * 0.31, y = 0.3 + 0.02 * Math.sin(t * 2.6 + i), z = 0.04;
      if (gesture === "point" && i === 1) { x = lerp(x, -0.42, g); y = lerp(y, 0.42, g); z = lerp(z, 0.12, g); }
      if (gesture === "wave" && i === 0) { x = lerp(x, 0.36, g); y = lerp(y, 0.55 + 0.03 * Math.sin(t * 12), g); }
      if (gesture === "shrug") { y = lerp(y, 0.42, g); x = lerp(x, s * 0.36, g); }
      if (gesture === "cover") { x = lerp(x, s * 0.2, g); y = lerp(y, 0.44, g); z = lerp(z, 0.2, g); }
      if (gesture === "cheer") { x = lerp(x, s * 0.34, g); y = lerp(y, 0.62 + 0.03 * Math.sin(t * 10 + i * 3), g); }
      h.position.set(x, y + (body.position.y - 0.36), z);
    });
    return api;
  }
  const api = { group, face: face_, update, height: 0.6 };
  face_({}); update(0);
  return api;
}
