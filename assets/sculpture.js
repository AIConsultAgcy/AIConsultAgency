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
      ring.position.set(mobile ? 0 : 2.2, mobile ? -1.85 : 0.05, 0);
      ring.scale.setScalar(mobile ? 0.52 : 0.96);
      ring.rotation.set(0.53 + smooth.y * 0.12, -0.63 + smooth.x * 0.17, -0.3 + phase);
      const spread = reduced.matches ? 0 : progress * 0.22;
      blades.forEach((b, i) => {
        const a = (i / blades.length) * Math.PI * 2;
        const r = 1.62 + spread * (0.6 + Math.sin(i * 2.3) * 0.35);
        b.position.set(Math.cos(a) * r, Math.sin(a) * r, Math.sin(a * 2 + 0.5) * 0.26 + spread * Math.cos(i * 1.4));
        b.rotation.set(0.35 + Math.sin(a) * 0.32, 0.8 + Math.sin(a * 2) * 0.4 + spread * 0.3, a + 0.38);
      });
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
    wake();
  }).observe(host);
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
