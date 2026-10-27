// 城市入场的单一时间线；只派生展示状态，不改变业务快照、对象身份或统计。
const clamp = (x) => Math.max(0, Math.min(1, x));
const smooth = (x) => {
  x = clamp(x);
  return x * x * (3 - 2 * x);
};
export function entranceFrame(seconds, spec, { reduced = false, returning = false } = {}) {
  const full = reduced || seconds >= spec.duration;
  const progress = (range) => (full ? 1 : smooth((seconds - range[0]) / (range[1] - range[0])));
  if (returning) {
    const fade = reduced ? 1 : smooth(seconds / spec.returnDuration);
    return {
      city: fade,
      material: 1,
      boundary: 1,
      park: 1,
      labels: fade,
      panel: 1,
      camera: 1,
      pulse: 0,
      done: fade === 1,
    };
  }
  return {
    city: progress(spec.cityReveal),
    material: progress(spec.materialReveal),
    boundary: progress(spec.boundaryReveal),
    park: progress(spec.parkReveal),
    labels: progress(spec.labelsReveal),
    panel: progress(spec.panelReveal),
    camera: full ? 1 : smooth(seconds / spec.duration),
    pulse: full
      ? 0
      : clamp((seconds - spec.parkReveal[0]) / (spec.parkReveal[1] - spec.parkReveal[0])),
    done: full,
  };
}
