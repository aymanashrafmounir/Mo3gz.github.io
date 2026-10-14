import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://aymanashraf.me',
  output: 'static',
  build: { inlineStylesheets: 'always' },
  trailingSlash: 'never',
  redirects: { '/portfolio-landing-page': '/' },
  vite: { plugins: [tailwindcss()] },
  devToolbar: { enabled: false },
});
