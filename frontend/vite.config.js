import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 6666,
    host: '0.0.0.0',  // 允许外网访问
    proxy: {
      '/api': {
        target: 'http://localhost:6667',
        changeOrigin: true
      }
    }
  }
})

