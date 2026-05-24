import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const viteHost = process.env.VITE_HOST || '0.0.0.0'
const vitePort = Number(process.env.VITE_PORT || '5173')

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: viteHost,
    port: vitePort
  }
})
