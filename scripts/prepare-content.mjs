import {
  readFile,
  writeFile,
  mkdir,
  copyFile,
  readdir,
  unlink,
} from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { format } from 'prettier';
import sharp from 'sharp';

const root = resolve(import.meta.dirname, '..');
const readJson = async (name) =>
  JSON.parse(await readFile(resolve(root, name), 'utf8'));
const content = await readJson('design/screen-content.json');
const selected = await readJson('design/selected-media-manifest.json');
const allowed = [
  'slug',
  'title',
  'category',
  'kind',
  'status',
  'summary',
  'overview',
  'role',
  'features',
  'challenge',
  'engineering',
  'stack',
  'validation',
  'live',
  'github',
  'capture',
  'caption',
];
const projects = content.projects.map((project, order) => ({
  ...Object.fromEntries(allowed.map((key) => [key, project[key] ?? null])),
  id: project.slug,
  order,
  gallery: project.gallery ?? [],
  demo: project.slug === 'blitzchatbot',
}));

async function copyAsset(source, destination) {
  const target = resolve(root, 'public', destination);
  await mkdir(resolve(target, '..'), { recursive: true });
  await copyFile(resolve(root, source), target);
}

const media = {};
const approvedMediaPaths = new Set();
const avifSlugs = new Set(['ayman-portrait', 'helixtra']);
for (const image of selected.images) {
  const original = basename(image.path);
  await copyAsset(image.path, `media/originals/${original}`);
  approvedMediaPaths.add(`media/originals/${original}`);
  const variants = [];
  for (const variant of image.variants) {
    const filename = basename(variant.path);
    await copyAsset(variant.path, `media/${filename}`);
    approvedMediaPaths.add(`media/${filename}`);
    variants.push({ src: `/media/${filename}`, width: variant.width });
  }
  const avifVariants = [];
  if (avifSlugs.has(image.slug)) {
    for (const width of [480, 640, 960, 1440]) {
      const filename = `${image.slug}-${width}.avif`;
      await sharp(resolve(root, image.path))
        .resize({ width, withoutEnlargement: true })
        .avif({ quality: 60, effort: 5 })
        .toFile(resolve(root, 'public/media', filename));
      approvedMediaPaths.add(`media/${filename}`);
      avifVariants.push({ src: `/media/${filename}`, width });
    }
  }
  media[image.slug] = {
    original: `/media/originals/${original}`,
    width: image.width,
    height: image.height,
    alt: image.alt,
    classification: image.classification,
    variants,
    avifVariants,
  };
}
for (const folder of ['media', 'media/originals']) {
  const entries = await readdir(resolve(root, 'public', folder), {
    withFileTypes: true,
  });
  for (const entry of entries) {
    const relativePath = `${folder}/${entry.name}`;
    if (entry.isFile() && !approvedMediaPaths.has(relativePath)) {
      await unlink(resolve(root, 'public', relativePath));
    }
  }
}
const fontWeights = ['Regular', 'Medium', 'SemiBold', 'Bold'];
const fontCoverage = await readJson('design/assets/fonts/web/coverage.json');
const availableCodepoints = new Set(fontCoverage.codepoints);
const originalCodepoints = new Set(fontCoverage.originalCodepoints);
const textSources = [JSON.stringify(projects)];
for (const filename of await readdir(resolve(root, 'src'), {
  recursive: true,
})) {
  if (/\.(astro|ts)$/.test(filename)) {
    textSources.push(await readFile(resolve(root, 'src', filename), 'utf8'));
  }
}
const missingCodepoints = new Set(
  [...textSources.join('')]
    .map((character) => character.codePointAt(0))
    .filter(
      (codepoint) =>
        originalCodepoints.has(codepoint) &&
        !availableCodepoints.has(codepoint),
    ),
);
if (missingCodepoints.size) {
  throw new Error(
    `Web font coverage missing: ${[...missingCodepoints].map((codepoint) => `U+${codepoint.toString(16)}`).join(', ')}. Regenerate design/assets/fonts/web with design/.tools/prepare_web_fonts.py.`,
  );
}
await mkdir(resolve(root, 'public/fonts'), { recursive: true });
for (const weight of fontWeights) {
  const filename = `AymanSansWeb-${weight}.woff2`;
  await copyAsset(`design/assets/fonts/web/${filename}`, `fonts/${filename}`);
}
await copyAsset('design/assets/fonts/OFL.txt', 'fonts/OFL.txt');
for (const filename of await readdir(resolve(root, 'public/fonts'))) {
  if (
    fontWeights.some((weight) =>
      ['ttf', 'woff2'].some(
        (extension) => filename === `MonaSans-${weight}.${extension}`,
      ),
    )
  ) {
    await unlink(resolve(root, 'public/fonts', filename));
  }
}
for (const filename of await readdir(resolve(root, 'design/assets/icons'))) {
  if (/\.(svg|txt)$/.test(filename) || filename === 'LICENSE') {
    await copyAsset(`design/assets/icons/${filename}`, `icons/${filename}`);
  }
}
await copyAsset('Ayman Kamel - CV.pdf', 'ayman-ashraf-mounir-cv.pdf');
await copyAsset('design/screens/home-preview-1440.png', 'og.png');
await mkdir(resolve(root, 'src/content'), { recursive: true });
await mkdir(resolve(root, 'src/data'), { recursive: true });
await writeFile(
  resolve(root, 'src/content/projects.json'),
  await format(JSON.stringify(projects), { parser: 'json' }),
);
await writeFile(
  resolve(root, 'src/data/media.json'),
  await format(JSON.stringify(media), { parser: 'json' }),
);
console.log(
  `Prepared ${projects.length} approved projects and ${selected.images.length} media assets.`,
);
