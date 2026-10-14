import { execFile } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { promisify } from 'node:util';

const root = resolve(import.meta.dirname, '..');
const config = JSON.parse(
  await readFile(resolve(root, 'wrangler.json'), 'utf8'),
);
const origin = `https://review.${config.name}.pages.dev`;
const execute = promisify(execFile);
const options = {
  cwd: root,
  env: { ...process.env, PUBLIC_SITE_INDEXABLE: 'false' },
  windowsHide: true,
  maxBuffer: 4 * 1024 * 1024,
};

for (const arguments_ of [
  [resolve(root, 'scripts/prepare-content.mjs')],
  [
    resolve(root, 'node_modules/astro/bin/astro.mjs'),
    'build',
    '--site',
    origin,
    '--outDir',
    config.pages_build_output_dir,
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
  resolve(root, config.pages_build_output_dir, '_headers'),
  '/*\n  X-Robots-Tag: noindex, nofollow\n',
);
console.log(`Prepared isolated noindex preview for ${origin}`);
