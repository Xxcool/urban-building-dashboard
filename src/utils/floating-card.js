// 信息浮层围绕对象选位：避开标签与操作区，在遮挡相近时保留原方向，降低镜头运动中的跳动。
const overlap = (a, b) =>
  Math.max(0, Math.min(a.left + a.width, b.left + b.width) - Math.max(a.left, b.left)) *
  Math.max(0, Math.min(a.top + a.height, b.top + b.height) - Math.max(a.top, b.top));
export function placeFloatingCard({
  anchor,
  card,
  bounds,
  obstacles = [],
  previous = null,
  gap = 20,
}) {
  const { width: w, height: h } = card,
    margin = 18,
    maxX = Math.max(margin, bounds.width - w - margin),
    maxY = Math.max(margin, bounds.height - h - margin);
  const x = anchor.left + anchor.width / 2,
    y = anchor.top + anchor.height / 2;
  const candidates = [
    { side: 'right', left: anchor.left + anchor.width + gap, top: y - h / 2 },
    { side: 'left', left: anchor.left - w - gap, top: y - h / 2 },
    { side: 'top', left: x - w / 2, top: anchor.top - h - gap },
    { side: 'bottom', left: x - w / 2, top: anchor.top + anchor.height + gap },
    ...[-1, 1].flatMap((dx) =>
      [-1, 1].map((dy) => ({
        side: dx < 0 ? 'left' : 'right',
        left: dx < 0 ? anchor.left - w - gap : anchor.left + anchor.width + gap,
        top: dy < 0 ? anchor.top - h - gap : anchor.top + anchor.height + gap,
      })),
    ),
  ];
  // 周边都拥挤时，补充视口边缘的可用槽位；候选仍需参与相同碰撞评分。
  for (const left of [margin, maxX])
    for (let top = margin; top <= maxY; top += Math.max(80, h / 2))
      candidates.push({ side: left === margin ? 'left' : 'right', left, top });
  const blocks = [{ ...anchor, weight: 8 }, ...obstacles];
  // 当四向候选都碰撞时，按障碍物边缘构建空位候选，不把“遮挡最少”当成“无遮挡”。
  const xs = new Set([margin, maxX]),
    ys = new Set([margin, maxY]);
  for (const b of blocks) {
    xs.add(Math.max(margin, Math.min(maxX, b.left - w - 12)));
    xs.add(Math.max(margin, Math.min(maxX, b.left + b.width + 12)));
    ys.add(Math.max(margin, Math.min(maxY, b.top - h - 12)));
    ys.add(Math.max(margin, Math.min(maxY, b.top + b.height + 12)));
  }
  for (const left of xs)
    for (const top of ys) {
      const dx = left + w / 2 - x,
        dy = top + h / 2 - y;
      candidates.push({
        side: Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : dy > 0 ? 'bottom' : 'top',
        left,
        top,
      });
    }
  const scored = candidates
    .map((item) => {
      const pos = {
        ...item,
        left: Math.max(margin, Math.min(maxX, item.left)),
        top: Math.max(margin, Math.min(maxY, item.top)),
        width: w,
        height: h,
      };
      const obstruction = blocks.reduce((sum, b) => sum + overlap(pos, b) * (b.weight ?? 4), 0);
      const dx = Math.max(pos.left - x, 0, x - pos.left - w),
        dy = Math.max(pos.top - y, 0, y - pos.top - h),
        distance = Math.hypot(dx, dy);
      const switching = previous && previous.side !== pos.side ? 55 : 0;
      return { ...pos, obstruction, score: obstruction * 100 + distance + switching };
    })
    .sort((a, b) => a.score - b.score);
  const best = scored[0];
  let start, end;
  // 连线从标签边缘连接到卡片边缘，不穿过信息正文。
  if (best.left >= anchor.left + anchor.width) {
    start = [anchor.left + anchor.width, y];
    end = [best.left, Math.max(best.top + 24, Math.min(best.top + h - 24, y))];
  } else if (best.left + w <= anchor.left) {
    start = [anchor.left, y];
    end = [best.left + w, Math.max(best.top + 24, Math.min(best.top + h - 24, y))];
  } else if (best.top >= anchor.top + anchor.height) {
    start = [x, anchor.top + anchor.height];
    end = [Math.max(best.left + 24, Math.min(best.left + w - 24, x)), best.top];
  } else {
    start = [x, anchor.top];
    end = [Math.max(best.left + 24, Math.min(best.left + w - 24, x)), best.top + h];
  }
  return {
    left: Math.round(best.left),
    top: Math.round(best.top),
    side: best.side,
    obstruction: best.obstruction,
    path: `M${start[0]},${start[1]} L${end[0]},${end[1]}`,
  };
}

// 将界面真实尺寸归一到场景逻辑坐标，适用于等比画布和宽屏；无需按固定1920像素猜位置。
export function measureFloatingCard(host, card, label, previous, extraObstacles = []) {
  if (!host || !card || !label || label.hidden) return null;
  const rect = host.getBoundingClientRect(),
    scale = rect.width / host.clientWidth;
  const box = (element, pad = 0) => {
    const b = element.getBoundingClientRect();
    return {
      left: (b.left - rect.left) / scale - pad,
      top: (b.top - rect.top) / scale - pad,
      width: b.width / scale + pad * 2,
      height: b.height / scale + pad * 2,
    };
  };
  const anchor = box(label, 6),
    obstacles = [...host.querySelectorAll('.labels button')]
      .filter((node) => node !== label && !node.hidden)
      .map((node) => box(node, 8));
  obstacles.push(...extraObstacles);
  const dashboard = host.closest('.dashboard');
  for (const node of dashboard.querySelectorAll(
    '.scene-actions,.layer-tabs,.settings-panel,.city-legend,.city-disclaimer,.gesture-hint,.diagnostics',
  )) {
    if (!node.getClientRects().length) continue;
    obstacles.push({ ...box(node, 12), weight: 20 });
  }
  return placeFloatingCard({
    anchor,
    card: { width: card.offsetWidth, height: card.offsetHeight },
    bounds: { width: host.clientWidth, height: host.clientHeight },
    obstacles,
    previous,
  });
}
