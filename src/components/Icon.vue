<script setup>
// 终稿的实心语义图标；出租率饼扇是图标符号，实际比例仍由旁侧数值表达。
import { computed } from 'vue';
const solid = {
  building:
    'M3 22V5l10-3v20h-3V6L6 7v15Zm11-14 7 3v11h-7Zm-7 1h2v3H7Zm0 5h2v3H7Zm0 5h2v3H7Zm9-7h2v3h-2Zm0 5h2v3h-2ZM1 22h22v2H1Z',
  area: 'm1 7 11-6 11 6-11 6Zm0 6 3-1.6 8 4.4 8-4.4 3 1.6-11 6Zm0 6 3-1.6 8 4.4 8-4.4 3 1.6-11 6Z',
  people:
    'M12 2a4 4 0 1 1 0 8 4 4 0 0 1 0-8ZM3 5a3 3 0 1 1 0 6 3 3 0 0 1 0-6Zm18 0a3 3 0 1 1 0 6 3 3 0 0 1 0-6ZM7 22v-6a5 5 0 0 1 10 0v6ZM0 22v-6a4 4 0 0 1 5-3.9V22Zm19 0v-9.9a4 4 0 0 1 5 3.9v6Z',
  chip: 'M6 5V1h2v4h3V1h2v4h3V1h2v4h2v2h4v2h-4v3h4v2h-4v3h4v2h-4v2h-2v4h-2v-4h-3v4h-2v-4H8v4H6v-4H4v-2H0v-2h4v-3H0v-2h4V9H0V7h4V5Zm2 4v8h8V9Z',
  briefcase:
    'M8 1h8a2 2 0 0 1 2 2v3h4a2 2 0 0 1 2 2v5H0V8a2 2 0 0 1 2-2h4V3a2 2 0 0 1 2-2Zm0 3v2h8V4ZM0 15h10v2h4v-2h10v7a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2Z',
  parking:
    'M4 1h16a3 3 0 0 1 3 3v17a3 3 0 0 1-3 3H4a3 3 0 0 1-3-3V4a3 3 0 0 1 3-3Zm4 4v15h3v-5h3a5 5 0 0 0 0-10Zm3 3h3a2 2 0 0 1 0 4h-3Z',
  bus: 'M6 1h12a4 4 0 0 1 4 4v14a2 2 0 0 1-2 2v3h-3v-3H7v3H4v-3a2 2 0 0 1-2-2V5a4 4 0 0 1 4-4ZM5 5v8h14V5Zm2 11a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Zm10 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z',
};
const lines = {
  code: 'm7 5-6 7 6 7m10-14 6 7-6 7m-3-17-4 20',
  back: 'm14 5-7 7 7 7',
  reset: 'M4 10a8 8 0 1 1 0 5M4 4v6h6',
  settings: 'M5 6h14M5 12h14M5 18h14',
  close: 'm5 5 14 14M19 5 5 19',
  expand: 'M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5',
};
const props = defineProps(['name']);
const filled = computed(() => !!solid[props.name] || props.name === 'meeting');
const path = computed(
  () =>
    solid[props.name === 'meeting' ? 'people' : props.name] || lines[props.name] || solid.building,
);
</script>

<template>
  <svg viewBox="-1 -1 26 27" aria-hidden="true">
    <template v-if="name === 'rate'">
      <path fill="currentColor" d="M11 1a11 11 0 1 0 11 12H11Z" />
      <path fill="#a88d73" d="M13 0v11h11A11 11 0 0 0 13 0Z" />
    </template>
    <path
      v-else
      :d="path"
      :fill="filled ? 'currentColor' : 'none'"
      :stroke="filled ? 'none' : 'currentColor'"
      :stroke-width="name === 'code' ? 2.7 : 1.8"
      fill-rule="evenodd"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>
