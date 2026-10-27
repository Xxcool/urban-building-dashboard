// Vue 单文件组件在构建时编译，公共资产按部署基础路径加载。
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  base: './',
  server: { watch: { usePolling: true, interval: 500 } },
  build: { chunkSizeWarningLimit: 900 },
});
