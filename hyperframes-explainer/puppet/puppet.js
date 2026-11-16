/*
 * The channel host as a 2D cut-out puppet made from the user's own character art
 * (characters/reference-sheet.jpg, front view). The art is used pixel for pixel;
 * only the joints move.
 *
 *   import { createPuppet } from "./puppet/puppet.js";
 *   const host = createPuppet(document.getElementById("stage"), { base: "./puppet/", height: 1200 });
 *   host.el.style.left = "540px"; host.el.style.top = "1700px";   // el's origin = between the feet
 *   host.pose("wave");                      // or host.pose(host.blend("idle", "wave", 0.5))
 *   host.face({ blink: 1, talk: 0.6 });      // 0..1
 *
 * Angles are degrees, CSS convention (positive = clockwise on screen).
 * The character's R side is on the viewer's left.
 * Parts are plain <img> elements, so HyperFrames waits for them before capturing frames.
 */
import { RIG } from "./rig.js";

export const POSES = {
  idle: {},
  wave: { shoulderR: 128, elbowR: -22, head: -4 },
  waveL: { shoulderL: -128, elbowL: 22, head: 4 },
  point: { shoulderR: 66, elbowR: 4, head: -6 },        // arm straight out to the viewer's left
  pointL: { shoulderL: -66, elbowL: -4, head: 6 },
  armsUp: { shoulderR: 150, shoulderL: -150, elbowR: -10, elbowL: 10, head: 0 },
  cheer: { shoulderR: 135, shoulderL: -135, elbowR: -35, elbowL: 35, hipR: 8, hipL: -8 },
  star: { shoulderR: 105, shoulderL: -105, hipR: 16, hipL: -16, kneeR: -6, kneeL: 6 },
  fall: { shoulderR: 155, shoulderL: -140, elbowR: -25, elbowL: 40, hipR: 18, hipL: -10, kneeR: -15, kneeL: 20, head: 10 },
  handOnChest: { shoulderR: -8, elbowR: -150, head: 8, front: ["R"] },
  handOnChestL: { shoulderL: 8, elbowL: 150, head: -8, front: ["L"] },
};

const JOINTS = ["root", "head", "shoulderR", "elbowR", "shoulderL", "elbowL", "hipR", "kneeR", "hipL", "kneeL"];

export function createPuppet(container, opts = {}) {
  const base = opts.base ?? "./puppet/";
  const J = RIG.joints;
  const top = RIG.parts.head.box[1];
  const s = (opts.height ?? 1000) / (RIG.feet_y - top); // source px -> screen px
  const feet = [J.hips[0], RIG.feet_y];

  const div = (parent, css = "") => {
    const d = document.createElement("div");
    d.style.cssText = "position:absolute;left:0;top:0;transform-origin:0 0;" + css;
    parent.appendChild(d);
    return d;
  };
  // a joint node sits at its pivot, positioned relative to the parent's pivot
  const node = (parent, pivot, parentPivot) =>
    div(parent, `left:${(pivot[0] - parentPivot[0]) * s}px;top:${(pivot[1] - parentPivot[1]) * s}px;`);
  const img = (parent, name, pivot) => {
    const [x0, y0, x1, y1] = RIG.parts[name].box;
    const i = document.createElement("img");
    i.src = base + name + ".png";
    i.alt = "";
    i.draggable = false;
    i.style.cssText = `position:absolute;left:${(x0 - pivot[0]) * s}px;top:${(y0 - pivot[1]) * s}px;width:${(x1 - x0) * s}px;height:${(y1 - y0) * s}px;`;
    parent.appendChild(i);
    return i;
  };

  const el = div(container, "width:0;height:0;");           // origin: between the feet
  const rig = {};
  rig.root = node(el, J.hips, feet);
  // hip piece, then legs (behind everything else)
  img(rig.root, "pelvis", J.hips);
  for (const side of ["R", "L"]) {
    rig["hip" + side] = node(rig.root, J["hip" + side], J.hips);
    img(rig["hip" + side], "thigh" + side, J["hip" + side]);
    rig["knee" + side] = node(rig["hip" + side], J["knee" + side], J["hip" + side]);
    img(rig["knee" + side], "shin" + side, J["knee" + side]);
  }
  // arms, then head, then the shirt on top
  for (const side of ["R", "L"]) {
    rig["shoulder" + side] = node(rig.root, J["shoulder" + side], J.hips);
    rig["shoulder" + side].style.zIndex = 2;
    img(rig["shoulder" + side], "upperArm" + side, J["shoulder" + side]);
    rig["elbow" + side] = node(rig["shoulder" + side], J["elbow" + side], J["shoulder" + side]);
    img(rig["elbow" + side], "forearm" + side, J["elbow" + side]);
  }
  rig.head = node(rig.root, J.neck, J.hips);
  rig.head.style.zIndex = 3;
  img(rig.head, "head", J.neck);

  // eyelids (blink) and mouth (talk), drawn over the head art
  const E = RIG.eyes;
  const lidColor = `rgb(${E.lid.join(",")})`;
  const lids = ["R", "L"].map((side) => {
    const [cx, cy] = E[side];
    const [w, h] = E.size;
    return div(rig.head, `left:${(cx - w / 2 - J.neck[0]) * s}px;top:${(cy - h / 2 - 2 - J.neck[1]) * s}px;width:${w * s}px;height:${(h + 3) * s}px;`
      + `background:linear-gradient(${lidColor} 0%, ${lidColor} 78%, #4a2a1c 92%, rgba(74,42,28,0) 100%);border-radius:50% 50% 50% 50% / 60% 60% 40% 40%;filter:blur(${0.6 * s}px);transform:scaleY(0);`);
  });
  const M = E.mouth ?? [476, 333];
  const mouth = div(rig.head, `left:${(M[0] - 24 - J.neck[0]) * s}px;top:${(M[1] - 4 - J.neck[1]) * s}px;width:${48 * s}px;height:${26 * s}px;`
    + `background:radial-gradient(ellipse at 50% 30%, #6b2a22 0%, #4a1913 70%);border-radius:40% 40% 50% 50%;`
    + `box-shadow:inset 0 ${4 * s}px 0 ${0}px #f4ede8;transform:scaleY(0);`);

  const torso = img(rig.root, "torso", J.hips);
  torso.style.zIndex = 4;

  const toPose = (p) => (typeof p === "string" ? POSES[p] : p) || {};

  function pose(p) {
    const P = toPose(p);
    for (const j of JOINTS) {
      const a = P[j] ?? 0;
      if (j === "root") continue;
      rig[j].style.transform = `rotate(${a}deg)`;
    }
    rig.root.style.transform = `rotate(${P.root ?? 0}deg)`;
    for (const side of ["R", "L"]) rig["shoulder" + side].style.zIndex = (P.front || []).includes(side) ? 5 : 2;
    return api;
  }

  /* mix two poses (names or objects) */
  function blend(a, b, t) {
    const A = toPose(a), B = toPose(b), out = { front: (t < 0.5 ? A : B).front };
    for (const j of JOINTS) out[j] = (A[j] ?? 0) + ((B[j] ?? 0) - (A[j] ?? 0)) * t;
    return out;
  }

  /* blink: 0 open .. 1 closed; talk: 0 closed .. 1 open */
  function face({ blink = 0, talk = 0 } = {}) {
    lids.forEach((l) => (l.style.transform = `scaleY(${Math.min(1, Math.max(0, blink))})`));
    mouth.style.transform = `scaleY(${Math.min(1, Math.max(0, talk))})`;
    return api;
  }

  /* place the puppet: x, y = screen position of the point between the feet; scale; squash (1 = none) */
  function place({ x = 0, y = 0, scale = 1, rotate = 0, squash = 1, flip = false } = {}) {
    el.style.transform = `translate(${x}px, ${y}px) rotate(${rotate}deg) scale(${scale * (flip ? -1 : 1) / Math.sqrt(squash)}, ${scale * squash})`;
    return api;
  }

  const api = { el, rig, pose, blend, face, place, poses: POSES, height: (RIG.feet_y - top) * s };
  pose("idle");
  return api;
}
