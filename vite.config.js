// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Pages from 'vite-plugin-pages'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    Pages({
      dirs: 'src/pages', // Le répertoire où se trouvent les pages
      extensions: ['vue'], // Extensions de fichiers à considérer
      importMode: 'sync', // Import synchrone des pages
    }),

  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),  // Ceci lie @ à src/
      '@core': path.resolve(__dirname, 'src/core'), 
    },
  },
})
