import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Все запросы /api/* фронтенд отправляет на бэкенд FastAPI (порт 8000)
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } },
})
