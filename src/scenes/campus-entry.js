// 城市到园区的统一展示时间线与镜头坐标换算；不改变对象、指标或交通仿真时间。
const clamp = (x) => Math.max(0, Math.min(1, x));
const smooth = (x) => {
  x = clamp(x);
  return x * x * (3 - 2 * x);
};
const lerp = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
const poseLerp = (a, b, t) => ({
  eye: lerp(a.eye, b.eye, t),
  target: lerp(a.target, b.target, t),
  fov: a.fov + (b.fov - a.fov) * t,
});
export function campusEntryFrame(seconds, spec, { repeat = false, reduced = false } = {}) {
  const duration = reduced ? spec.reducedDuration : repeat ? spec.repeatDuration : spec.duration;
  const time = clamp(seconds / duration) * spec.duration;
  const progress = (range) => smooth((time - range[0]) / (range[1] - range[0]));
  const done = seconds >= duration,
    handoff = reduced || time >= spec.handoff[0];
  const opacity = reduced ? smooth(seconds / duration) : progress(spec.handoff);
  return {
    duration,
    time,
    done,
    handoff,
    phase: done
      ? 'complete'
      : reduced
        ? 'handoff'
        : time < spec.approach[0]
          ? 'locate'
          : time < spec.handoff[0]
            ? 'approach'
            : time < spec.handoff[1]
              ? 'handoff'
              : time < spec.panel[0]
                ? 'settle'
                : 'reveal',
    approach: progress(spec.approach),
    settle: progress(spec.settle),
    campusOpacity: opacity,
    cityOpacity: opacity === 1 ? 0 : 1,
    cityPanel: 1 - progress(spec.cityPanel),
    panel: reduced ? opacity : progress(spec.panel),
    kpis: Array.from({ length: 4 }, (_, i) =>
      reduced ? opacity : progress([spec.panel[0] + i * spec.kpiStagger, spec.panel[1]]),
    ),
    material: reduced ? 1 : progress(spec.material),
    labels: reduced ? [opacity, opacity, opacity] : spec.labels.map(progress),
    otherLabels: 1 - progress(spec.locate),
    parkLabel: 1 - progress(spec.approach),
    pulse: reduced ? 0 : Math.sin(Math.PI * clamp(time / spec.locate[1])),
  };
}
export function entryGateSeconds(spec, options = {}) {
  const duration = options.reduced
    ? spec.reducedDuration
    : options.repeat
      ? spec.repeatDuration
      : spec.duration;
  return options.reduced ? 0 : (spec.handoff[0] / spec.duration) * duration;
}
export function advanceEntryClock(seconds, delta, ready, spec, options = {}) {
  const next = seconds + Math.max(0, Math.min(delta, spec.maxStepSeconds));
  return ready ? next : Math.min(next, entryGateSeconds(spec, options));
}
export function campusEntryCameras(start, production, frame, { reduced = false } = {}) {
  const c = production.city,
    spec = production.campusEntry,
    origin = [c.campusPositionM[0], c.campusPositionM[2], -c.campusPositionM[1]],
    scale = c.campusScale;
  const map = (pose, inward) => ({
    eye: pose.eye.map((v, i) => (inward ? (v - origin[i]) / scale : v * scale + origin[i])),
    target: pose.target.map((v, i) => (inward ? (v - origin[i]) / scale : v * scale + origin[i])),
    fov: pose.fov,
  });
  const config = production.cameras.campus,
    toThree = (v) => [v[0], v[2], -v[1]],
    end = { eye: toThree(config.eye), target: toThree(config.target), fov: config.fov };
  if (reduced) return { city: start, campus: end };
  const direction = start.eye.map((v, i) => v - start.target[i]),
    length = Math.hypot(...direction),
    target = origin.map((v, i) => v + (i === 1 ? spec.targetHeightM * scale : 0));
  const gate = {
    eye: target.map((v, i) => v + (direction[i] / length) * spec.handoffDistanceM * scale),
    target,
    fov: start.fov,
  };
  if (!frame.handoff)
    return { city: poseLerp(start, gate, frame.approach), campus: map(gate, true) };
  const campus = poseLerp(map(gate, true), end, frame.settle);
  return { city: map(campus, false), campus };
}
