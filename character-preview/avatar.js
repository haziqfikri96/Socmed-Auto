/*
 * Stylised 3D avatar of the channel host, built from Three.js primitives (no model files).
 *
 *   import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.181.2/+esm";
 *   import { createAvatar } from "./avatar.js";
 *   const avatar = createAvatar(THREE);          // ~1.0 units tall, feet at y = 0, facing +z
 *   scene.add(avatar.group);
 *   avatar.pose("peace");                         // or avatar.pose(avatar.blend("idle", "fall", 0.5))
 *
 * Joints are plain THREE.Group pivots in avatar.rig, so a scene can also animate them directly.
 * Character sides: L = the avatar's own left = +x.
 */

const SKIN = 0xc08a64;
const HAIR = 0x141110;
const TEE = 0x1b1b1d;
const STITCH = 0xf2f2f2;
const PANTS = 0xcdbb98;
const BAG = 0xd9ccb2;
const SHOE = 0xf4f4f2;
const SOLE = 0xb9b9b9;
const LIPS = 0x7c4636;
const EYE = 0x1c120d;
const PHONE = 0x6e9fe6;

export const POSES = {
  idle: {},
  peace: {
    shoulderR: [-0.35, 0, -0.32], elbowR: [-2.45, 0, 0.1], wristR: [0.1, Math.PI, 0],
    shoulderL: [0.1, 0, 0.12], elbowL: [-0.5, 0, 0],
    head: [0.04, -0.1, 0.06], hands: { R: "peace" },
  },
  wave: {
    shoulderR: [0, 0, -2.5], elbowR: [-0.3, 0, 0], wristR: [0, Math.PI, 0.2],
    head: [0, -0.08, -0.05], hands: { R: "open" },
  },
  fall: {
    shoulderL: [0, 0, 2.7], shoulderR: [0, 0, -2.7], elbowL: [-0.4, 0, 0], elbowR: [-0.4, 0, 0],
    hipL: [-0.2, 0, 0.3], hipR: [0.2, 0, -0.3], kneeL: [0.5, 0, 0], kneeR: [0.4, 0, 0],
    head: [-0.25, 0, 0], hands: { L: "open", R: "open" },
  },
  crouch: {
    hips: [0.25, 0, 0], spine: [0.15, 0, 0], hipL: [-1.1, 0, 0.1], hipR: [-1.1, 0, -0.1],
    kneeL: [1.6, 0, 0], kneeR: [1.6, 0, 0], ankleL: [-0.7, 0, 0], ankleR: [-0.7, 0, 0],
    shoulderL: [0.9, 0, 0.2], shoulderR: [0.9, 0, -0.2], head: [-0.3, 0, 0],
  },
  jump: {
    spine: [-0.1, 0, 0], shoulderL: [-0.3, 0, 2.3], shoulderR: [-0.3, 0, -2.3],
    hipL: [-0.4, 0, 0.05], hipR: [0.2, 0, -0.05], kneeL: [0.9, 0, 0], kneeR: [0.3, 0, 0],
    head: [-0.15, 0, 0], hands: { L: "open", R: "open" },
  },
  point: {
    shoulderR: [-1.45, 0.25, 0], elbowR: [-0.1, 0, 0], wristR: [0, Math.PI / 2, 0],
    head: [0, -0.15, 0], hands: { R: "point" },
  },
};

const JOINTS = ["hips", "spine", "neck", "head", "shoulderL", "shoulderR", "elbowL", "elbowR",
  "wristL", "wristR", "hipL", "hipR", "kneeL", "kneeR", "ankleL", "ankleR"];

/* rest pose: arms hanging slightly away from the body, palms facing in */
const REST = {
  shoulderL: [0, 0, 0.1], shoulderR: [0, 0, -0.1],
  elbowL: [-0.15, 0, 0], elbowR: [-0.15, 0, 0],
  wristL: [0, -Math.PI / 2, 0], wristR: [0, Math.PI / 2, 0],
};

/* finger curl per grip: [thumb, index, middle, ring, pinky] (radians toward the palm) */
const GRIPS = {
  relaxed: [0.4, 0.45, 0.55, 0.65, 0.75],
  open: [0.1, 0.05, 0.05, 0.08, 0.1],
  fist: [1.3, 2.2, 2.3, 2.3, 2.3],
  peace: [1.3, 0, 0, 2.4, 2.4],
  point: [1.2, 0, 2.3, 2.3, 2.3],
};

export function createAvatar(THREE, opts = {}) {
  const lift = opts.emissiveLift ?? 0; // 0..1: brighten for dark scenes
  const matCache = {};
  const mat = (color, extra = {}) => {
    const key = color + JSON.stringify(extra);
    if (!matCache[key]) {
      const c = new THREE.Color(color);
      matCache[key] = new THREE.MeshStandardMaterial({
        color: c, roughness: 0.6, metalness: 0,
        emissive: c.clone().multiplyScalar(lift), ...extra,
      });
    }
    return matCache[key];
  };
  const skin = mat(SKIN, { roughness: 0.55 });
  const tee = mat(TEE, { roughness: 0.85 });
  const stitch = mat(STITCH, { roughness: 0.7 });
  const pants = mat(PANTS, { roughness: 0.9 });
  const bag = mat(BAG, { roughness: 0.9 });

  const mesh = (geo, material, parent, pos = [0, 0, 0], rot = [0, 0, 0], scale = [1, 1, 1]) => {
    const m = new THREE.Mesh(geo, material);
    m.position.set(...pos); m.rotation.set(...rot); m.scale.set(...scale);
    m.castShadow = m.receiveShadow = true;
    parent.add(m);
    return m;
  };
  const pivot = (parent, pos = [0, 0, 0]) => {
    const g = new THREE.Group();
    g.position.set(...pos);
    parent.add(g);
    return g;
  };
  const capsule = (r, len) => new THREE.CapsuleGeometry(r, len, 8, 20);
  const sphere = (r) => new THREE.SphereGeometry(r, 40, 28);
  const tube = (points, r, closed = false) =>
    new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p)), closed), 96, r, 12, closed);

  const group = new THREE.Group();
  const rig = {};

  /* ---------- hips, pants, torso ---------- */
  rig.hips = pivot(group, [0, 0.445, 0]);
  const pelvisProfile = [[0.001, -0.075], [0.1, -0.07], [0.118, -0.02], [0.12, 0.0], [0.11, 0.02], [0.001, 0.02]];
  mesh(new THREE.LatheGeometry(pelvisProfile.map(([r, y]) => new THREE.Vector2(r, y)), 40), pants, rig.hips, [0, 0, 0], [0, 0, 0], [1, 1, 0.68]);

  rig.spine = pivot(rig.hips, [0, 0, 0]);
  const teeProfile = [[0.001, -0.035], [0.133, -0.035], [0.136, 0.04], [0.138, 0.16], [0.136, 0.23], [0.118, 0.27], [0.08, 0.293], [0.04, 0.3], [0.001, 0.3]];
  mesh(new THREE.LatheGeometry(teeProfile.map(([r, y]) => new THREE.Vector2(r, y)), 48), tee, rig.spine, [0, 0, 0], [0, 0, 0], [1, 1, 0.66]);
  // hem stitch + shoulder seams (white contrast stitching)
  mesh(new THREE.TorusGeometry(0.133, 0.0028, 6, 64), stitch, rig.spine, [0, -0.025, 0], [Math.PI / 2, 0, 0], [1, 0.66, 1]);
  for (const s of [1, -1]) {
    mesh(tube([[s * 0.045, 0.297, 0], [s * 0.09, 0.285, 0.004], [s * 0.12, 0.262, 0.003], [s * 0.14, 0.235, 0]], 0.0028), stitch, rig.spine);
    mesh(tube([[s * 0.133, 0.15, 0.06], [s * 0.137, 0.2, 0.045], [s * 0.14, 0.24, 0.02]], 0.0026), stitch, rig.spine);
  }
  // collar rib
  mesh(new THREE.TorusGeometry(0.046, 0.009, 10, 40), mat(0x262628), rig.spine, [0, 0.293, 0.004], [Math.PI / 2, 0, 0], [1, 0.9, 1]);

  /* ---------- backpack + straps ---------- */
  mesh(capsule(0.1, 0.1), bag, rig.spine, [0, 0.14, -0.13], [0, 0, 0], [1.05, 1, 0.46]);
  mesh(capsule(0.065, 0.04), mat(0xcdbfa4, { roughness: 0.9 }), rig.spine, [0, 0.09, -0.178], [0, 0, 0], [1.1, 1, 0.35]);
  for (const s of [1, -1]) {
    mesh(tube([[s * 0.075, 0.25, -0.1], [s * 0.088, 0.3, -0.03], [s * 0.09, 0.285, 0.06], [s * 0.093, 0.22, 0.098], [s * 0.105, 0.13, 0.1], [s * 0.12, 0.06, 0.07], [s * 0.127, 0.04, 0.0]], 0.0105), bag, rig.spine);
  }

  /* ---------- lanyard + phone ---------- */
  const ropeCanvas = document.createElement("canvas");
  ropeCanvas.width = 64; ropeCanvas.height = 32;
  const rc = ropeCanvas.getContext("2d");
  rc.fillStyle = "#f4f2ee"; rc.fillRect(0, 0, 64, 32);
  rc.fillStyle = "#151515";
  for (let i = -2; i < 6; i++) { rc.beginPath(); rc.moveTo(i * 16, 0); rc.lineTo(i * 16 + 8, 0); rc.lineTo(i * 16 + 24, 32); rc.lineTo(i * 16 + 16, 32); rc.fill(); }
  const ropeTex = new THREE.CanvasTexture(ropeCanvas);
  ropeTex.colorSpace = THREE.SRGBColorSpace;
  ropeTex.wrapS = ropeTex.wrapT = THREE.RepeatWrapping;
  ropeTex.repeat.set(60, 1);
  const rope = new THREE.MeshStandardMaterial({ map: ropeTex, roughness: 0.9, emissive: new THREE.Color(0xffffff).multiplyScalar(lift * 0.3) });
  mesh(tube([[0, 0.305, -0.06], [0.05, 0.3, -0.035], [0.062, 0.29, 0.03], [0.05, 0.24, 0.088], [0.025, 0.17, 0.104], [0, 0.15, 0.106],
    [-0.025, 0.17, 0.104], [-0.05, 0.24, 0.088], [-0.062, 0.29, 0.03], [-0.05, 0.3, -0.035]], 0.0085, true), rope, rig.spine);
  mesh(tube([[0, 0.15, 0.106], [0.03, 0.08, 0.106], [0.06, 0.0, 0.098], [0.075, -0.045, 0.094]], 0.0065), rope, rig.spine);
  const phone = pivot(rig.spine, [0.078, -0.105, 0.098]);
  mesh(new THREE.BoxGeometry(0.052, 0.104, 0.01), mat(PHONE, { metalness: 0.5, roughness: 0.35 }), phone, [0, 0, 0], [0.1, -0.15, 0.08]);
  mesh(new THREE.BoxGeometry(0.044, 0.094, 0.002), mat(0x0b0d12, { roughness: 0.2 }), phone, [0, 0, 0.0055], [0.1, -0.15, 0.08]);
  rig.phone = phone;

  /* ---------- neck + head ---------- */
  rig.neck = pivot(rig.spine, [0, 0.29, 0]);
  mesh(new THREE.CylinderGeometry(0.036, 0.041, 0.09, 24), skin, rig.neck, [0, 0.035, 0]);
  rig.head = pivot(rig.neck, [0, 0.07, 0]);
  const H = pivot(rig.head, [0, 0.085, 0.004]); // head centre
  const headProfile = [];
  for (let i = 0; i <= 32; i++) {
    const a = (i / 32) * Math.PI; // 0 = chin, PI = crown
    const y = -Math.cos(a) * 0.122;
    const taper = y < 0 ? 1 - 0.2 * Math.pow(-y / 0.122, 2.2) : 1; // narrower jaw and chin
    headProfile.push(new THREE.Vector2(Math.max(0.001, Math.sin(a) * 0.112 * taper), y));
  }
  mesh(new THREE.LatheGeometry(headProfile, 48), skin, H, [0, 0, 0], [0, 0, 0], [0.92, 1, 0.98]);
  for (const s of [1, -1]) {
    mesh(sphere(0.026), skin, H, [s * 0.103, -0.005, -0.01], [0, 0, s * 0.15], [0.45, 1.05, 0.75]); // ears
    // eyes
    mesh(sphere(0.0125), mat(EYE, { roughness: 0.25 }), H, [s * 0.038, 0.008, 0.096], [0, s * 0.3, 0], [1.2, 0.78, 0.6]);
    mesh(sphere(0.0034), mat(0xffffff, { roughness: 0.1, emissive: new THREE.Color(0xffffff).multiplyScalar(0.4) }), H, [s * 0.038 + 0.004, 0.012, 0.104]);
    // brows: thick, nearly straight
    mesh(capsule(0.0062, 0.026), mat(HAIR, { roughness: 0.7 }), H, [s * 0.04, 0.036, 0.1], [0, s * 0.38, Math.PI / 2 + s * 0.08]);
    // nostril wings
    mesh(sphere(0.0072), skin, H, [s * 0.012, -0.031, 0.097]);
  }
  mesh(sphere(0.0145), skin, H, [0, -0.024, 0.104], [0.2, 0, 0], [1, 1.15, 1]); // nose
  // closed-mouth smile
  const arc = 0.5 * Math.PI;
  mesh(new THREE.TorusGeometry(0.019, 0.0031, 8, 24, arc), mat(LIPS), H, [0, -0.047, 0.094], [-0.25, 0, -Math.PI / 2 - arc / 2]);

  /* hair: slick, swept back, glossy */
  const hair = mat(HAIR, { roughness: 0.55 });
  // hairline mask: high on the forehead, just above the ears at the sides, down to the nape at the back
  const hc = document.createElement("canvas");
  hc.width = 1024; hc.height = 512;
  const hx = hc.getContext("2d");
  hx.fillStyle = "#fff";
  hx.beginPath();
  hx.moveTo(0, 0);
  for (let x = 0; x <= 1024; x += 4) {
    const front = Math.sin((x / 1024) * Math.PI * 2); // +1 front (+z), -1 back
    const edge = front > 0 ? 1.36 - 0.42 * Math.pow(front, 1.5) : 1.36 - 0.6 * front; // polar angle of the hairline
    hx.lineTo(x, (edge / Math.PI) * 512);
  }
  hx.lineTo(1024, 0);
  hx.fill();
  const hairMask = new THREE.CanvasTexture(hc);
  const hairShell = new THREE.MeshStandardMaterial({
    color: hair.color, roughness: 0.55, emissive: hair.emissive, alphaMap: hairMask, alphaTest: 0.5, side: THREE.DoubleSide,
  });
  mesh(new THREE.SphereGeometry(0.119, 64, 40), hairShell, H, [0, 0.005, -0.004], [0, 0, 0], [0.97, 1.06, 1.04]);
  mesh(sphere(0.07), hair, H, [-0.006, 0.088, 0.0], [-0.35, 0.06, 0.04], [1.4, 0.5, 1.45]); // swept-back volume

  /* ---------- arms ---------- */
  const hands = {};
  for (const side of ["L", "R"]) {
    const s = side === "L" ? 1 : -1;
    const sh = (rig["shoulder" + side] = pivot(rig.spine, [s * 0.14, 0.245, 0]));
    mesh(capsule(0.032, 0.11), skin, sh, [0, -0.075, 0]);
    mesh(new THREE.CylinderGeometry(0.05, 0.054, 0.1, 28), tee, sh, [0, -0.033, 0]);
    mesh(new THREE.TorusGeometry(0.054, 0.0026, 6, 40), stitch, sh, [0, -0.08, 0], [Math.PI / 2, 0, 0]);
    const el = (rig["elbow" + side] = pivot(sh, [0, -0.135, 0]));
    mesh(capsule(0.029, 0.095), skin, el, [0, -0.06, 0]);
    if (side === "R") { // black sport watch
      mesh(new THREE.CylinderGeometry(0.0315, 0.0315, 0.022, 28), mat(0x111111, { roughness: 0.4 }), el, [0, -0.1, 0]);
      mesh(new THREE.BoxGeometry(0.03, 0.026, 0.012), mat(0x1e1e1e, { roughness: 0.2, metalness: 0.4 }), el, [0, -0.1, 0.029]);
    }
    const wr = (rig["wrist" + side] = pivot(el, [0, -0.122, 0]));
    mesh(sphere(0.03), skin, wr, [0, -0.028, 0], [0, 0, 0], [1, 1.12, 0.55]);
    const fingers = [];
    [-0.018, -0.006, 0.006, 0.018].forEach((fx, i) => {
      const f = pivot(wr, [fx * s * -1, -0.055, 0.002]);
      mesh(capsule(0.0072, i === 0 || i === 3 ? 0.024 : 0.03), skin, f, [0, -0.018, 0]);
      fingers.push(f);
    });
    const thumb = pivot(wr, [s * -0.026, -0.022, 0.008]);
    mesh(capsule(0.0085, 0.024), skin, thumb, [0, -0.016, 0]);
    thumb.rotation.z = s * 0.6;
    hands[side] = { thumb, fingers }; // fingers ordered index..pinky
  }
  rig.hands = hands;

  /* ---------- legs ---------- */
  for (const side of ["L", "R"]) {
    const s = side === "L" ? 1 : -1;
    const hp = (rig["hip" + side] = pivot(rig.hips, [s * 0.062, -0.04, 0]));
    mesh(capsule(0.054, 0.14), pants, hp, [0, -0.095, 0]);
    const kn = (rig["knee" + side] = pivot(hp, [0, -0.19, 0]));
    mesh(capsule(0.047, 0.12), pants, kn, [0, -0.085, 0]);
    const an = (rig["ankle" + side] = pivot(kn, [0, -0.17, 0]));
    mesh(capsule(0.038, 0.07), mat(SHOE, { roughness: 0.6 }), an, [0, -0.012, 0.022], [Math.PI / 2, 0, 0], [1, 1, 0.75]);
    mesh(capsule(0.04, 0.072), mat(SOLE, { roughness: 0.8 }), an, [0, -0.032, 0.022], [Math.PI / 2, 0, 0], [1.02, 1.02, 0.28]);
  }

  /* ---------- posing ---------- */
  const setGrip = (side, grip) => {
    const c = GRIPS[grip] || GRIPS.relaxed;
    const h = hands[side];
    h.thumb.rotation.x = -c[0] * 0.6;
    h.fingers.forEach((f, i) => {
      f.rotation.x = -c[i + 1];
      f.rotation.z = 0;
    });
    if (grip === "peace") {
      const s = side === "L" ? 1 : -1;
      h.fingers[0].rotation.z = s * 0.16;
      h.fingers[1].rotation.z = -s * 0.16;
    }
  };

  function pose(p) {
    const P = typeof p === "string" ? POSES[p] : p;
    for (const j of JOINTS) {
      const v = (P && P[j]) || REST[j] || [0, 0, 0];
      rig[j].rotation.set(v[0], v[1], v[2]);
    }
    const hp = (P && P.hands) || {};
    setGrip("L", hp.L || "relaxed");
    setGrip("R", hp.R || "relaxed");
    return api;
  }

  /* mix two poses (names or objects); hands switch at t = 0.5 */
  function blend(a, b, t) {
    const A = typeof a === "string" ? POSES[a] : a;
    const B = typeof b === "string" ? POSES[b] : b;
    const out = { hands: t < 0.5 ? A.hands : B.hands };
    for (const j of JOINTS) {
      const va = A[j] || REST[j] || [0, 0, 0];
      const vb = B[j] || REST[j] || [0, 0, 0];
      out[j] = va.map((x, i) => x + (vb[i] - x) * t);
    }
    return out;
  }

  const api = { group, rig, pose, blend, poses: POSES, height: 1.03 };
  pose("idle");
  return api;
}
