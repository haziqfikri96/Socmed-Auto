/*
 * Stylised 3D avatar of the channel host, built from Three.js primitives (no model files).
 * Design follows the host's own character sheet (characters/reference-sheet.jpg): side-part black
 * hair, oversized black tee with a "Shichi.AI" print, khaki chinos, navy sneakers.
 * opts.print changes the chest text; opts.emissiveLift brightens it for dark scenes.
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

const SKIN = 0xc78c68;
const HAIR = 0x141110;
const TEE = 0x1b1b1d;
const PANTS = 0xc4b08e;
const SHOE = 0x2b2f3f;
const SOLE = 0xb9b5ae;
const LIPS = 0x8e5444;
const EYE = 0x1c120d;

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
  const pants = mat(PANTS, { roughness: 0.9 });

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
  const teeProfile = [[0.001, -0.07], [0.138, -0.07], [0.139, 0.04], [0.138, 0.16], [0.136, 0.23], [0.118, 0.27], [0.08, 0.293], [0.04, 0.3], [0.001, 0.3]];
  mesh(new THREE.LatheGeometry(teeProfile.map(([r, y]) => new THREE.Vector2(r, y)), 48), tee, rig.spine, [0, 0, 0], [0, 0, 0], [1, 1, 0.66]);
  // collar rib
  mesh(new THREE.TorusGeometry(0.046, 0.009, 10, 40), mat(0x262628), rig.spine, [0, 0.293, 0.004], [Math.PI / 2, 0, 0], [1, 0.9, 1]);

  /* chest print (distressed light-grey sans) */
  const pc = document.createElement("canvas");
  pc.width = 1024; pc.height = 200;
  const px = pc.getContext("2d");
  px.fillStyle = "#d4d4d4";
  px.font = "bold 150px 'DejaVu Sans', 'Liberation Sans', Arial, sans-serif";
  px.textAlign = "center"; px.textBaseline = "middle";
  px.fillText(opts.print ?? "Shichi.AI", 512, 104, 1000);
  px.globalCompositeOperation = "destination-out"; // worn print texture
  let seed = 7;
  const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  for (let i = 0; i < 2600; i++) px.fillRect(rnd() * 1024, rnd() * 200, 1 + rnd() * 3, 1 + rnd() * 3);
  const printTex = new THREE.CanvasTexture(pc);
  printTex.colorSpace = THREE.SRGBColorSpace;
  printTex.anisotropy = 4;
  mesh(new THREE.CylinderGeometry(0.1415, 0.1415, 0.05, 48, 1, true, -0.78, 1.56),
    new THREE.MeshStandardMaterial({ map: printTex, transparent: true, alphaTest: 0.3, roughness: 0.9, emissive: new THREE.Color(0xd4d4d4).multiplyScalar(lift * 0.3), emissiveMap: printTex }),
    rig.spine, [0, 0.19, 0], [0, 0, 0], [1, 1, 0.66]);

  /* ---------- neck + head ---------- */
  rig.neck = pivot(rig.spine, [0, 0.29, 0]);
  mesh(new THREE.CylinderGeometry(0.036, 0.041, 0.09, 24), skin, rig.neck, [0, 0.035, 0]);
  rig.head = pivot(rig.neck, [0, 0.07, 0]);
  const H = pivot(rig.head, [0, 0.085, 0.004]); // head centre
  const headProfile = [];
  for (let i = 0; i <= 32; i++) {
    const a = (i / 32) * Math.PI; // 0 = chin, PI = crown
    const y = -Math.cos(a) * 0.122;
    const taper = y < 0 ? 1 - 0.16 * Math.pow(-y / 0.122, 2.2) : 1; // narrower jaw and chin
    headProfile.push(new THREE.Vector2(Math.max(0.001, Math.sin(a) * 0.112 * taper), y));
  }
  mesh(new THREE.LatheGeometry(headProfile, 48), skin, H, [0, 0, 0], [0, 0, 0], [0.92, 1, 0.98]);
  for (const s of [1, -1]) {
    mesh(sphere(0.03), skin, H, [s * 0.103, -0.006, -0.008], [0, 0, s * 0.18], [0.45, 1.05, 0.75]); // ears
    // eyes: white, brown iris, pupil, catch-light, lash line
    const ex = s * 0.039, ey = 0.006;
    mesh(sphere(0.019), mat(0xfafafa, { roughness: 0.2 }), H, [ex, ey, 0.09], [0, s * 0.32, 0], [1, 1.08, 0.6]);
    mesh(sphere(0.0118), mat(0x5a3420, { roughness: 0.2 }), H, [ex + s * 0.001, ey - 0.001, 0.1], [0, s * 0.32, 0], [1, 1, 0.45]);
    mesh(sphere(0.0062), mat(0x0c0806, { roughness: 0.15 }), H, [ex + s * 0.0015, ey - 0.001, 0.1045], [0, s * 0.32, 0], [1, 1, 0.45]);
    mesh(sphere(0.0033), mat(0xffffff, { roughness: 0.1, emissive: new THREE.Color(0xffffff).multiplyScalar(0.5) }), H, [ex + 0.004, ey + 0.005, 0.107]);
    mesh(new THREE.TorusGeometry(0.0185, 0.0022, 6, 24, Math.PI * 0.85), mat(0x1a120e), H, [ex, ey + 0.001, 0.094], [0.05, s * 0.32, Math.PI * 0.075], [1, 1.1, 0.6]);
    // brows: thick, gently arched
    mesh(new THREE.TorusGeometry(0.05, 0.0047, 8, 24, 0.55), mat(HAIR, { roughness: 0.7 }), H, [s * 0.04, -0.008, 0.098], [0, s * 0.32, Math.PI / 2 - 0.275 - s * 0.06], [1, 1, 0.8]);
    // nostril wings
    mesh(sphere(0.0062), skin, H, [s * 0.011, -0.031, 0.096]);
  }
  mesh(sphere(0.013), skin, H, [0, -0.024, 0.103], [0.2, 0, 0], [1, 1.15, 1]); // nose
  // closed-mouth smile
  const arc = 0.55 * Math.PI;
  mesh(new THREE.TorusGeometry(0.022, 0.003, 8, 24, arc), mat(LIPS), H, [0, -0.049, 0.093], [-0.25, 0, -Math.PI / 2 - arc / 2]);

  /* hair: side part on the character's right, fringe swept up and over to the left */
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
  mesh(sphere(0.08), hair, H, [0.012, 0.074, -0.006], [-0.1, 0, 0.12], [1.32, 0.62, 1.38]); // top volume, heavier on the left
  mesh(sphere(0.075), hair, H, [0.014, 0.078, 0.022], [0.22, 0, 0.16], [1.22, 0.44, 1.05]); // fringe swept up and across

  /* ---------- arms ---------- */
  const hands = {};
  for (const side of ["L", "R"]) {
    const s = side === "L" ? 1 : -1;
    const sh = (rig["shoulder" + side] = pivot(rig.spine, [s * 0.14, 0.245, 0]));
    mesh(capsule(0.032, 0.11), skin, sh, [0, -0.075, 0]);
    mesh(new THREE.CylinderGeometry(0.048, 0.054, 0.14, 28), tee, sh, [0, -0.053, 0]);
    mesh(new THREE.TorusGeometry(0.05, 0.005, 8, 32), tee, sh, [0, -0.122, 0], [Math.PI / 2, 0, 0]); // sleeve hem
    mesh(sphere(0.044), tee, sh, [-Math.sign(sh.position.x) * 0.006, 0.006, 0], [0, 0, 0], [1, 0.45, 1]); // rounded shoulder
    const el = (rig["elbow" + side] = pivot(sh, [0, -0.135, 0]));
    mesh(capsule(0.029, 0.095), skin, el, [0, -0.06, 0]);
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
    mesh(capsule(0.038, 0.088), mat(SHOE, { roughness: 0.75 }), an, [0, -0.012, 0.026], [Math.PI / 2, 0, 0], [1, 1, 0.78]);
    mesh(new THREE.BoxGeometry(0.02, 0.004, 0.045), mat(0x3a3f52, { roughness: 0.8 }), an, [0, 0.016, 0.03], [0.25, 0, 0]); // laces
    mesh(capsule(0.039, 0.087), mat(SOLE, { roughness: 0.8 }), an, [0, -0.033, 0.025], [Math.PI / 2, 0, 0], [1.03, 1.03, 0.24]);
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
