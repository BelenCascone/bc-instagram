import * as THREE from './lib/three.module.js';

const W = 1080, H = 1920, DUR = 47.0;
const SUN = new THREE.Vector3(0.18, 0.075, -1).normalize();
const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ss = (a, b, x) => { const t = cl((x - a) / (b - a)); return t * t * (3 - 2 * t); };
const lerp = (a, b, p) => a + (b - a) * p;

// ---------- renderer ----------
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(48, W / H, 0.1, 4000);

// ---------- shared sky function (GLSL) ----------
const SKY_GLSL = `
uniform vec3 sunDir;
vec3 skyCol(vec3 d){
  float e = clamp(d.y, -0.2, 1.0);
  vec3 horizon = vec3(1.00, 0.80, 0.58);   // warm peach
  vec3 low     = vec3(0.93, 0.62, 0.55);   // rose
  vec3 band    = vec3(0.47, 0.36, 0.62);   // violet
  vec3 zenith  = vec3(0.07, 0.20, 0.17);   // BC forest green, deep
  vec3 c = mix(horizon, low, smoothstep(0.0, 0.06, e));
  c = mix(c, band, smoothstep(0.05, 0.22, e));
  c = mix(c, zenith, smoothstep(0.20, 0.75, e));
  float s = max(dot(normalize(d), sunDir), 0.0);
  c += vec3(1.0, 0.86, 0.55) * pow(s, 18.0) * 0.55;          // halo
  c += vec3(0.85, 1.0, 0.55) * pow(s, 260.0) * 0.6;          // lime-gold core glow
  c = mix(c, vec3(1.0, 0.98, 0.88) * 2.4, smoothstep(0.99935, 0.99965, s)); // sun disc
  return c;
}`;

// ---------- sky dome ----------
const sky = new THREE.Mesh(new THREE.SphereGeometry(3000, 48, 24), new THREE.ShaderMaterial({
  side: THREE.BackSide, depthWrite: false, uniforms: { sunDir: { value: SUN } },
  vertexShader: `varying vec3 vD; void main(){ vD = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: SKY_GLSL + `varying vec3 vD; void main(){ gl_FragColor = vec4(skyCol(vD),1.0); }`
}));
scene.add(sky);

// ---------- sea ----------
const seaMat = new THREE.ShaderMaterial({
  uniforms: { sunDir: { value: SUN }, uTime: { value: 0 }, camPos: { value: new THREE.Vector3() } },
  vertexShader: `varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position,1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: SKY_GLSL + `
  uniform float uTime; uniform vec3 camPos; varying vec3 vW;
  float hgt(vec2 p){
    float t = uTime;
    float h = 0.0;
    h += sin(dot(p, vec2(0.08, 0.05)) + t*0.9) * 0.35;
    h += sin(dot(p, vec2(-0.13, 0.11)) + t*1.3) * 0.22;
    h += sin(dot(p, vec2(0.31, -0.21)) + t*2.1) * 0.08;
    h += sin(dot(p, vec2(-0.57, 0.43)) + t*2.9) * 0.045;
    h += sin(dot(p, vec2(1.13, 0.87)) + t*4.0) * 0.02;
    return h;
  }
  void main(){
    vec2 p = vW.xz; float e = 0.15;
    vec3 n = normalize(vec3(hgt(p-vec2(e,0.))-hgt(p+vec2(e,0.)), 2.0*e*1.0, hgt(p-vec2(0.,e))-hgt(p+vec2(0.,e))));
    vec3 v = normalize(vW - camPos);
    float dist = length(vW.xz - camPos.xz);
    n = normalize(mix(n, vec3(0.,1.,0.), smoothstep(80.0, 900.0, dist)));
    vec3 r = reflect(v, n); r.y = abs(r.y);
    float fres = 0.04 + 0.96 * pow(1.0 - max(dot(-v, n), 0.0), 5.0);
    vec3 deep = vec3(0.03, 0.11, 0.10);
    vec3 col = mix(deep, skyCol(r), fres);
    float g = max(dot(r, sunDir), 0.0);
    col += vec3(1.0, 0.85, 0.55) * (pow(g, 900.0) * 6.0 + pow(g, 90.0) * 0.5);
    vec3 hz = skyCol(normalize(vec3(v.x, 0.004, v.z)));
    col = mix(col, hz, smoothstep(250.0, 1800.0, dist));
    gl_FragColor = vec4(col, 1.0);
  }`
});
const sea = new THREE.Mesh(new THREE.PlaneGeometry(5200, 5200, 1, 1), seaMat);
sea.rotation.x = -Math.PI / 2; scene.add(sea);

// ---------- clouds (sprites, purple cumulus) ----------
function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
function cloudTex(seed) {
  const r = rng(seed), c = document.createElement('canvas'); c.width = 512; c.height = 320; const g = c.getContext('2d');
  for (let k = 0; k < 46; k++) {
    const x = 80 + r() * 352, base = 250, y = base - Math.pow(r(), 0.8) * 150 * (1 - Math.abs(x - 256) / 300), rad = 30 + r() * 62;
    const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, 'rgba(255,255,255,0.95)'); gr.addColorStop(0.65, 'rgba(255,255,255,0.7)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.beginPath(); g.arc(x, y, rad, 0, 7); g.fill();
  }
  g.globalCompositeOperation = 'destination-out'; const cut = g.createLinearGradient(0, 240, 0, 300); cut.addColorStop(0, 'rgba(0,0,0,0)'); cut.addColorStop(1, 'rgba(0,0,0,1)'); g.fillStyle = cut; g.fillRect(0, 240, 512, 80);
  g.globalCompositeOperation = 'source-atop';
  const sh = g.createLinearGradient(0, 40, 0, 290);
  sh.addColorStop(0, '#ffe6c4'); sh.addColorStop(0.35, '#f2b8a8'); sh.addColorStop(0.7, '#8d6aa8'); sh.addColorStop(1, '#4e3d6e');
  g.fillStyle = sh; g.fillRect(0, 0, 512, 320);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const CT = [1, 2, 3, 4, 5].map(cloudTex);
const clouds = [];
{
  const r = rng(77);
  for (let k = 0; k < 70; k++) {
    const far = k < 18;
    const z = far ? -1500 - r() * 600 : 60 - r() * 900;
    const x = far ? (r() - 0.5) * 2400 : (r() < 0.5 ? -1 : 1) * (25 + r() * 220);
    const s = far ? 280 + r() * 380 : 40 + r() * 120;
    const y = far ? 40 + r() * 120 : 18 + r() * 70;
    const m = new THREE.SpriteMaterial({ map: CT[k % 5], transparent: true, depthWrite: false, fog: false, opacity: far ? 0.95 : 0.92 });
    const sp = new THREE.Sprite(m); sp.scale.set(s, s * 0.625, 1); sp.position.set(x, y, z); scene.add(sp); clouds.push(sp);
  }
}

// ---------- paper plane made of punched tape ----------
function paperTex() {
  const c = document.createElement('canvas'); c.width = 512; c.height = 512; const g = c.getContext('2d');
  g.fillStyle = '#fbf8e6'; g.fillRect(0, 0, 512, 512);
  g.fillStyle = 'rgba(120,110,80,0.06)'; for (let i = 0; i < 3000; i++) g.fillRect(Math.random() * 512, Math.random() * 512, 2, 2);
  g.fillStyle = '#c6ff00'; g.fillRect(0, 236, 512, 40);
  const r = rng(9); g.fillStyle = '#1b4332';
  for (let row = 0; row < 7; row++) for (let col = 0; col < 18; col++) if (r() > 0.42 && row !== 3) { g.beginPath(); g.arc(18 + col * 27, 60 + row * 62, 7, 0, 7); g.fill(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const PT = paperTex();
const planeGeo = new THREE.BufferGeometry();
{ // classic dart: nose at -z
  const v = [
    0, 0, -2.2, -1.25, 0.18, 1.1, 0, 0, 1.0,     // left wing
    0, 0, -2.2, 0, 0, 1.0, 1.25, 0.18, 1.1,      // right wing
    0, 0, -2.2, 0, 0, 1.0, 0, -0.42, 0.95,       // keel left
    0, 0, -2.2, 0, -0.42, 0.95, 0, 0, 1.0,       // keel right
  ];
  const uv = [0.5, 0, 0, 1, 0.5, 1, 0.5, 0, 0.5, 1, 1, 1, 0.5, 0, 0.5, 1, 0.3, 1, 0.5, 0, 0.3, 1, 0.5, 1];
  planeGeo.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
  planeGeo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
  planeGeo.computeVertexNormals();
}
const plane = new THREE.Mesh(planeGeo, new THREE.MeshStandardMaterial({ map: PT, side: THREE.DoubleSide, roughness: 0.85, metalness: 0 }));
plane.scale.setScalar(1.3); scene.add(plane);
const sunLight = new THREE.DirectionalLight(0xffd7a0, 3.2); scene.add(sunLight); scene.add(sunLight.target);
const fill = new THREE.HemisphereLight(0x9a86c8, 0x123a30, 1.1); scene.add(fill);

// ---------- trailing punched tape ribbon ----------
const RS = 90;
function tapeTex() {
  const c = document.createElement('canvas'); c.width = 64; c.height = 1024; const g = c.getContext('2d');
  g.fillStyle = '#fbf8e6'; g.fillRect(0, 0, 64, 1024); g.fillStyle = '#1b4332'; const r = rng(31);
  for (let y = 10; y < 1024; y += 22) for (let x = 0; x < 5; x++) if (r() > 0.45) { g.beginPath(); g.arc(8 + x * 12, y, 3.6, 0, 7); g.fill(); }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapT = THREE.RepeatWrapping; return t;
}
const ribbonGeo = new THREE.BufferGeometry();
ribbonGeo.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(RS * 2 * 3), 3));
{ const uv = [], idx = []; for (let i = 0; i < RS; i++) { uv.push(0, i / RS * 4, 1, i / RS * 4); if (i < RS - 1) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
  ribbonGeo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); ribbonGeo.setIndex(idx); }
const ribbonMat = new THREE.MeshStandardMaterial({ map: tapeTex(), side: THREE.DoubleSide, roughness: 0.9, transparent: true, opacity: 0 });
const ribbon = new THREE.Mesh(ribbonGeo, ribbonMat); ribbon.frustumCulled = false; scene.add(ribbon);

// ---------- flight path ----------
const SPEED = 14;
function pos(t) {
  const climb = 6 * ss(10.0, 13.8, t) - 3.5 * ss(16, 21, t) + 4 * ss(36.5, 44, t);
  return new THREE.Vector3(Math.sin(t * 0.33) * 7 + Math.sin(t * 0.9 + 1) * 1.6, 7 + Math.sin(t * 0.55) * 1.3 + climb, -t * SPEED);
}
function frameAt(t) {
  const p = pos(t), f = pos(t + 0.05).sub(p).normalize();
  const lat = (pos(t + 0.3).x - 2 * p.x + pos(t - 0.3).x);
  return { p, f, roll: -lat * 1.4 };
}

// ---------- camera beats (relative to the plane: right, up, back, plus look lead) ----------
const BEATS = [
  [0.0, [-14, -4.5, -26], 0],    // low wide, plane passes towards the sun
  [4.6, [6.5, 1.0, 9], 0],       // side chase, close
  [10.1, [-3, -6, 7], 0],        // looking up as it climbs
  [13.8, [11, 2.5, -3], 0],      // orbit start
  [19.0, [-10, 3, 6], 0],        // orbit other side
  [22.5, [4, 16, 24], 0],        // high wide over the sea
  [27.2, [3.2, 2.4, 8.5], 0],    // chase behind with the tape
  [34.1, [-3.4, 1.2, 5], 0],        // close, faster
  [36.5, [-2, 3.5, 30], 0],      // pull back towards the sun
];
function camOffset(t) {
  let i = 0; while (i < BEATS.length - 1 && t >= BEATS[i + 1][0]) i++;
  const cur = BEATS[i], prev = BEATS[Math.max(0, i - 1)];
  const k = i === 0 ? 1 : ss(cur[0], cur[0] + 1.6, t);
  const o = cur[1].map((v, j) => lerp(prev[1][j], v, k));
  return o;
}

// ---------- UI overlay ----------
const ui = document.getElementById('ui').getContext('2d');
let SUBS = []; const logo = new Image(); logo.src = 'logo_negro.png';
const eo = x => { x = cl(x); return 1 - Math.pow(1 - x, 3); };
function fade(t, a, b, f = 0.45) { return eo((t - a) / f) * (1 - eo((t - (b - f)) / f)); }
function txt(s, x, y, font, color, alpha, { align = 'center', shadow = true, ls = 0 } = {}) {
  if (alpha <= 0.003) return; ui.save(); ui.globalAlpha = alpha; ui.font = font; ui.textAlign = align; ui.textBaseline = 'alphabetic';
  if (ls) ui.letterSpacing = ls + 'px';
  if (shadow) { ui.shadowColor = 'rgba(20,10,30,.45)'; ui.shadowBlur = 24; ui.shadowOffsetY = 3; }
  ui.fillStyle = color; ui.fillText(s, x, y); ui.restore();
}
const CARDS = [
  // [start, end, lines: [text, size, style, color]]
  [0.2, 4.6, [['¿empezar', 110, 'italic 600', '#FBF8E6'], ['a los 31?', 150, 'italic 600', '#C6FF00']]],
  [4.8, 10.1, [['Cecilia', 140, 'italic 600', '#FBF8E6'], ['Berdichevsky', 104, 'italic 600', '#FBF8E6'], ['contadora · 10 años', 46, 'normal 600', 'rgba(251,248,230,.8)', 'In']]],
  [10.2, 13.8, [['a los 31:', 96, 'italic 400', '#FBF8E6'], ['Matemática, UBA', 92, 'italic 600', '#C6FF00']]],
  [13.9, 19.05, [['1961', 190, 'normal 600', '#FBF8E6'], ['llega Clementina', 84, 'italic 600', '#C6FF00']]],
  [19.1, 22.5, [['primera fila', 120, 'italic 600', '#FBF8E6']]],
  [22.5, 27.1, [['su profe trabajó', 80, 'italic 400', '#FBF8E6'], ['con Alan Turing', 96, 'italic 600', '#C6FF00']]],
  [27.3, 31.7, [['su primer', 96, 'italic 400', '#FBF8E6'], ['programa', 140, 'italic 600', '#C6FF00']]],
  [31.75, 36.45, [['días', 150, 'italic 600', '#FBF8E6'], ['→ segundos', 120, 'italic 600', '#C6FF00']]],
  [36.55, 43.75, [['nunca es tarde', 104, 'italic 600', '#FBF8E6'], ['para despegar', 112, 'italic 600', '#C6FF00']]],
];
function drawUI(t) {
  ui.clearRect(0, 0, W, H);
  // soft top/bottom vignette for legibility
  let g = ui.createLinearGradient(0, 0, 0, 760); g.addColorStop(0, 'rgba(10,22,18,.55)'); g.addColorStop(1, 'rgba(10,22,18,0)'); ui.fillStyle = g; ui.fillRect(0, 0, W, 760);
  g = ui.createLinearGradient(0, 1500, 0, H); g.addColorStop(0, 'rgba(10,22,18,0)'); g.addColorStop(1, 'rgba(10,22,18,.55)'); ui.fillStyle = g; ui.fillRect(0, 1500, W, 420);
  for (const [a, b, lines] of CARDS) {
    const al = fade(t, a, b, 0.5); if (al <= 0) continue;
    let y = 300; const rise = (1 - eo((t - a) / 0.8)) * 26;
    lines.forEach((ln, i) => {
      const [s, size, style, col, fam] = ln; const li = fade(t, a + i * 0.25, b, 0.5);
      txt(s, 540, y + size * 0.8 + rise, `${style} ${size}px ${fam || 'Fr'}`, col, li);
      y += size * (fam ? 1.5 : 1.05);
    });
  }
  // subtitles
  const c = SUBS.find(s => t >= s.s - 0.05 && t <= s.e + 0.35);
  if (c && t < 43.8) {
    ui.save(); ui.font = '500 40px In'; const words = c.t.split(' '); const lines = []; let ln = '';
    words.forEach(w => { const tt = ln ? ln + ' ' + w : w; if (ui.measureText(tt).width > 900 && ln) { lines.push(ln); ln = w; } else ln = tt; }); lines.push(ln);
    const a = fade(t, c.s - 0.05, c.e + 0.35, 0.15);
    lines.forEach((l, i) => txt(l, 540, 1690 + i * 54 - (lines.length - 1) * 27, '500 40px In', '#FBF8E6', a));
    ui.restore();
  }
  // end card
  if (t > 43.4) {
    const a = eo((t - 43.4) / 0.8);
    ui.save(); ui.globalAlpha = a * 0.82; ui.fillStyle = '#121412'; ui.fillRect(0, 0, W, H); ui.restore();
    if (logo.complete) { ui.save(); ui.globalAlpha = eo((t - 43.7) / 0.6); const lw = 520, lh = lw * logo.height / logo.width; ui.drawImage(logo, 540 - lw / 2, 640 - lh / 2, lw, lh); ui.restore(); }
    txt('nunca es tarde', 540, 930, 'italic 600 92px Fr', '#FBF8E6', eo((t - 44.0) / 0.5), { shadow: false });
    txt('para despegar', 540, 1040, 'italic 600 100px Fr', '#C6FF00', eo((t - 44.2) / 0.5), { shadow: false });
    txt('Clases de tecnología e IA · Escribinos', 540, 1170, '500 42px In', 'rgba(251,248,230,.85)', eo((t - 44.6) / 0.5), { shadow: false });
    txt('@bc.informatica.pna', 540, 1250, '600 40px In', '#C6FF00', eo((t - 44.8) / 0.5), { shadow: false });
  }
}

// ---------- seek ----------
const tmp = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
function seek(t) {
  const fr = frameAt(t);
  plane.position.copy(fr.p);
  const m = new THREE.Matrix4().lookAt(new THREE.Vector3(0, 0, 0), fr.f, up); // object -z faces f
  plane.quaternion.setFromRotationMatrix(m);
  plane.rotateZ(fr.roll + Math.sin(t * 3.1) * 0.04);
  plane.rotateX(Math.sin(t * 2.3) * 0.03);
  // camera (Ghibli-style: offset in plane's yaw frame, gentle drift)
  const o = camOffset(t);
  const right = new THREE.Vector3().crossVectors(fr.f, up).normalize();
  const back = fr.f.clone().multiplyScalar(-1);
  const cp = fr.p.clone().addScaledVector(right, o[0]).addScaledVector(up, o[1]).addScaledVector(back, o[2]);
  cp.x += Math.sin(t * 0.37) * 0.6; cp.y += Math.sin(t * 0.51) * 0.4;
  cp.y = Math.max(cp.y, 1.2);
  camera.position.copy(cp);
  const look = fr.p.clone().addScaledVector(fr.f, 3).add(new THREE.Vector3(0, t < 4.6 ? 4 : 0.6, 0));
  camera.lookAt(look);
  camera.rotateZ(Math.sin(t * 0.29) * 0.025);
  sky.position.copy(cp);
  sea.position.set(cp.x, 0, cp.z);
  seaMat.uniforms.uTime.value = t; seaMat.uniforms.camPos.value.copy(cp);
  sunLight.position.copy(fr.p).addScaledVector(SUN, 50); sunLight.target.position.copy(fr.p);
  // ribbon (tape trailing behind the plane)
  ribbonMat.opacity = ss(26.6, 27.8, t) * (1 - ss(36.8, 38.5, t));
  const arr = ribbonGeo.attributes.position.array;
  for (let i = 0; i < RS; i++) {
    const tt = t - 0.15 - i * 0.022, f2 = frameAt(tt), q = f2.p.clone().addScaledVector(f2.f, -1.4);
    const r2 = new THREE.Vector3().crossVectors(f2.f, up).normalize();
    q.y += Math.sin(i * 0.35 - t * 9) * 0.12 * (i / RS) - i * 0.006;
    const w = 0.17, tw = Math.sin(i * 0.2 - t * 6) * 0.6;
    const side = r2.clone().multiplyScalar(Math.cos(tw) * w).add(new THREE.Vector3(0, Math.sin(tw) * w, 0));
    arr.set([q.x - side.x, q.y - side.y, q.z - side.z, q.x + side.x, q.y + side.y, q.z + side.z], i * 6);
  }
  ribbonGeo.attributes.position.needsUpdate = true; ribbonGeo.computeVertexNormals();
  renderer.render(scene, camera);
  drawUI(t);
}
window.seek = seek;
window.ready = fetch('subs.json').then(r => r.json()).then(j => { SUBS = j; return Promise.all(['italic 600 40px Fr', 'italic 400 40px Fr', 'normal 600 40px Fr', '500 40px In', '600 40px In'].map(f => document.fonts.load(f))); })
  .then(() => new Promise(r => { if (logo.complete) r(); else { logo.onload = r; logo.onerror = r; } })).then(() => { seek(0); return true; });
