// 本地静态大屏构建：Vue模板编译随包交付，资产全部从本站加载。
import { defineConfig } from 'vite';
export default defineConfig({resolve:{alias:{vue:'vue/dist/vue.esm-bundler.js'}},define:{__VUE_OPTIONS_API__:true,__VUE_PROD_DEVTOOLS__:false,__VUE_PROD_HYDRATION_MISMATCH_DETAILS__:false},base:'./',server:{watch:{usePolling:true,interval:500}},build:{chunkSizeWarningLimit:900}});
