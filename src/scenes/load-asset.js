// 按实际读取的字节反馈模型下载进度；沿用调用方的 fetch 与取消信号。
export async function readSceneBytes(response, onProgress) {
  if (!response.body) {
    const bytes = await response.arrayBuffer();
    onProgress(bytes.byteLength);
    return bytes;
  }

  const reader = response.body.getReader();
  const chunks = [];
  let downloaded = 0;
  let reported = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      downloaded += value.byteLength;
      // 快速本地下载合并小分片的反馈，避免每个网络分片都触发界面更新。
      if (downloaded - reported >= 256 * 1024) {
        onProgress(downloaded);
        reported = downloaded;
      }
    }
  } finally {
    reader.releaseLock();
  }

  const result = new Uint8Array(downloaded);
  let offset = 0;
  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.byteLength;
  }
  if (downloaded !== reported || downloaded === 0) onProgress(downloaded);
  return result.buffer;
}
