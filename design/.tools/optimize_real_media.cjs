// Responsive copies only; originals and portrait appearance remain unchanged.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const sharp = require('C:/Users/sigma/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root = path.resolve(__dirname, '../..');
const design = path.join(root, 'design');
const digest = buffer => crypto.createHash('sha256').update(buffer).digest('hex');

(async () => {
  const captures = JSON.parse(await fs.readFile(path.join(design, 'capture-manifest.json'), 'utf8'));
  const records = [{
    slug: 'ayman-portrait', path: 'design/assets/personal/ayman-original.jpg',
    classification: 'original-personal-photograph',
    permission: 'Direction A explicitly selected with this original portfolio photograph.',
    alt: 'Ayman at a programming competition, photographed outdoors.',
    intendedRoutes: ['/', '/about']
  }, ...captures.map(c => ({
    slug: c.assetKey || c.project, path: c.path, classification: c.classification,
    source: c.source, permission: c.use,
    alt: c.caption, intendedRoutes: ['/projects', '/projects/' + c.project]
  }))];
  const output = path.join(design, 'assets/selected-web');
  await fs.mkdir(output, { recursive: true });
  for (const item of records) {
    const source = await fs.readFile(path.join(root, item.path));
    const metadata = await sharp(source).metadata();
    Object.assign(item, { width: metadata.width, height: metadata.height, sha256: digest(source), variants: [] });
    for (const width of [480, 960, 1440]) {
      const filename = item.slug + '-' + width + '.webp';
      const bytes = await sharp(source).rotate().resize({ width, withoutEnlargement: true }).webp({ quality: 85 }).toBuffer();
      await fs.writeFile(path.join(output, filename), bytes);
      const actual = await sharp(bytes).metadata();
      item.variants.push({ path: 'design/assets/selected-web/' + filename, width: actual.width, height: actual.height, bytes: bytes.length, sha256: digest(bytes) });
    }
  }
  await fs.writeFile(path.join(design, 'selected-media-manifest.json'), JSON.stringify({ direction: 'A', selected: '2026-10-14', images: records }, null, 2));
  const edited = records.filter(item => item.classification === 'ai-edited-application-demo').length;
  console.log(`${records.length} approved assets preserved (${records.length - edited} genuine, ${edited} AI-edited demo); ${records.length * 3} responsive WebP copies created.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
