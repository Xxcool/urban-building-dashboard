// 按规划画布等比例适配窗口，统一场景宽度与界面缩放。
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
export function useDashboardViewport(config) {
  // 设计尺寸只控制 UI 的等比缩放；逻辑画布扩展到窗口边缘，宽屏余量交给三维场景。
  const baseViewport = config.project.viewport;
  const viewport = ref({ width: innerWidth, height: innerHeight });
  const scale = computed(() =>
    Math.min(
      viewport.value.width / baseViewport.width,
      viewport.value.height / baseViewport.height,
    ),
  );
  const canvasSize = computed(() => ({
    width: viewport.value.width / scale.value,
    height: viewport.value.height / scale.value,
  }));
  const railWidth = baseViewport.width * config.design.layout.railFraction;
  const sceneStyle = computed(() => ({
    left: railWidth + 'px',
    width: canvasSize.value.width - railWidth + 'px',
  }));
  const screenStyle = computed(() => ({
    width: canvasSize.value.width + 'px',
    height: canvasSize.value.height + 'px',
    transform: `translate(-50%,-50%) scale(${scale.value})`,
    ...Object.fromEntries(Object.entries(config.design.palette).map(([k, v]) => ['--' + k, v])),
    '--title-size': config.design.typography.titlePx + 'px',
    '--metric-size': config.design.typography.metricPx + 'px',
    '--body-size': config.design.typography.bodyPx + 'px',
    '--rail-padding': config.design.layout.paddingPx + 'px',
    '--rail-width': railWidth + 'px',
  }));
  const resize = () => (viewport.value = { width: innerWidth, height: innerHeight });

  onMounted(() => {
    resize();
    window.addEventListener('resize', resize);
  });
  onBeforeUnmount(() => window.removeEventListener('resize', resize));
  return { sceneStyle, screenStyle, resize };
}
