// 加载由规划源派生的配置并启动应用；失败明确提示，不显示伪造默认数据。
import { createApp } from 'vue';
import App from './App.vue';
import './styles/main.css';
try {
  const response = await fetch('./assets/runtime.json');
  if (!response.ok) throw new Error('配置读取失败');
  const config = await response.json();
  createApp(App, { config }).mount('#app');
} catch (error) {
  console.error(error);
  document.querySelector('#app').textContent = '展示配置载入失败，请检查本地资源。';
}
