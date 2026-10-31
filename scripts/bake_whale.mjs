import { writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

// Bake the original renderer, rather than approximating its dive with SVG transforms.
// From the profile repo: node scripts/bake_whale.mjs /path/to/dsh-ascii-whales
// Then: python3 scripts/build_contrib.py. Daily refreshes reuse whale-motion.json.
const source = resolve(process.argv[2] || '../dsh-ascii-whales');
const revision = execFileSync('git', ['-C', source, 'rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
const { createScene, whalePose, projectParticle } = await import(pathToFileURL(resolve(source, 'src/model.js')));
const { divePose } = await import(pathToFileURL(resolve(source, 'src/motion.js')));
const { resetWhaleRig, updateWhaleRig } = await import(pathToFileURL(resolve(source, 'src/rig.js')));
const scene = createScene(1, '探索未至之境', 'blue', 1, 0);
const whale = scene.whales[0];
Object.assign(whale, { x: 414, y: 200, heading: 0, turn: 0, length: 560 });
resetWhaleRig(whale);
const timing = { entry: 3.6, under: 1.8, exit: 4.8 };
const project = time => {
  const dive = divePose(time - 9, timing);
  Object.assign(whale._motion, {
    wave: (time - 6) * 1.45, stroke: 0.65,
    submergence: dive.submergence, pitch: dive.pitch, noseFirst: dive.noseFirst,
    depth: dive.depth, tailKick: dive.tailKick, arch: dive.arch,
  });
  // Keep moving forward on the same bearing, including the invisible underwater phase.
  whale.x = 414 + 4.8 * (time - 6);
  updateWhaleRig(whale);
  const pose = whalePose(whale, 0, 900, 400, 1);
  return scene.particles.map(p => projectParticle(p, pose));
};
const rest = project(6);

// Intersect the renderer's visible triangles with a character lattice. Barycentric
// anchors stay attached to the same skin as the spine, fins and flukes deform.
function lattice(pitch) {
  const cells = new Map();
  for (let t = 0; t < scene.triangles.length; t += 3) {
    const ids = Array.from(scene.triangles.slice(t, t + 3));
    const [a, b, c] = ids.map(i => rest[i]);
    const d = (b.y - c.y) * (a.x - c.x) + (c.x - b.x) * (a.y - c.y);
    if (Math.abs(d) < 1e-5) continue;
    const left = Math.ceil(Math.min(a.x, b.x, c.x) / pitch);
    const right = Math.floor(Math.max(a.x, b.x, c.x) / pitch);
    const top = Math.ceil(Math.min(a.y, b.y, c.y) / pitch);
    const bottom = Math.floor(Math.max(a.y, b.y, c.y) / pitch);
    for (let row = top; row <= bottom; row++) for (let col = left; col <= right; col++) {
      const x = col * pitch, y = row * pitch;
      const u = ((b.y - c.y) * (x - c.x) + (c.x - b.x) * (y - c.y)) / d;
      const v = ((c.y - a.y) * (x - c.x) + (a.x - c.x) * (y - c.y)) / d;
      const weights = [u, v, 1 - u - v];
      if (Math.min(...weights) < -1e-6) continue;
      const visibility = weights.reduce((s, w, i) => s + w * rest[ids[i]].visibility, 0);
      if (visibility < 0.45) continue;
      const z = weights.reduce((s, w, i) => s + w * rest[ids[i]].z, 0);
      const key = `${col}:${row}`;
      if (!cells.has(key) || z < cells.get(key).z) cells.set(key, { ids, weights, x, y, z });
    }
  }
  return [...cells.values()];
}
let candidates;
let pitch = 12;
for (; pitch > 5; pitch -= 0.025) {
  candidates = lattice(pitch);
  if (candidates.length >= 371) break;
}
// Remove only a few excess samples, retaining the outer silhouette and fin tips.
while (candidates.length > 371) {
  let best = -1, score = Infinity;
  for (let i = 0; i < candidates.length; i++) {
    const p = candidates[i];
    const neighbors = candidates.reduce((n, q) => n + (Math.hypot(p.x - q.x, p.y - q.y) < pitch * 1.5 ? 1 : 0), 0);
    const rank = 10 - neighbors + (i * 0.61803398875 % 1);
    if (rank < score) { best = i; score = rank; }
  }
  candidates.splice(best, 1);
}
// Column-wise order keeps heatmap travel local, rather than a random particle cloud.
candidates.sort((a, b) => a.x - b.x || a.y - b.y);
const times = Array.from({ length: 151 }, (_, i) => 6 + i / 10);
const round = x => Math.round(x * 100) / 100;
const frames = times.map(time => {
  const projected = project(time);
  return candidates.map(({ ids, weights }) => {
    const blend = field => weights.reduce((s, w, i) => s + w * projected[ids[i]][field], 0);
    return [round(blend('x')), round(blend('y')), round(blend('visibility')), round(blend('light'))];
  });
});
const output = resolve('assets/whale-motion.json');
await writeFile(output, JSON.stringify({
  source: 'https://github.com/jryang1997/dsh-ascii-whales', revision,
  species: 'blue', timing, diveStart: 9, pitch: round(pitch), times, frames,
}));
console.log(`Baked ${frames.length} poses × ${candidates.length} skin anchors from ${revision} → ${output}`);
