import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'index.html')
      },
      output: {
        entryFileNames: 'popup.js',
        chunkFileNames: 'popup-[hash].js',
        assetFileNames: 'popup-[hash].[ext]'
      }
    }
  }
})
