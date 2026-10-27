// 覆盖四向避让、窄窗口边界和方向稳定性，验证浮层选择而非固定右上角。
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { placeFloatingCard } from '../src/utils/floating-card.js';
const base = {
  anchor: { left: 480, top: 380, width: 60, height: 40 },
  card: { width: 320, height: 270 },
  bounds: { width: 1200, height: 900 },
};
test('相邻方向被遮挡时选其他无碰撞位置', () => {
  const p = placeFloatingCard({
    ...base,
    obstacles: [{ left: 550, top: 100, width: 630, height: 700, weight: 20 }],
  });
  assert.equal(p.obstruction, 0);
  assert.ok(p.left + 320 <= 550);
});
test('上下左右角落与窄窗口都保持卡片在视口内', () => {
  for (const [x, y] of [
    [0, 0],
    [850, 0],
    [0, 680],
    [850, 680],
  ]) {
    const p = placeFloatingCard({
      ...base,
      bounds: { width: 940, height: 720 },
      anchor: { left: x, top: y, width: 60, height: 40 },
    });
    assert.ok(p.left >= 18 && p.top >= 18);
    assert.ok(p.left + 320 <= 922 && p.top + 270 <= 702);
  }
});
test('原方向仍可用时保持稳定，新遮挡优先消除', () => {
  const first = placeFloatingCard({ ...base, previous: { side: 'left' } });
  assert.equal(first.side, 'left');
  const second = placeFloatingCard({
    ...base,
    previous: first,
    obstacles: [{ left: 80, top: 100, width: 380, height: 700 }],
  });
  assert.notEqual(second.side, 'left');
  assert.equal(second.obstruction, 0);
});
test('四向都拥挤时搜索障碍边缘形成的内部空位', () => {
  const obstacles = [
    { left: 0, top: 0, width: 300, height: 720 },
    { left: 940, top: 0, width: 260, height: 720 },
    { left: 300, top: 0, width: 640, height: 200 },
    { left: 300, top: 600, width: 640, height: 300 },
  ];
  const p = placeFloatingCard({ ...base, obstacles });
  assert.equal(p.obstruction, 0);
  assert.ok(p.left >= 300 && p.left + 320 <= 940 && p.top >= 200 && p.top + 270 <= 600);
});
