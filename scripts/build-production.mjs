import { execFile } from 'node:child_process';
import { writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { promisify } from 'node:util';

const root = resolve(import.meta.dirname, '..');
const output = 'output/production-dist';
const execute = promisify(execFile);
const options = {
  cwd: root,
  env: { ...process.env, PUBLIC_SITE_INDEXABLE: 'true' },
  windowsHide: true,
  maxBuffer: 4 * 1024 * 1024,
};

for (const arguments_ of [
  [resolve(root, 'scripts/prepare-content.mjs')],
  [
    resolve(root, 'node_modules/astro/bin/astro.mjs'),
    'build',
    '--site',
    'https://aymanashraf.me',
    '--outDir',
    output,
  ],
]) {
  const { stdout, stderr } = await execute(
    process.execPath,
    arguments_,
    options,
  );
  process.stdout.write(stdout);
  process.stderr.write(stderr);
}

await writeFile(
  resolve(root, output, '_redirects'),
  '/portfolio-landing-page / 301\n/portfolio-landing-page/ / 301\n',
);
console.log('Prepared indexable production build for https://aymanashraf.me');
