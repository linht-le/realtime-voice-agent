import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const BACKEND_URL = process.env.VITE_BACKEND_URL || 'http://localhost:8000'

const createProxy = (paths) => {
  const proxy = {}
  paths.forEach((path) => {
    if (path === '/ws') {
      proxy[path] = {
        target: BACKEND_URL.replace('http', 'ws'),
        ws: true,
        changeOrigin: true
      }
    } else {
      proxy[path] = {
        target: BACKEND_URL,
        changeOrigin: true
      }
    }
  })
  return proxy
}

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: createProxy(['/ws', '/api', '/settings', '/documents', '/prompts', '/tools'])
  }
})
