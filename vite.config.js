import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import Pages from 'vite-plugin-pages'
import path from 'path' 

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, __dirname, '')
  const backendUrl = env.VITE_DEV_BACKEND_URL || 'http://127.0.0.1:8000'

  return {
    plugins: [
      vue(),
      Pages({
        dirs: 'src/pages',
        extensions: ['vue'],
        importMode: 'sync',
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@core': path.resolve(__dirname, 'src/core'),
        // Ne pas aliaser path ici
      },
    },
    server: {
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
        },
        '/socket.io': {
          target: backendUrl,
          changeOrigin: true,
          ws: true,
        },
      },
    },
    optimizeDeps: {
      include: ['postcss', 'source-map-js'],
    },
  }
})
