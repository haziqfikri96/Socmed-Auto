/*
 * Host character from a GLB (characters/glb/character.glb), with an animation state controller.
 *
 *   import * as THREE from "three";
 *   import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
 *   import { loadCharacter } from "./character.js";
 *   window.THREE = THREE;                       // lets HyperFrames wait for the model before capturing
 *   const host = await loadCharacter(THREE, GLTFLoader, "assets/character.glb", { height: 1 });
 *   scene.add(host.root);
 *
 * Two ways to drive it:
 *   - Timeline (renders, deterministic):  host.setSchedule([[0, "Idle"], [3.3, "Pointing"], ...]); host.evaluate(t);
 *     The state at time t, the 0.4 s cross-fades and every clip's playhead are worked out from t alone,
 *     so any frame can be rendered in any order and always looks the same.
 *   - Live (interactive pages): host.play("Talking") cross-fades over 0.4 s; call host.update(clock.getDelta())
 *     from requestAnimationFrame.
 *
 * States are names like "Idle", "Talking", "Pointing", "Cheer". opts.clipMap maps a state to a clip name in
 * the file; by default a state uses the clip whose name contains the state name (case-insensitive).
 * A state with no clip falls back to procedural motion (breathing, nods, turning to point), which is all a
 * model without a skeleton can do.
 */

export const FADE = 0.4;

// placeholder colour regions for the current untextured Meshy export (fractions of its bounding box)
export const SHICHI_PAINT = {
  hem: 0.44, legX: 0.25, neck: 0.81, torsoX: 0.25, sleeve: 0.62, sleeveX: 0.41,
  hairTop: 0.93, hairTopFront: 0.952, frontZ: 0.18, hairBackZ: -0.14, hairBackU: 0.847, hairSideX: 0.081, hairSideU: 0.905,
  eyeU: 0.909, eyeH: 0.0065, eyeX: 0.047, eyeW: 0.016, eyeZ: 0.24, browU: 0.926, browH: 0.0035,
};

const PROCEDURAL = {
  // rigid-body motion for models without bones: [lean (rad), turn (rad), bob amplitude, bob speed, nod]
  Idle: [0, 0, 0.004, 2.2, 0],
  Talking: [0.02, 0, 0.006, 5.5, 0.02],
  Pointing: [0.04, 0.45, 0.004, 2.2, 0.01],
  Cheer: [-0.03, 0, 0.03, 9.0, 0],
};

export async function loadCharacter(THREE, GLTFLoader, url, opts = {}) {
  const gltf = await new GLTFLoader().loadAsync(url);
  const model = gltf.scene;
  const clips = gltf.animations || [];
  console.log(`[character] ${url}: ${clips.length} animation clip(s)`, clips.map((c) => `${c.name} (${c.duration.toFixed(2)}s)`));

  // normalise: feet on y = 0, centred, given height, facing +z
  const box = new THREE.Box3().setFromObject(model);
  const size = box.getSize(new THREE.Vector3());
  const k = (opts.height ?? 1) / size.y;
  model.scale.setScalar(k);
  model.position.set(-((box.min.x + box.max.x) / 2) * k, -box.min.y * k, -((box.min.z + box.max.z) / 2) * k);

  let skinned = false, textured = false;
  model.traverse((o) => {
    if (!o.isMesh) return;
    o.castShadow = true;
    o.receiveShadow = true;
    if (o.isSkinnedMesh) { skinned = true; o.frustumCulled = false; }
    for (const m of [].concat(o.material)) {
      if (m.map) { textured = true; m.map.colorSpace = THREE.SRGBColorSpace; m.map.anisotropy = 4; }
      // keep materials out of the "plastic" and "chrome" extremes so they sit with the scene lighting
      if ("metalness" in m) m.metalness = Math.min(m.metalness, 0.1);
      if ("roughness" in m) m.roughness = clamp(m.roughness, 0.45, 0.85);
      if ("envMapIntensity" in m) m.envMapIntensity = opts.envIntensity ?? 0.7;
    }
  });
  console.log(`[character] skeleton: ${skinned ? "yes" : "no"}, textures: ${textured ? "yes" : "no"}`);
  if (!textured && opts.paint) paintPlaceholder(THREE, model, opts.paint);

  // the pivot moves the whole body (procedural motion); the model inside keeps its own transform
  const root = new THREE.Group();
  const pivot = new THREE.Group();
  pivot.add(model);
  root.add(pivot);

  const mixer = new THREE.AnimationMixer(model);
  const actions = {};
  const clipFor = (state) => {
    const want = opts.clipMap?.[state];
    return clips.find((c) => c.name === want) || clips.find((c) => c.name.toLowerCase().includes(state.toLowerCase())) || null;
  };
  const actionFor = (state) => {
    if (!(state in actions)) {
      const clip = clipFor(state);
      actions[state] = clip ? mixer.clipAction(clip) : null;
      if (actions[state]) { actions[state].enabled = true; actions[state].setEffectiveWeight(0); actions[state].play(); }
    }
    return actions[state];
  };

  /* ---------- timeline-driven (deterministic) ---------- */
  let schedule = [[0, "Idle"]];
  function setSchedule(keys) { schedule = keys.slice().sort((a, b) => a[0] - b[0]); }

  // weight of each state at time t: the current state fades in over FADE while the previous fades out
  function weightsAt(t) {
    let i = 0;
    while (i < schedule.length - 1 && t >= schedule[i + 1][0]) i++;
    const [t0, cur] = schedule[i];
    const w = {};
    const f = i === 0 ? 1 : clamp((t - t0) / FADE, 0, 1);
    w[cur] = f;
    if (f < 1) {
      // a state can be interrupted mid-fade: blend in whatever was showing at t0
      const prev = weightsAt(t0 - 1e-6);
      for (const s in prev) w[s] = (w[s] || 0) + prev[s] * (1 - f);
    }
    return w;
  }
  const startOf = (state, t) => { // when the state's current run began (clip playheads restart per run)
    let s = 0;
    for (const [tk, st] of schedule) { if (tk > t) break; if (st === state) s = tk; }
    return s;
  };

  function evaluate(t) {
    const w = weightsAt(t);
    for (const state of new Set([...schedule.map((s) => s[1]), ...Object.keys(actions)])) {
      const a = actionFor(state);
      if (!a) continue;
      a.setEffectiveWeight(w[state] || 0);
      a.time = (t - startOf(state, t)) % a.getClip().duration;
    }
    mixer.update(0);
    applyProcedural(w, t);
  }

  function applyProcedural(w, t) {
    let lean = 0, turn = 0, bob = 0, nod = 0, total = 0;
    for (const state in w) {
      const ww = w[state];
      if (!ww || actionFor(state)) continue; // states with a real clip don't need it
      const [l, tr, amp, spd, n] = PROCEDURAL[state] || PROCEDURAL.Idle;
      lean += l * ww; turn += tr * ww; bob += amp * Math.abs(Math.sin(t * spd)) * ww; nod += n * Math.sin(t * spd * 0.5) * ww; total += ww;
    }
    if (!total) { pivot.position.y = 0; pivot.rotation.set(0, 0, 0); pivot.scale.set(1, 1, 1); return; }
    pivot.rotation.set(lean + nod, turn * (opts.pointTurn ?? 1), 0);
    pivot.position.y = bob;
    const breathe = 1 + 0.006 * Math.sin(t * 2.4);
    pivot.scale.set(1 / Math.sqrt(breathe), breathe, 1 / Math.sqrt(breathe));
  }

  /* ---------- live (interactive) ---------- */
  let liveState = null, liveTime = 0, liveFrom = null, liveSince = 0;
  function play(state, fade = FADE) {
    const next = actionFor(state), prev = liveState && actionFor(liveState);
    if (next) {
      next.reset().setEffectiveWeight(1).play();
      if (prev && prev !== next) prev.crossFadeTo(next, fade, false);
      else next.fadeIn(fade);
    }
    liveFrom = liveState; liveState = state; liveSince = 0;
  }
  function update(delta) {
    liveTime += delta; liveSince += delta;
    mixer.update(delta);
    const f = clamp(liveSince / FADE, 0, 1), w = { [liveState || "Idle"]: f };
    if (liveFrom && f < 1) w[liveFrom] = (w[liveFrom] || 0) + 1 - f;
    applyProcedural(w, liveTime);
  }

  return { root, model, mixer, clips, actions, skinned, textured, setSchedule, evaluate, play, update, height: opts.height ?? 1 };
}

/*
 * Temporary colours for an untextured export, painted per vertex from the character sheet:
 * black side-part hair, skin, black tee, khaki chinos, navy sneakers. Remove once the GLB has textures.
 */
function paintPlaceholder(THREE, model, cfg) {
  const C = (hex) => new THREE.Color(hex);
  const col = { skin: C(0xa8704f), hair: C(0x121010), tee: C(0x1b1b1d), pants: C(0x9c8a6e), shoe: C(0x262b3d), sole: C(0x9d9993), eye: C(0x24140c), sclera: C(0xd9d2cb), brow: C(0x2a1d16) };
  model.traverse((o) => {
    if (!o.isMesh) return;
    const g = o.geometry, p = g.attributes.position, n = p.count;
    g.computeBoundingBox();
    const bb = g.boundingBox, H = bb.max.y - bb.min.y, W = bb.max.x - bb.min.x, D = bb.max.z - bb.min.z;
    const colors = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const x = (p.getX(i) - (bb.min.x + bb.max.x) / 2) / W; // -0.5..0.5 across the arm span
      const u = (p.getY(i) - bb.min.y) / H;                  // 0 feet .. 1 top of head
      const z = (p.getZ(i) - (bb.min.z + bb.max.z) / 2) / D; // -0.5 back .. 0.5 front
      const ax = Math.abs(x);
      let c;
      if (u < 0.018) c = col.sole;
      else if (u < 0.075) c = col.shoe;
      else if (u < cfg.hem && ax < cfg.legX) c = col.pants;
      else if (u < cfg.neck && (ax < cfg.torsoX || (u > cfg.sleeve && ax < cfg.sleeveX))) c = col.tee;
      else if (u < cfg.neck) c = col.skin; // arms and hands
      else if (u > (z > cfg.frontZ ? cfg.hairTopFront : cfg.hairTop) || (z < cfg.hairBackZ && u > cfg.hairBackU) || (ax > cfg.hairSideX && u > cfg.hairSideU)) c = col.hair;
      else if (z > cfg.eyeZ && ((u - cfg.eyeU) / (cfg.eyeH * 0.8)) ** 2 + ((ax - cfg.eyeX) / (cfg.eyeW * 0.42)) ** 2 < 1) c = col.eye;
      else if (z > cfg.eyeZ && ((u - cfg.eyeU) / cfg.eyeH) ** 2 + ((ax - cfg.eyeX) / cfg.eyeW) ** 2 < 1) c = col.sclera;
      else if (z > cfg.eyeZ - 0.04 && ((u - cfg.browU) / cfg.browH) ** 2 + ((ax - cfg.eyeX) / (cfg.eyeW * 1.5)) ** 2 < 1) c = col.brow;
      else c = col.skin;
      colors.set([c.r, c.g, c.b], i * 3);
    }
    g.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    o.material = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.78, metalness: 0, envMapIntensity: 0.45 });
  });
}

function clamp(x, a, b) { return Math.min(b, Math.max(a, x)); }
