import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/diaryChat': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@services': '/src/services',
    }
  }
})