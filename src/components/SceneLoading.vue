<script setup>
// 三层场景共用加载反馈；阶段与字节数由实际加载链路提供。
import { computed, useId } from 'vue';
const gradientId = useId();
const props = defineProps({
  scene: { type: String, required: true },
  phase: { type: String, required: true },
  downloaded: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  error: { type: Boolean, default: false },
  message: { type: String, required: true },
});
defineEmits(['retry']);
const scenes = {
  city: {
    label: '区域总览',
    title: '城市脉络，即将呈现',
    description: '正在准备区域空间，稍后为您展开光谷全景',
  },
  campus: {
    label: '园区总览',
    title: '园区空间，即将展开',
    description: '正在准备园区资源，即将开启楼宇探索',
  },
  building: {
    label: '重点楼宇',
    title: '楼宇细节，即将展开',
    description: '正在准备楼宇空间，即将呈现建筑细节',
  },
};
const current = computed(() => scenes[props.scene]);
const phases = [
  { id: 'resources', label: '资源载入', message: '正在载入空间资源' },
  { id: 'scene', label: '空间构建', message: '正在构建三维空间' },
  { id: 'ready', label: '画面呈现', message: '正在准备首帧画面' },
];
const phaseIndex = computed(() => phases.findIndex((item) => item.id === props.phase));
const determinate = computed(() => props.phase === 'resources' && props.total > 0);
const percent = computed(() => Math.min(100, Math.floor((props.downloaded / props.total) * 100)));
const megabytes = (value) => (value / 1000000).toFixed(1);
</script>
<template>
  <section
    class="scene-loading"
    :class="{ 'scene-loading--error': error }"
    :aria-label="current.label + '资源加载'"
    :aria-busy="!error"
    :data-loading-phase="phase"
    :data-loaded-bytes="downloaded"
    :data-total-bytes="total"
  >
    <div class="micro">光谷 · 数字空间</div>
    <div class="loading-content">
      <svg class="drawing" viewBox="0 0 420 270" aria-hidden="true">
        <defs>
          <linearGradient :id="gradientId" x1="0" y1="0" x2="0" y2="1">
            <stop stop-color="#6eb9a0" stop-opacity="0" />
            <stop offset="1" stop-color="#6eb9a0" stop-opacity=".32" />
          </linearGradient>
        </defs>
        <path
          class="map"
          d="M20 174 197 72 400 185M20 192 197 90 400 203M51 211 228 109M87 232 264 130M123 253 300 151M25 153 203 256M59 134 237 237M95 113 273 216M133 91 311 194M171 69 349 172"
        />
        <ellipse class="halo" cx="211" cy="194" rx="148" ry="63" />
        <path class="site" d="m73 188 133-77 140 81-133 77Z" />
        <path class="trace" d="m73 188 133-77 140 81-133 77Z" />
        <g transform="translate(0 -9)">
          <path class="soft" d="m107 173 41-24 29 17v42l-41 24-29-17Z" />
          <path
            class="windows"
            d="m107 181 29 17 41-24m-41 24v34m-29-40 29 17 41-24m-70 18 29 17 41-24"
          />
        </g>
        <g>
          <path class="front" d="m181 85 44 25v123l-44-25Z" />
          <path class="side" d="m225 110 46-27v123l-46 27Z" />
          <path class="top" d="m181 85 46-27 44 25-46 27Z" />
          <path
            class="windows"
            d="m191 91 0 123m11-117v124m11-118v124m23-123v123m12-130v123m12-130v123M181 101l44 25 46-27m-90 18 44 25 46-27m-90 18 44 25 46-27m-90 18 44 25 46-27m-90 18 44 25 46-27m-90 18 44 25 46-27m-90 18 44 25 46-27"
          />
        </g>
        <g>
          <path class="soft" d="m278 173 32-19 30 17v44l-32 19-30-17Z" />
          <path class="windows" d="m278 183 30 17 32-19m-32 19v34m-30-41 30 17 32-19" />
        </g>
        <path
          class="scan"
          :style="{ fill: `url(#${gradientId})` }"
          d="m151 84 77-44 76 44v27l-77 44-76-44Z"
        />
        <g class="nodes">
          <circle cx="74" cy="188" r="2.2" />
          <circle cx="346" cy="192" r="2.2" />
          <circle cx="213" cy="269" r="2.2" />
        </g>
      </svg>
      <div class="eyebrow">{{ current.label }}</div>
      <h2>{{ error ? '空间暂未就绪' : current.title }}</h2>
      <p class="description">
        {{ error ? '暂时未能完成资源准备，可重新载入后再试。' : current.description }}
      </p>
      <div class="progress">
        <div class="progress-head">
          <span role="status" aria-live="polite">{{
            error ? message : phases[phaseIndex].message
          }}</span
          ><b aria-hidden="true">{{ String(phaseIndex + 1).padStart(2, '0') }} / 03</b>
        </div>
        <div
          v-if="!error"
          class="track"
          :class="{ 'track--indeterminate': !determinate }"
          role="progressbar"
          :aria-label="determinate ? '空间资源下载' : '场景准备'"
          :aria-valuenow="determinate ? percent : undefined"
          :aria-valuemin="0"
          :aria-valuemax="100"
        >
          <i v-if="determinate" :style="{ width: percent + '%' }"></i>
        </div>
        <div v-else class="error-rule"></div>
        <div v-if="determinate && !error" class="download" aria-hidden="true">
          {{ megabytes(downloaded) }} / {{ megabytes(total) }} MB
        </div>
        <div class="steps" aria-hidden="true">
          <span
            v-for="(item, index) in phases"
            :key="item.id"
            :class="{ active: index === phaseIndex, done: index < phaseIndex }"
            ><i></i>{{ item.label }}</span
          >
        </div>
      </div>
      <button v-if="error" class="retry" type="button" @click="$emit('retry')">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 10a8 8 0 1 1 0 5M4 4v6h6" /></svg
        >重新载入
      </button>
      <p v-else class="help">首次进入需要准备三维资源</p>
    </div>
    <div class="annotation">高新区数字楼宇</div>
  </section>
</template>

<style scoped>
.scene-loading {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: linear-gradient(130deg, #f3f5f0f2, #f1f4edf5 65%, #eaf1ebf2);
  backdrop-filter: blur(12px);
  display: grid;
  place-items: center;
  z-index: 10;
  color: #153f42;
}
.scene-loading:before {
  content: '';
  position: absolute;
  width: 975px;
  height: 975px;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -58%);
  background: radial-gradient(ellipse, #dcece578, transparent 68%);
  pointer-events: none;
}
.micro {
  position: absolute;
  top: 55px;
  left: 66px;
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 16px;
  letter-spacing: 0.16em;
  color: #63837d;
}
.micro:before {
  content: '';
  width: 9px;
  height: 9px;
  background: #258a82;
  border-radius: 50%;
  box-shadow: 0 0 0 6px #2b8d7c0c;
}
.annotation {
  position: absolute;
  right: 57px;
  bottom: 46px;
  font-size: 15px;
  color: #718b7d;
  letter-spacing: 0.17em;
}
.loading-content {
  position: relative;
  width: 690px;
  max-width: 85%;
  text-align: center;
  transform: translateY(-25px);
}
.drawing {
  display: block;
  width: 555px;
  max-width: 100%;
  height: 368px;
  margin: 0 auto 15px;
  overflow: visible;
}
.map {
  fill: none;
  stroke: #a5bfb4;
  stroke-width: 0.8;
  opacity: 0.55;
}
.site {
  fill: #e4eee7;
  stroke: #b5cdbf;
  stroke-width: 1;
}
.soft {
  fill: #f3f7f0;
  stroke: #7ba99c;
  stroke-width: 1;
}
.front {
  fill: #e3efe7;
  stroke: #499889;
  stroke-width: 1;
}
.side {
  fill: #cde2d7;
  stroke: #499889;
  stroke-width: 1;
}
.top {
  fill: #f3f8ee;
  stroke: #499889;
  stroke-width: 1;
}
.windows {
  stroke: #7bafa1;
  stroke-width: 0.75;
  fill: none;
}
.trace {
  stroke: #17867e;
  stroke-width: 1.8;
  fill: none;
  stroke-linecap: round;
  stroke-dasharray: 68 300;
  animation: trace 4s linear infinite;
}
.scan {
  animation: scan 3s ease-in-out infinite;
}
.nodes circle {
  fill: #1d8a7e;
  opacity: 0.7;
}
.halo {
  fill: none;
  stroke: #8fb5a2;
  stroke-width: 0.6;
  stroke-dasharray: 2 6;
  opacity: 0.6;
}
.eyebrow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 21px;
  font-size: 17px;
  letter-spacing: 0.18em;
  color: #59817a;
  margin-bottom: 24px;
}
.eyebrow:before,
.eyebrow:after {
  content: '';
  height: 1px;
  width: 44px;
  background: #9cbcb0;
}
.loading-content h2 {
  font-size: 44px;
  letter-spacing: 0.06em;
  font-weight: 550;
  margin: 0 0 20px;
  line-height: 1.4;
}
.description {
  font-size: 20px;
  letter-spacing: 0.03em;
  color: #647e72;
  margin: 0;
  line-height: 1.8;
}
.progress {
  margin: 51px auto 0;
  width: 525px;
  max-width: 100%;
  position: relative;
}
.progress-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  font-size: 17px;
  color: #4f7e74;
  margin-bottom: 18px;
  line-height: 1.6;
}
.progress-head > span {
  text-align: left;
}
.progress-head b {
  font-family: monospace;
  font-size: 17px;
  font-weight: 400;
  letter-spacing: 0.13em;
  color: #638174;
  white-space: nowrap;
}
.track {
  height: 3px;
  background: #d9e4da;
  overflow: hidden;
  position: relative;
}
.track > i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #6ba995, #13877b);
  transition: width 0.18s linear;
}
.track--indeterminate:before {
  content: '';
  display: block;
  height: 100%;
  width: 46%;
  background: linear-gradient(90deg, transparent, #13877b 70%, #4c9d8a);
  animation: progress 2.8s ease-in-out infinite;
}
.download {
  text-align: right;
  font-size: 15px;
  font-variant-numeric: tabular-nums;
  color: #647e72;
  margin-top: 10px;
  position: absolute;
  right: 0;
  top: 48px;
}
.steps {
  display: flex;
  justify-content: space-between;
  margin-top: 34px;
  font-size: 15px;
  color: #6d887a;
}
.steps span {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}
.steps i {
  width: 6px;
  height: 6px;
  border: 1px solid #9eb6a9;
  border-radius: 50%;
}
.steps .active {
  color: #297e72;
}
.steps .active i,
.steps .done i {
  border: 0;
  background: #268878;
}
.steps .active i {
  box-shadow: 0 0 0 4px #d9e8dc;
}
.help {
  margin: 58px 0 0;
  font-size: 15px;
  letter-spacing: 0.08em;
  color: #718b7d;
  line-height: 1.6;
}
.retry {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 42px;
  padding: 15px 28px;
  border: 1px solid #b4b9a7;
  border-radius: 30px;
  background: #fffef7c9;
  color: #41695f;
  font-size: 19px;
  cursor: pointer;
  transition:
    background 0.2s,
    border-color 0.2s;
}
.retry:hover {
  background: #fffef7;
  border-color: #6f9687;
}
.retry svg {
  width: 22px;
  height: 22px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.retry:focus-visible {
  outline: 3px solid #47a8af;
  outline-offset: 4px;
}
.error-rule {
  height: 3px;
  background: #bf9b7f66;
}
.scene-loading--error .trace,
.scene-loading--error .scan {
  animation: none;
}
.scene-loading--error .scan {
  opacity: 0;
}
.scene-loading--error .trace {
  stroke: #a38267;
}
.scene-loading--error .progress-head {
  color: #88674f;
}
.scene-loading-leave-active {
  transition: opacity 0.28s ease;
}
.scene-loading-leave-to {
  opacity: 0;
  pointer-events: none;
}
@keyframes progress {
  from {
    transform: translateX(-110%);
  }
  to {
    transform: translateX(330%);
  }
}
@keyframes trace {
  to {
    stroke-dashoffset: -368;
  }
}
@keyframes scan {
  0%,
  100% {
    opacity: 0;
    transform: translateY(-25px);
  }
  45% {
    opacity: 0.6;
  }
  70% {
    transform: translateY(20px);
    opacity: 0;
  }
}
@media (prefers-reduced-motion: reduce) {
  .trace,
  .scan,
  .track--indeterminate:before {
    animation: none;
  }
  .scan {
    opacity: 0;
  }
  .track--indeterminate:before {
    width: 33%;
    transform: none;
  }
  .track > i,
  .scene-loading-leave-active {
    transition: none;
  }
}
</style>
