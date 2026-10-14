// Hero sculpture: 38 rounded chrome blades assembled into one turning ring, three of them orange.
// Separate operations, one controlled workflow. Renders only while on screen; pauses on request.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const host = document.querySelector('.sculpture');
const toggle = document.querySelector('.motion-control');
if (host) start();

function start() {
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'low-power' }); } catch (e) { return; }
  let frame = 0, visible = true, mobile = false, phase = 0, last = 0, lastDraw = 0, progress = 0, paused = false;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = new THREE.Vector2(), smooth = new THREE.Vector2(), zero = new THREE.Vector2();
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 60);
  camera.position.set(0, 0, 10);
  renderer.setClearColor(0x080b10, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.85;
  renderer.domElement.setAttribute('aria-hidden', 'true');
  host.appendChild(renderer.domElement);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.055).texture;
  pmrem.dispose();

  const ring = new THREE.Group();
  scene.add(ring);
  const geometry = new RoundedBoxGeometry(1.65, 0.36, 1.24, 5, 0.17);
  const chrome = new THREE.MeshPhysicalMaterial({ color: 0x9aa7b4, metalness: 0.98, roughness: 0.16, clearcoat: 1, clearcoatRoughness: 0.15, envMapIntensity: 1.1 });
  const orange = new THREE.MeshPhysicalMaterial({ color: 0xff7547, metalness: 0.62, roughness: 0.22, clearcoat: 1, emissive: 0x5b1607, emissiveIntensity: 0.16 });
  const blades = [];
  for (let i = 0; i < 38; i++) { const m = new THREE.Mesh(geometry, i >= 27 && i <= 29 ? orange : chrome); blades.push(m); ring.add(m); }
  const key = new THREE.DirectionalLight(0xe9f1ff, 2); key.position.set(-2, 5, 6);
  const warm = new THREE.PointLight(0xff7547, 100, 15, 2); warm.position.set(2, -1, 3);
  const rim = new THREE.DirectionalLight(0x8ca8d2, 3); rim.position.set(-4, 1, -3);
  scene.add(key, warm, rim);

  function place(spread) {
    blades.forEach((b, i) => {
      const a = (i / blades.length) * Math.PI * 2;
      const r = 1.62 + spread * (0.6 + Math.sin(i * 2.3) * 0.35);
      b.position.set(Math.cos(a) * r, Math.sin(a) * r, Math.sin(a * 2 + 0.5) * 0.26 + spread * Math.cos(i * 1.4));
      b.rotation.set(0.35 + Math.sin(a) * 0.32, 0.8 + Math.sin(a * 2) * 0.4 + spread * 0.3, a + 0.38);
    });
  }

  // Fit the ring into the space to the right of the headline, so it never sits on the type at any width.
  // Measures the ring's on-screen box at scale 1 (corners of every blade, projected), then scales and places it.
  const headline = document.querySelector('.hero-content h1');
  const fit = { x: 2.2, y: 0.05, s: 0.96 };
  const corner = new THREE.Vector3();
  geometry.computeBoundingBox();
  function measure(x = 0, y = 0, sc = 1) {
    ring.position.set(x, y, 0); ring.scale.setScalar(sc); ring.rotation.set(0.53, -0.63, -0.3); place(0);
    ring.updateMatrixWorld(true);
    const bb = geometry.boundingBox; let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (const b of blades) for (let k = 0; k < 8; k++) {
      corner.set(k & 1 ? bb.max.x : bb.min.x, k & 2 ? bb.max.y : bb.min.y, k & 4 ? bb.max.z : bb.min.z).applyMatrix4(b.matrixWorld).project(camera);
      x0 = Math.min(x0, corner.x); x1 = Math.max(x1, corner.x); y0 = Math.min(y0, corner.y); y1 = Math.max(y1, corner.y);
    }
    return { x0, x1, y0, y1 };
  }
  function layout(width, height) {
    if (mobile) { fit.x = 0; fit.y = -1.85; fit.s = 0.52; return; }
    const m = measure(), margin = 1.06;                          // a little room for the slow turn and the pointer tilt
    const w1 = (m.x1 - m.x0) / 2 * width * margin, h1 = (m.y1 - m.y0) / 2 * height * margin;
    const host_ = host.getBoundingClientRect();
    let textRight = width * 0.5;
    if (headline) { const rg = document.createRange(); rg.selectNodeContents(headline); textRight = rg.getBoundingClientRect().right - host_.left; }
    const left = textRight + Math.max(32, width * 0.025), right = width * 0.985;
    const s = Math.min((right - left) / w1, height * 0.74 / h1, 1.15);
    const cx = (left + right) / 2, cy = height * 0.47;
    const halfH = Math.tan(camera.fov * Math.PI / 360) * camera.position.z, halfW = halfH * camera.aspect;
    // the measured box is not centred on the ring origin; shift by its centre at the chosen scale
    const bx = (m.x0 + m.x1) / 2 * halfW * s, by = (m.y0 + m.y1) / 2 * halfH * s;
    fit.s = Math.max(s, 0.45);
    fit.x = (cx / width * 2 - 1) * halfW - bx;
    fit.y = (1 - cy / height * 2) * halfH - by;
    // perspective skews the estimate off-centre: measure where it actually lands and correct, twice
    for (let k = 0; k < 2; k++) {
      const a = measure(fit.x, fit.y, fit.s);
      const pw = (a.x1 - a.x0) / 2 * width * margin, ph = (a.y1 - a.y0) / 2 * height * margin;
      const g = Math.min(1, (right - left) / pw, height * 0.74 / ph);
      fit.s *= g;
      const ax = ((a.x0 + a.x1) / 2 + 1) / 2 * width, ay = (1 - (a.y0 + a.y1) / 2) / 2 * height;
      fit.x += (cx - ax) / width * 2 * halfW;
      fit.y -= (cy - ay) / height * 2 * halfH;
    }
  }

  function render(now) {
    frame = 0;
    if (!visible || (document.hidden && lastDraw)) return; // always paint the first frame, even in a background tab
    const moving = !paused && !reduced.matches;
    const delta = last ? Math.min((now - last) / 1000, 0.05) : 0;
    last = now;
    if (moving) phase += delta * 0.075;
    if (!moving || now - lastDraw >= (mobile ? 1000 / 30 : 1000 / 45)) {
      lastDraw = now;
      smooth.lerp(moving ? pointer : zero, 0.045);
      ring.position.set(fit.x, fit.y, 0);
      ring.scale.setScalar(fit.s);
      ring.rotation.set(0.53 + smooth.y * 0.12, -0.63 + smooth.x * 0.17, -0.3 + phase);
      place(reduced.matches ? 0 : progress * 0.22);
      renderer.render(scene, camera);
    }
    if (moving) frame = requestAnimationFrame(render);
  }
  function wake() { if (frame || !visible || (document.hidden && lastDraw)) return; last = 0; if (document.hidden) { render(performance.now()); return; } frame = requestAnimationFrame(render); }

  new ResizeObserver(() => {
    const { width, height } = host.getBoundingClientRect();
    if (!width || !height) return;
    mobile = width < 760;
    camera.aspect = width / height;
    camera.fov = mobile ? 47 : 38;
    camera.updateProjectionMatrix();
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, mobile ? 1 : 1.5));
    renderer.setSize(width, height, false);
    layout(width, height);
    wake();
  }).observe(host);
  if (document.fonts) document.fonts.ready.then(() => { const r = host.getBoundingClientRect(); if (r.width && r.height) { layout(r.width, r.height); lastDraw = 0; wake(); } });
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (!visible) { cancelAnimationFrame(frame); frame = 0; } else wake(); }, { threshold: 0.01 }).observe(host);
  addEventListener('pointermove', (e) => {
    if (e.pointerType === 'touch' || reduced.matches || paused) return;
    const r = host.getBoundingClientRect();
    pointer.set(THREE.MathUtils.clamp((e.clientX - r.left) / r.width * 2 - 1, -1, 1), THREE.MathUtils.clamp((e.clientY - r.top) / r.height * 2 - 1, -1, 1));
  }, { passive: true });
  addEventListener('scroll', () => {
    const r = host.getBoundingClientRect();
    progress = THREE.MathUtils.clamp(-r.top / Math.max(r.height, 1), 0, 1);
    if (!paused && !reduced.matches) wake();
  }, { passive: true });
  document.addEventListener('visibilitychange', () => { if (document.hidden) { cancelAnimationFrame(frame); frame = 0; } else wake(); });
  reduced.addEventListener('change', wake);
  renderer.domElement.addEventListener('webglcontextlost', (e) => { e.preventDefault(); cancelAnimationFrame(frame); frame = 0; visible = false; host.classList.remove('ready'); });
  if (toggle) toggle.addEventListener('click', () => {
    paused = !paused;
    toggle.setAttribute('aria-pressed', String(paused));
    toggle.setAttribute('aria-label', paused ? 'Play sculpture animation' : 'Pause sculpture animation');
    toggle.querySelector('.ico-pause').hidden = paused;
    toggle.querySelector('.ico-play').hidden = !paused;
    toggle.querySelector('.lbl').textContent = paused ? 'Motion off' : 'Motion on';
    wake();
  });
  host.classList.add('ready');
  wake();
}
