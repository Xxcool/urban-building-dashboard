<script setup>
// 独立区域LOD场景：示意路网与建筑，不新增真实地理数据或经营统计。
import { onMounted, onBeforeUnmount, ref, watch, computed, nextTick } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { toThree, area, number, occupancy } from '../data/state.js';
import Icon from '../components/Icon.vue';
import SceneLoading from '../components/SceneLoading.vue';
import { readSceneBytes } from './load-asset.js';
import { createDaylightSky } from './daylight-environment.js';
import { measureFloatingCard } from '../utils/floating-card.js';
import { entranceFrame } from './entrance.js';

const props = defineProps(['config', 'active', 'resetTick', 'tour', 'replayTick', 'data']);
const emit = defineEmits(['enter', 'stats', 'status', 'entrance', 'interrupt']);

const cardPosition = ref(null),
  selectedPoi = ref(null),
  selectedInfo = computed(() => spec.poi.find((p) => p.id === selectedPoi.value));
// 阶段对应真实资源、空间构建与首帧准备，字节总量来自当前模型清单。
const loadingPhase = ref('resources');
const downloadedBytes = ref(0);
const totalBytes = ref(0);
const host = ref(null),
  labelHost = ref(null),
  status = ref('正在载入区域场景'),
  failure = ref(false);
let renderer,
  scene,
  camera,
  controls,
  model,
  composer,
  bloomComposer,
  bloomPass,
  mixPass,
  aoPass,
  pmrem,
  environment,
  sky,
  waterNormal,
  frame,
  observer,
  disposed = false,
  lastTime = 0,
  lastStats = 0,
  frames = 0,
  pointerStart;
const controller = new AbortController(),
  labels = new Map(),
  anchors = new Map(),
  samples = [],
  ray = new THREE.Raycaster(),
  pointer = new THREE.Vector2();
const spec = props.config.production.city,
  motion = props.config.design.motion.cityEntrance;
const reduced = matchMedia('(prefers-reduced-motion: reduce)'),
  revealUniform = { value: 1 },
  materialUniform = { value: 1 },
  parkUniform = { value: 1 },
  boundaryUniform = { value: 1 };
let playing = false,
  returning = false,
  elapsed = 0,
  pulseRing,
  frameState = entranceFrame(motion.duration, motion),
  ready = false,
  aoBlend = 0,
  poiRing,
  poiDisc,
  cameraMove = null;
let entryFrame = null,
  entryStart = null;
const cameraSnapshot = () => ({
  eye: camera.position.toArray(),
  target: controls.target.toArray(),
  fov: camera.fov,
});
function beginCampusEntry() {
  if (!ready) return null;
  finishEntrance();
  closePoi();
  controls.autoRotate = false;
  controls.enableDamping = false;
  controls.update();
  controls.enabled = false;
  entryStart = cameraSnapshot();
  entryFrame = { otherLabels: 1, parkLabel: 1, pulse: 0 };
  return entryStart;
}
function applyCampusEntry(pose, frame) {
  if (!ready) return;
  entryFrame = frame;
  camera.position.fromArray(pose.eye);
  controls.target.fromArray(pose.target);
  camera.fov = pose.fov;
  camera.lookAt(controls.target);
  camera.updateProjectionMatrix();
  camera.updateMatrixWorld(true);
  host.value.dataset.entryProjection = JSON.stringify(
    new THREE.Vector3(...toThree(spec.campusPositionM)).project(camera).toArray(),
  );
  if (pulseRing) {
    pulseRing.visible = frame.pulse > 0.001;
    pulseRing.scale.setScalar(1 + (1 - frame.pulse) * 0.35);
    pulseRing.material.opacity = frame.pulse * 0.55;
  }
}
function finishCampusEntry({ restore = false } = {}) {
  if (!ready) return;
  if (restore && entryStart) {
    camera.position.fromArray(entryStart.eye);
    controls.target.fromArray(entryStart.target);
    camera.fov = entryStart.fov;
    camera.updateProjectionMatrix();
  }
  entryFrame = null;
  entryStart = null;
  if (pulseRing) pulseRing.visible = false;
  controls.enabled = true;
  controls.enableDamping = true;
  lastTime = 0;
}
defineExpose({ beginCampusEntry, applyCampusEntry, finishCampusEntry });
function applyEntrance(driveCamera = false) {
  frameState = entranceFrame(elapsed, motion, { reduced: reduced.matches, returning });
  revealUniform.value = frameState.city;
  materialUniform.value = frameState.material;
  parkUniform.value = frameState.park;
  boundaryUniform.value = frameState.boundary;
  if (driveCamera && !returning) {
    const target = new THREE.Vector3(...toThree(spec.camera.target)),
      eye = new THREE.Vector3(...toThree(spec.camera.eye));
    camera.position
      .copy(target)
      .lerp(eye, THREE.MathUtils.lerp(motion.cameraDistanceFactor, 1, frameState.camera));
    controls.target.copy(target);
  }
  if (pulseRing) {
    const t = frameState.pulse;
    pulseRing.visible = t > 0 && t < 1 && !frameState.done;
    pulseRing.scale.setScalar(1 + t * 2.5);
    pulseRing.material.opacity = (1 - t) * 0.45;
  }
  emit('entrance', { panel: frameState.panel, done: frameState.done });
  if (host.value) {
    host.value.dataset.entrancePhase = frameState.done
      ? 'complete'
      : returning
        ? 'return'
        : elapsed < motion.boundaryReveal[0]
          ? 'city'
          : elapsed < motion.parkReveal[0]
            ? 'boundary'
            : 'park';
    host.value.dataset.entrance = JSON.stringify({
      playing,
      returning,
      elapsed: +elapsed.toFixed(3),
      ...frameState,
      cameraProgress: frameState.camera,
      camera: camera?.position.toArray(),
    });
  }
}
function finishEntrance() {
  if (!ready) return;
  playing = false;
  elapsed = motion.duration;
  returning = false;
  applyEntrance();
  controls.enableDamping = true;
  lastTime = 0;
}
function startEntrance(isReturn = false) {
  if (!ready) return;
  returning = isReturn;
  elapsed = 0;
  playing = !reduced.matches;
  lastTime = 0;
  if (!isReturn) reset();
  controls.enableDamping = !playing;
  applyEntrance(playing);
  if (reduced.matches) finishEntrance();
}
const reduceChanged = () => {
  if (reduced.matches) finishEntrance();
};
const interrupt = () => {
  if (entryFrame) emit('interrupt');
  cameraMove = null;
  finishEntrance();
};
const report = (message, error = false) => {
  status.value = message;
  failure.value = error;
  emit('status', { message, error });
};
function dispose(root) {
  const gs = new Set(),
    ms = new Set(),
    ts = new Set();
  root?.traverse((obj) => {
    if (obj.geometry) gs.add(obj.geometry);
    for (const m of obj.material
      ? Array.isArray(obj.material)
        ? obj.material
        : [obj.material]
      : []) {
      ms.add(m);
      Object.values(m).forEach((v) => {
        if (v?.isTexture) ts.add(v);
      });
    }
  });
  gs.forEach((g) => g.dispose());
  ms.forEach((m) => m.dispose());
  ts.forEach((t) => t.dispose());
}
let lastCardLayout = 0;
function placePoiCard(time) {
  if (!selectedPoi.value || time - lastCardLayout < 90) return;
  lastCardLayout = time;
  const card = host.value.querySelector('.city-info-card'),
    label = labels.get(selectedPoi.value);
  const previous = cardPosition.value?.owner === selectedPoi.value ? cardPosition.value : null;
  const position = measureFloatingCard(host.value, card, label, previous);
  if (position) cardPosition.value = { ...position, owner: selectedPoi.value };
}
function closePoi() {
  selectedPoi.value = null;
  cardPosition.value = null;
  cameraMove = null;
  if (poiRing) poiRing.visible = false;
  if (poiDisc) poiDisc.visible = false;
  labels.forEach((node) => node.classList.remove('selected'));
}
const escapePoi = (e) => {
  if (e.key === 'Escape' && selectedPoi.value) {
    e.preventDefault();
    e.stopImmediatePropagation();
    closePoi();
  }
};
function selectPoi(item) {
  finishEntrance();
  selectedPoi.value = item.id;
  cardPosition.value = null;
  lastCardLayout = 0;
  labels.forEach((node, id) => node.classList.toggle('selected', id === item.id));
  const center = new THREE.Vector3(...toThree([item.position[0], item.position[1], 6]));
  poiRing.position.copy(center);
  poiDisc.position.copy(center);
  poiRing.visible = true;
  poiDisc.visible = true;
  // 小幅平移保持区域上下文；镜头位置不由标签高度推断，交互打断后立即交还控制。
  const delta = center.clone().sub(controls.target);
  delta.y = 0;
  delta.clampLength(0, 260);
  cameraMove = {
    fromEye: camera.position.clone(),
    fromTarget: controls.target.clone(),
    delta,
    t: 0,
  };
}
function reset() {
  if (!camera) return;
  closePoi();
  const damping = controls.enableDamping;
  controls.autoRotate = false;
  controls.enableDamping = false;
  controls.update();
  camera.position.set(...toThree(spec.camera.eye));
  controls.target.set(...toThree(spec.camera.target));
  controls.update();
  controls.enableDamping = damping;
}
function resize() {
  if (!renderer || !host.value?.clientWidth || !props.active) return;
  const w = host.value.clientWidth,
    h = host.value.clientHeight,
    scale = host.value.getBoundingClientRect().width / w;
  renderer.setPixelRatio(
    Math.max(0.65, Math.min(devicePixelRatio, spec.render.pixelRatioCap) * scale),
  );
  renderer.setSize(w, h, false);
  composer?.setPixelRatio(renderer.getPixelRatio());
  composer?.setSize(w, h);
  bloomComposer?.setPixelRatio(renderer.getPixelRatio());
  bloomComposer?.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
const visibility = () => {
  lastTime = 0;
};
const down = (e) => {
  if (entryFrame) emit('interrupt');
  cameraMove = null;
  finishEntrance();
  pointerStart = [e.clientX, e.clientY];
};
function up(e) {
  if (!pointerStart || Math.hypot(e.clientX - pointerStart[0], e.clientY - pointerStart[1]) > 5)
    return;
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.set(
    ((e.clientX - rect.left) / rect.width) * 2 - 1,
    (-(e.clientY - rect.top) / rect.height) * 2 + 1,
  );
  ray.setFromCamera(pointer, camera);
  const root = model.getObjectByName('city_PARK-DEMO');
  if (root && ray.intersectObject(root, true).length) emit('enter');
}
onMounted(async () => {
  try {
    const rs = spec.render;
    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = rs.exposure;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.info.autoReset = false;
    renderer.shadowMap.autoUpdate = false;
    renderer.domElement.setAttribute('aria-label', '区域三维概念沙盘，可旋转缩放并进入示范园区');
    host.value.prepend(renderer.domElement);
    scene = new THREE.Scene();
    scene.background = new THREE.Color(rs.background);
    scene.fog = new THREE.Fog(rs.background, 6500, 18000);
    scene.add(new THREE.HemisphereLight('#edf5fa', '#b4b89e', rs.hemisphereIntensity));
    const sun = new THREE.DirectionalLight('#fff4dc', rs.sunIntensity);
    sun.position.set(-1300, 2800, 1400);
    sun.castShadow = true;
    sun.shadow.mapSize.setScalar(rs.shadowMapSize);
    Object.assign(sun.shadow.camera, {
      left: -2400,
      right: 2400,
      top: 1900,
      bottom: -1900,
      near: 10,
      far: 6500,
    });
    sun.shadow.camera.updateProjectionMatrix();
    sun.shadow.camera.layers.enable(2);
    sun.shadow.radius = 3;
    sun.shadow.normalBias = 1;
    sun.shadow.bias = -0.0001;
    scene.add(sun);
    // 程序化日光环境与微波法线只供材质反射，不以概念图片替代真实三维。
    sky = createDaylightSky(props.config.production.restoration.sky);
    pmrem = new THREE.PMREMGenerator(renderer);
    environment = pmrem.fromEquirectangular(sky);
    scene.environment = environment.texture;
    scene.environmentIntensity = 0.6;
    const waves = new Uint8Array(128 * 128 * 4);
    for (let y = 0; y < 128; y++)
      for (let x = 0; x < 128; x++) {
        const k = (y * 128 + x) * 4,
          nx = Math.sin(x * 0.48 + y * 0.19) * 0.25 + Math.sin(x * 0.12 - y * 0.34) * 0.15,
          ny = Math.cos(y * 0.38 + x * 0.17) * 0.22;
        waves[k] = 128 + nx * 110;
        waves[k + 1] = 128 + ny * 110;
        waves[k + 2] = 245;
        waves[k + 3] = 255;
      }
    waterNormal = new THREE.DataTexture(waves, 128, 128);
    waterNormal.wrapS = waterNormal.wrapT = THREE.RepeatWrapping;
    waterNormal.needsUpdate = true;
    camera = new THREE.PerspectiveCamera(spec.camera.fov, 1, spec.camera.near, spec.camera.far);
    bloomComposer = new EffectComposer(renderer);
    bloomComposer.renderToScreen = false;
    bloomComposer.addPass(new RenderPass(scene, camera));
    const glow = rs.bloom;
    bloomPass = new UnrealBloomPass(
      new THREE.Vector2(512, 512),
      glow.strength,
      glow.radius,
      glow.threshold,
    );
    bloomComposer.addPass(bloomPass);
    composer = new EffectComposer(renderer);
    composer.addPass(new RenderPass(scene, camera));
    aoPass = new GTAOPass(scene, camera, 512, 512, undefined, rs.ambientOcclusion);
    aoPass.blendIntensity = 0;
    // AO独立使用较低分辨率，主画面与描边保持全分辨率，降低实体林带的离屏渲染负担。
    const setAOSize = aoPass.setSize.bind(aoPass);
    aoPass.setSize = (w, h) =>
      setAOSize(
        Math.max(1, Math.round(w * rs.ambientOcclusion.resolutionScale)),
        Math.max(1, Math.round(h * rs.ambientOcclusion.resolutionScale)),
      );
    const renderAO = aoPass.render.bind(aoPass);
    aoPass.render = (...args) => {
      const mask = camera.layers.mask;
      camera.layers.disable(2);
      try {
        return renderAO(...args);
      } finally {
        camera.layers.mask = mask;
      }
    };
    composer.addPass(aoPass);
    mixPass = new ShaderPass({
      uniforms: {
        tDiffuse: { value: null },
        bloomTexture: { value: null },
        boundaryBloomMix: { value: spec.boundary.bloomMix },
      },
      vertexShader:
        'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
      fragmentShader:
        'uniform sampler2D tDiffuse;uniform sampler2D bloomTexture;uniform float boundaryBloomMix;varying vec2 vUv;void main(){vec4 base=texture2D(tDiffuse,vUv);gl_FragColor=vec4(base.rgb+texture2D(bloomTexture,vUv).rgb*boundaryBloomMix,base.a);}',
    });
    composer.addPass(mixPass);
    composer.addPass(new OutputPass());
    composer.addPass(new SMAAPass());
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.07;
    controls.minDistance = 1200;
    controls.maxDistance = 7500;
    controls.maxPolarAngle = Math.PI * 0.43;
    controls.minPolarAngle = 0.15;
    controls.autoRotateSpeed = 0.25;
    const response = await fetch('./assets/city-build-info.json', { signal: controller.signal });
    if (!response.ok) throw new Error('区域模型清单读取失败');
    const info = await response.json();
    if (info.planningSha256 !== props.config.planningSha256)
      throw new Error('区域模型与规划版本不一致');
    totalBytes.value = info.bytes;
    const assetResponse = await fetch('./assets/' + info.asset, { signal: controller.signal });
    if (!assetResponse.ok) throw new Error('区域模型读取失败');
    const bytes = await readSceneBytes(assetResponse, (received) => {
      if (!disposed) downloadedBytes.value = received;
    });
    loadingPhase.value = 'scene';
    await nextTick();
    if (disposed) return;
    const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), (v) =>
      v.toString(16).padStart(2, '0'),
    ).join('');
    if (hash !== info.assetSha256) throw new Error('区域模型哈希不一致');
    if (disposed) return;
    const gltf = await new GLTFLoader().parseAsync(bytes, './assets/');
    if (disposed) {
      dispose(gltf.scene);
      return;
    }
    model = gltf.scene;
    scene.add(model);
    const bakedAO = spec.bakedLighting.enabled && info.bakingComplete === true;
    model.traverse((obj) => {
      if (obj.isMesh) {
        if (bakedAO && obj.userData.bakeReceiver) {
          if (!obj.geometry.getAttribute('uv1') || !obj.material.aoMap)
            throw new Error('城市静态烘焙缺少UV2或AO：' + obj.name);
          obj.material.aoMapIntensity = spec.bakedLighting.aoStrength;
        }
        if (obj.material?.name?.startsWith('city_leafCard')) {
          obj.layers.set(2);
          obj.material.alphaTest = 0.48;
          obj.material.transparent = false;
          obj.material.side = THREE.DoubleSide;
          obj.material.depthWrite = true;
          obj.material.needsUpdate = true;
        }
        if (['city_water', 'city_waterDeep'].includes(obj.material?.name)) {
          obj.material.normalMap = waterNormal;
          obj.material.normalScale = new THREE.Vector2(0.012, 0.012);
          obj.material.envMapIntensity = 0.65;
          obj.material.roughness = 0.42;
          obj.material.metalness = 0.12;
          obj.material.onBeforeCompile = (shader) => {
            shader.vertexShader =
              'varying vec3 cityWaterPosition;\n' +
              shader.vertexShader.replace(
                '#include <worldpos_vertex>',
                '#include <worldpos_vertex>\ncityWaterPosition=(modelMatrix*vec4(transformed,1.0)).xyz;',
              );
            shader.fragmentShader =
              'varying vec3 cityWaterPosition;\n' +
              shader.fragmentShader.replace(
                '#include <color_fragment>',
                '#include <color_fragment>\nfloat lakeDepthVariation=sin(cityWaterPosition.x*.003+sin(cityWaterPosition.z*.004)*2.0)*sin(cityWaterPosition.z*.0043);diffuseColor.rgb*=.96+.09*lakeDepthVariation;float ripple=pow(max(0.0,sin(cityWaterPosition.x*.11+cityWaterPosition.z*.075+sin(cityWaterPosition.x*.027))),20.0);diffuseColor.rgb+=vec3(.004,.006,.007)*ripple;',
              );
          };
          obj.material.needsUpdate = true;
        }
        obj.castShadow =
          !obj.name.startsWith('regional_terrain') &&
          !obj.name.startsWith('regional_roads') &&
          !obj.name.startsWith('regional_context');
        obj.receiveShadow = true;
      }
      if (obj.name.startsWith('city_anchor_')) anchors.set(obj.name.slice(12), obj);
    });
    if (anchors.size !== spec.poi.length || !model.getObjectByName('city_PARK-DEMO'))
      throw new Error('区域对象绑定缺失');
    // 主线保留青蓝实色，浅色描边和低透明度外晕衬底；辉光单独渲染，避免把线身冲成白色。
    const curve = new THREE.CatmullRomCurve3(
      spec.outline.map(([x, y]) => new THREE.Vector3(...toThree([x, y, 5]))),
      true,
      'centripetal',
    );
    for (const layer of spec.boundary.layers) {
      const material = new THREE.MeshBasicMaterial({
        color: new THREE.Color(layer.color).multiplyScalar(layer.emission ?? 1),
        transparent: true,
        opacity: layer.opacity,
        depthWrite: false,
        depthTest: false,
        toneMapped: false,
      });
      material.onBeforeCompile = (shader) => {
        shader.uniforms.boundaryProgress = boundaryUniform;
        shader.vertexShader =
          'varying float boundaryU;\n' +
          shader.vertexShader.replace(
            '#include <uv_vertex>',
            '#include <uv_vertex>\nboundaryU=uv.x;',
          );
        shader.fragmentShader =
          'uniform float boundaryProgress;varying float boundaryU;\n' +
          shader.fragmentShader.replace(
            '#include <color_fragment>',
            '#include <color_fragment>\nif(boundaryU>boundaryProgress)discard; if(boundaryProgress<1.0)diffuseColor.rgb*=1.0+.15*smoothstep(.025,0.0,abs(boundaryU-boundaryProgress));',
          );
      };
      const border = new THREE.Mesh(
        new THREE.TubeGeometry(curve, spec.outline.length * 6, layer.radius, 6, true),
        material,
      );
      border.renderOrder = layer.order;
      if (layer.glow) border.layers.set(1);
      scene.add(border);
    }
    // 共享展示进度控制材质由轮廓色恢复；不修改透明叶片的深度与Alpha契约。
    const seen = new Set(),
      parkMaterials = new Map();
    model.traverse((obj) => {
      if (!obj.isMesh) return;
      const parkMesh = obj.name.startsWith('regional_campus');
      if (parkMesh) {
        const clone = (m) => {
          if (!parkMaterials.has(m)) parkMaterials.set(m, m.clone());
          return parkMaterials.get(m);
        };
        obj.material = Array.isArray(obj.material) ? obj.material.map(clone) : clone(obj.material);
      }
      for (const material of Array.isArray(obj.material) ? obj.material : [obj.material]) {
        if (seen.has(material)) continue;
        seen.add(material);
        const original = material.onBeforeCompile.bind(material),
          isPark = parkMesh || material.name === 'city_zoneGold',
          isFacade = ['city_building', 'city_buildingWarm'].includes(material.name);
        material.onBeforeCompile = (shader) => {
          original(shader);
          if (isFacade) {
            shader.vertexShader =
              'varying vec3 cityFacadePosition;varying vec3 cityFacadeNormal;\n' +
              shader.vertexShader.replace(
                '#include <worldpos_vertex>',
                '#include <worldpos_vertex>\ncityFacadePosition=(modelMatrix*vec4(transformed,1.0)).xyz;cityFacadeNormal=normalize(mat3(modelMatrix)*objectNormal);',
              );
            shader.fragmentShader =
              'varying vec3 cityFacadePosition;varying vec3 cityFacadeNormal;\n' +
              shader.fragmentShader.replace(
                '#include <color_fragment>',
                '#include <color_fragment>\nif(abs(cityFacadeNormal.y)<.45){float axis=abs(cityFacadeNormal.x)>.5?cityFacadePosition.z:cityFacadePosition.x;float windows=step(.28,fract(axis/4.6))*step(.3,fract(cityFacadePosition.y/4.2));diffuseColor.rgb=mix(diffuseColor.rgb,vec3(.42,.53,.54),windows*.22);}',
              );
          }
          shader.uniforms.cityReveal = revealUniform;
          shader.uniforms.cityMaterial = materialUniform;
          shader.uniforms.parkReveal = parkUniform;
          shader.fragmentShader =
            'uniform float cityReveal;uniform float cityMaterial;uniform float parkReveal;\n' +
            shader.fragmentShader.replace(
              '#include <color_fragment>',
              '#include <color_fragment>\nfloat reveal=cityReveal;' +
                (isPark ? 'reveal*=parkReveal;' : '') +
                'float neutral=dot(diffuseColor.rgb,vec3(.2126,.7152,.0722));diffuseColor.rgb=mix(vec3(.76,.81,.78),mix(vec3(neutral),diffuseColor.rgb,.12+.88*cityMaterial),.12+.88*reveal);',
            );
        };
        material.customProgramCacheKey = () => `city-v19-${isPark}-${isFacade}`;
        material.needsUpdate = true;
      }
    });
    pulseRing = new THREE.Mesh(
      new THREE.RingGeometry(65, 76, 64),
      new THREE.MeshBasicMaterial({
        color: '#c69a50',
        transparent: true,
        opacity: 0,
        side: THREE.DoubleSide,
        depthWrite: false,
        depthTest: false,
      }),
    );
    pulseRing.rotation.x = -Math.PI / 2;
    pulseRing.position.set(...toThree([spec.campusPositionM[0], spec.campusPositionM[1], 12]));
    pulseRing.renderOrder = 6;
    pulseRing.visible = false;
    scene.add(pulseRing);
    poiRing = new THREE.Mesh(
      new THREE.RingGeometry(130, 136, 80),
      new THREE.MeshBasicMaterial({
        color: '#168d99',
        transparent: true,
        opacity: 0.75,
        side: THREE.DoubleSide,
        depthWrite: false,
      }),
    );
    poiDisc = new THREE.Mesh(
      new THREE.CircleGeometry(130, 80),
      new THREE.MeshBasicMaterial({
        color: '#1da0ab',
        transparent: true,
        opacity: 0.14,
        side: THREE.DoubleSide,
        depthWrite: false,
      }),
    );
    for (const object of [poiRing, poiDisc]) {
      object.rotation.x = -Math.PI / 2;
      object.visible = false;
      scene.add(object);
    }
    for (const item of spec.poi) {
      const campus = item.action === 'enter-campus',
        node = document.createElement('button');
      node.type = 'button';
      node.className = 'city-label ' + (campus ? 'campus-pin' : 'neutral-pin');
      node.dataset.regionId = item.id;
      node.setAttribute('aria-label', campus ? '从区域进入光谷示范园区' : '查看' + item.label);
      if (campus) {
        const title = document.createElement('strong');
        title.textContent = item.label;
        const action = document.createElement('span');
        action.textContent = '进入园区 ›';
        node.append(title, action);
        node.addEventListener('click', () => emit('enter'));
      } else {
        node.textContent = item.label + ' ›';
        node.addEventListener('click', () => selectPoi(item));
      }
      labelHost.value.append(node);
      labels.set(item.id, node);
    }
    window.addEventListener('keydown', escapePoi, true);
    renderer.shadowMap.needsUpdate = true;
    reset();
    observer = new ResizeObserver(resize);
    observer.observe(host.value);
    window.addEventListener('resize', resize);
    document.addEventListener('visibilitychange', visibility);
    renderer.domElement.addEventListener('pointerdown', down, true);
    renderer.domElement.addEventListener('pointerup', up);
    loadingPhase.value = 'ready';
    await nextTick();
    if (disposed) return;
    resize();
    ready = true;
    reduced.addEventListener('change', reduceChanged);
    renderer.domElement.addEventListener('wheel', interrupt, { capture: true, passive: true });
    startEntrance();
    function render(time) {
      if (disposed) return;
      frame = requestAnimationFrame(render);
      if (!props.active || document.visibilityState !== 'visible') {
        lastTime = 0;
        return;
      }
      const visibleDelta = lastTime ? Math.min((time - lastTime) / 1000, 0.1) : 0;
      if (playing) {
        elapsed += visibleDelta;
        applyEntrance(true);
        if (frameState.done) {
          playing = false;
          controls.enableDamping = true;
          applyEntrance();
        }
      }
      if (lastTime) {
        samples.push(time - lastTime);
        if (samples.length > 600) samples.shift();
      }
      lastTime = time;
      controls.autoRotate =
        !!props.tour &&
        !entryFrame &&
        !playing &&
        !matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (cameraMove) {
        cameraMove.t = Math.min(1, cameraMove.t + visibleDelta / 0.7);
        const k = cameraMove.t * cameraMove.t * (3 - 2 * cameraMove.t);
        camera.position.copy(cameraMove.fromEye).addScaledVector(cameraMove.delta, k);
        controls.target.copy(cameraMove.fromTarget).addScaledVector(cameraMove.delta, k);
        if (cameraMove.t === 1) cameraMove = null;
      }
      if (!entryFrame) controls.update();
      const viewDistance = camera.position.distanceTo(controls.target);
      scene.fog.near = viewDistance * spec.context.fogNearDistanceFactor;
      scene.fog.far = scene.fog.near + spec.context.fogDepthM;
      host.value.dataset.selectedPoi = selectedPoi.value ?? '';
      host.value.dataset.cameraPosition = JSON.stringify(camera.position.toArray());
      scene.updateMatrixWorld(true);
      const projected = {};
      for (const [id, node] of anchors) {
        const p = node.getWorldPosition(new THREE.Vector3()).project(camera);
        const label = labels.get(id);
        label.hidden =
          frameState.labels < 0.01 ||
          p.z > 1 ||
          p.x < -0.96 ||
          p.x > 0.96 ||
          p.y < -0.94 ||
          p.y > 0.94;
        label.disabled = !!entryFrame || frameState.labels < 0.7;
        label.tabIndex = label.disabled ? -1 : 0;
        label.style.opacity =
          frameState.labels *
          (entryFrame ? (id === 'PARK-DEMO' ? entryFrame.parkLabel : entryFrame.otherLabels) : 1);
        label.style.pointerEvents = !entryFrame && frameState.labels > 0.7 ? '' : 'none';
        label.style.transform = `translate(${(p.x * 0.5 + 0.5) * host.value.clientWidth}px,${(-p.y * 0.5 + 0.5) * host.value.clientHeight + (1 - frameState.labels) * 10}px) translate(-50%,-100%)`;
        projected[id] = { x: p.x * 0.5 + 0.5, y: -p.y * 0.5 + 0.5, visible: !label.hidden };
      }
      placePoiCard(time);
      host.value.dataset.cityProjection = JSON.stringify(projected);
      const bounds = spec.outline.map(([x, y]) =>
        new THREE.Vector3(...toThree([x, y, 0])).project(camera),
      );
      host.value.dataset.cityBounds = JSON.stringify({
        left: Math.min(...bounds.map((p) => p.x * 0.5 + 0.5)),
        right: Math.max(...bounds.map((p) => p.x * 0.5 + 0.5)),
        top: Math.min(...bounds.map((p) => -p.y * 0.5 + 0.5)),
        bottom: Math.max(...bounds.map((p) => -p.y * 0.5 + 0.5)),
      }); // 镜头运动期间沿用真实日光阴影，停稳后淡入AO，避免连续重算高成本的屏幕空间遮蔽。
      aoBlend = playing || entryFrame ? 0 : Math.min(1, aoBlend + visibleDelta * 5);
      aoPass.enabled = !bakedAO && !playing && !entryFrame;
      aoPass.blendIntensity = rs.ambientOcclusion.blendIntensity * aoBlend;
      renderer.info.reset();
      const background = scene.background;
      scene.background = new THREE.Color(0x000000);
      camera.layers.set(1);
      renderer.shadowMap.enabled = false;
      bloomComposer.render();
      scene.background = background;
      camera.layers.set(0);
      camera.layers.enable(2);
      renderer.shadowMap.enabled = true;
      mixPass.uniforms.bloomTexture.value = bloomPass.renderTargetsHorizontal[0].texture;
      composer.render();
      if (frames === 0) report('');
      frames++;
      if (time - lastStats > 1200) {
        const sorted = [...samples].sort((a, b) => a - b);
        emit('stats', {
          quality: info.quality,
          asset: info.asset,
          assetVersion: hash.slice(0, 12),
          objects: spec.poi.map((i) => i.id),
          anchors: [...anchors.keys()],
          modelTriangles: info.triangles,
          triangles: renderer.info.render.triangles,
          calls: renderer.info.render.calls,
          geometries: renderer.info.memory.geometries,
          textures: renderer.info.memory.textures,
          frames,
          frameP95: sorted.length
            ? +sorted[Math.floor((sorted.length - 1) * 0.95)].toFixed(1)
            : null,
          level: 'city',
          selection: selectedPoi.value ?? 'PARK-DEMO',
        });
        lastStats = time;
      }
    }
    frame = requestAnimationFrame(render);
  } catch (e) {
    if (!disposed) {
      console.error(e);
      emit('entrance', { panel: 1, done: true });
      report('区域场景加载失败，请检查资源后重试', true);
    }
  }
});
watch(
  () => props.resetTick,
  () => {
    if (props.active) {
      finishEntrance();
      reset();
    }
  },
);
watch(
  () => props.replayTick,
  () => {
    if (props.active) startEntrance();
  },
);
watch(
  () => props.tour,
  () => {
    if (props.tour) finishEntrance();
  },
);
watch(
  () => props.active,
  () => {
    lastTime = 0;
    if (!props.active) {
      finishEntrance();
      closePoi();
    } else {
      resize();
      startEntrance(true);
    }
  },
);
onBeforeUnmount(() => {
  disposed = true;
  window.removeEventListener('keydown', escapePoi, true);
  reduced.removeEventListener('change', reduceChanged);
  renderer?.domElement.removeEventListener('wheel', interrupt, true);
  controller.abort();
  cancelAnimationFrame(frame);
  observer?.disconnect();
  window.removeEventListener('resize', resize);
  document.removeEventListener('visibilitychange', visibility);
  renderer?.domElement.removeEventListener('pointerdown', down, true);
  renderer?.domElement.removeEventListener('pointerup', up);
  controls?.dispose();
  dispose(scene);
  waterNormal?.dispose();
  sky?.dispose();
  environment?.dispose();
  pmrem?.dispose();
  composer?.passes.forEach((p) => p.dispose());
  composer?.dispose();
  bloomComposer?.passes.forEach((p) => p.dispose());
  bloomComposer?.dispose();
  renderer?.dispose();
  renderer?.forceContextLoss();
  renderer?.domElement.remove();
  labels.forEach((l) => l.remove());
});

const definitions = props.config.demoDesign.contentDefinitions;
const reload = () => window.location.reload();
</script>

<template>
  <div ref="host" class="scene-view city-scene">
    <div ref="labelHost" class="labels"></div>
    <svg
      v-if="selectedPoi && cardPosition?.owner === selectedPoi"
      class="card-tether"
      aria-hidden="true"
    >
      <path :d="cardPosition.path" />
    </svg>
    <section
      v-if="selectedInfo"
      class="city-info-card object-popover"
      role="dialog"
      :aria-label="selectedInfo.label + '信息'"
      :data-poi-id="selectedInfo.id"
      :data-placement="cardPosition?.side"
      :data-obstruction="cardPosition?.obstruction"
      :style="{
        left: (cardPosition?.left ?? 0) + 'px',
        top: (cardPosition?.top ?? 0) + 'px',
        visibility: cardPosition?.owner === selectedPoi ? 'visible' : 'hidden',
      }"
    >
      <header class="popover-head">
        <div class="popover-symbol">
          <Icon :name="selectedPoi === 'INDUSTRY-DEMO' ? 'building' : 'briefcase'" />
        </div>
        <div class="popover-heading">
          <p class="card-eyebrow">{{ selectedInfo.content.eyebrow }} · 区域概览</p>
          <h2>{{ selectedInfo.label }}</h2>
        </div>
        <button class="card-close" aria-label="关闭区域信息" @click="closePoi">
          <Icon name="close" />
        </button>
      </header>
      <div class="popover-body">
        <template v-if="selectedPoi === 'INDUSTRY-DEMO'"
          ><dl class="popover-metrics industry-metrics">
            <div>
              <dt>园区楼宇</dt>
              <dd>{{ number(data.campus.buildings) }}<small>栋</small></dd>
            </div>
            <div>
              <dt>建筑面积</dt>
              <dd>{{ area(data.campus.grossAreaM2) }}<small>万㎡</small></dd>
            </div>
          </dl>
          <p class="popover-section-label">产业方向</p>
          <ul class="popover-tags">
            <li v-for="item in definitions.industryDirections.labels" :key="item">{{ item }}</li>
          </ul></template
        >
        <ul v-else class="popover-services">
          <li v-for="(item, index) in definitions.services.labels" :key="item">
            <Icon :name="['meeting', 'parking', 'bus'][index]" />
            <div>
              <strong>{{ item }}</strong
              ><span>{{ ['交流与协作', '到访与泊车', '园区通达'][index] }}</span>
            </div>
          </li>
        </ul>
      </div>
      <footer class="popover-footer">
        <span class="quality-dot">{{
          selectedPoi === 'INDUSTRY-DEMO' ? '演示数据' : '示范配套'
        }}</span
        ><span>{{ selectedPoi === 'INDUSTRY-DEMO' ? '光谷示范园区' : '设施信息待核定' }}</span>
      </footer>
    </section>
    <Transition name="scene-loading">
      <SceneLoading
        v-if="status"
        scene="city"
        :phase="loadingPhase"
        :downloaded="downloadedBytes"
        :total="totalBytes"
        :message="status"
        :error="failure"
        @retry="reload"
      />
    </Transition>
  </div>
</template>
