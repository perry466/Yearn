import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // 监听 0.0.0.0，允许局域网其他设备访问
    port: 5173,
    // 允许访问的主机名（Vite 6 默认拦截非白名单主机，局域网 .local / IP 访问需放行）
    // 若要按 IP 访问，把 allowedHosts 设为 true 可放行所有主机；生产部署建议改用 build + nginx
    allowedHosts: ['roc-ubuntu.local', 'localhost', '127.0.0.1'],
    // 后端 API 代理
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
