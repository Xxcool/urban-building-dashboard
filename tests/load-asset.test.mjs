// 下载进度不能改变模型字节或吞掉取消和网络异常。
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readSceneBytes } from '../src/scenes/load-asset.js';

test('分片读取保留全部模型字节，进度来自真实读取量', async () => {
  const a = new Uint8Array(300_000).fill(7);
  const b = new Uint8Array([9, 10, 11]);
  const progress = [];
  const response = new Response(
    new ReadableStream({
      start(controller) {
        controller.enqueue(a);
        controller.enqueue(b);
        controller.close();
      },
    }),
  );
  const result = new Uint8Array(await readSceneBytes(response, (value) => progress.push(value)));
  assert.equal(result.length, a.length + b.length);
  assert.deepEqual(result.slice(0, a.length), a);
  assert.deepEqual(result.slice(a.length), b);
  assert.deepEqual(progress, [a.length, a.length + b.length]);
  assert.equal(response.body.locked, false);
});

test('空响应保留空字节结果，后续模型校验负责拒绝无效内容', async () => {
  const progress = [];
  const result = await readSceneBytes(new Response(null), (value) => progress.push(value));
  assert.equal(result.byteLength, 0);
  assert.deepEqual(progress, [0]);
});

test('读取中断继续抛出原错误，并释放读取锁', async () => {
  const error = new DOMException('The operation was aborted', 'AbortError');
  const response = new Response(
    new ReadableStream({
      pull(controller) {
        controller.error(error);
      },
    }),
  );
  await assert.rejects(
    readSceneBytes(response, () => {}),
    (reason) => reason === error,
  );
  assert.equal(response.body.locked, false);
});
