import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import fs from 'fs';
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    https: {
      key: fs.readFileSync('../ssl/localhost-key.pem'),
      cert: fs.readFileSync('../ssl/localhost.pem'),
    },
  },
  plugins: [svelte()],
  resolve: {
    alias: {
      $lib: path.resolve("./src/lib"),
    },
  },
})
