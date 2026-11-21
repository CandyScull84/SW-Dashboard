import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/merge-requests": "http://localhost:8088",
      "/push-events": "http://localhost:8088",
      "/failing-pipelines": "http://localhost:8088",
      "/team-status": "http://localhost:8088",
      "/active-projects": "http://localhost:8088"
    }
  }
})
