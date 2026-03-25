import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@/domains': path.resolve(__dirname, './app/src/domains'),
      '@/kernel': path.resolve(__dirname, './app/src/kernel'),
      '@/views': path.resolve(__dirname, './app/src/views'),
      '@/modules': path.resolve(__dirname, './app/src/modules'),
      '@/components': path.resolve(__dirname, './app/src/components'),
      '@/hooks': path.resolve(__dirname, './app/src/hooks'),
      '@/utils': path.resolve(__dirname, './app/src/utils'),
    },
  },

  // Tauri expects a fixed port will fail if that port is already in use
  server: {
    port: 5173,
    strictPort: true,
  },

  // Tauri uses a localhost server in development
  // We need to provide this information to Vite
  clearScreen: false,

  // Env variables
  envPrefix: ['VITE_', 'TAURI_'],

  build: {
    // Tauri uses Chromium on Windows and WebKit on macOS and Linux
    target: process.env.TAURI_PLATFORM == 'windows' ? 'chrome105' : 'safari13',
    // Don't minify for debug builds
    minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
    // Produce sourcemaps for debug builds
    sourcemap: !!process.env.TAURI_DEBUG,
  },
});
