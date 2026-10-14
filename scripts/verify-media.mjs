import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { chromium, firefox, webkit } from '@playwright/test';

const base = process.env.QA_BASE_URL ?? 'http://127.0.0.1:4321';
const root = new URL('../', import.meta.url);
const output = new URL('output/acceptance-screenshots/', root);
await mkdir(output, { recursive: true });
const selected = JSON.parse(
  await readFile(new URL('design/selected-media-manifest.json', root), 'utf8'),
);
const report = {
  started: new Date().toISOString(),
  base,
  scope: {
    browsers: ['chromium', 'firefox', 'webkit'],
    widths: [390, 768, 1440],
    routes: ['/', '/projects', '/projects/helixtra'],
    modes: ['avif', 'webp-fallback'],
    fallbackMethod:
      'For fallback contexts only, a real navigation response is fetched and its optional AVIF source elements removed before HTML reaches the browser parser. Image responses remain real and unmodified. This simulates the optional codec being unavailable.',
  },
  checks: [],
  codecSupport: {},
  sourceHashes: [],
  screenshots: [],
  failures: [],
};
function fail(name, error) {
  report.failures.push({ name, message: error.message });
  console.error(`FAIL ${name}: ${error.message}`);
}
const hash = (bytes) => createHash('sha256').update(bytes).digest('hex');
for (const image of selected.images) {
  try {
    const expected = image.sha256;
    const sourceHash = hash(await readFile(new URL(image.path, root)));
    assert.equal(sourceHash, expected, `${image.slug}: approved original hash`);
    const name = image.path.split('/').at(-1);
    for (const folder of ['public', 'dist'])
      assert.equal(
        hash(
          await readFile(new URL(`${folder}/media/originals/${name}`, root)),
        ),
        expected,
        `${folder} original matches approved source`,
      );
    for (const variant of image.variants)
      for (const folder of ['public', 'dist'])
        assert.equal(
          hash(
            await readFile(
              new URL(
                `${folder}/media/${variant.path.split('/').at(-1)}`,
                root,
              ),
            ),
          ),
          variant.sha256,
          `${folder} WebP remains unchanged`,
        );
    report.sourceHashes.push({
      slug: image.slug,
      originalSha256: sourceHash,
      unchangedWebPVariants: image.variants.length,
      passed: true,
    });
  } catch (error) {
    fail(`approved media hash ${image.slug}`, error);
  }
}

await Promise.all(
  Object.entries({ chromium, firefox, webkit }).map(async ([name, engine]) => {
    const browser = await engine.launch();
    let avifSupported;
    try {
      for (const mode of report.scope.modes) {
        const context = await browser.newContext({
          viewport: { width: 390, height: 1000 },
          reducedMotion: 'reduce',
        });
        try {
          if (mode === 'webp-fallback')
            await context.route('**/*', async (route) => {
              if (!route.request().isNavigationRequest())
                return route.continue();
              const response = await route.fetch();
              const html = await response.text();
              return route.fulfill({
                response,
                body: html.replace(
                  /<source\b[^>]*\btype=["']image\/avif["'][^>]*>/gi,
                  '',
                ),
              });
            });
          const page = await context.newPage();
          page.setDefaultTimeout(10000);
          for (const width of report.scope.widths) {
            await page.setViewportSize({ width, height: 1000 });
            for (const route of report.scope.routes) {
              const label = `${name} ${mode} ${width}px ${route}`;
              try {
                const response = await page.goto(`${base}${route}`);
                assert.ok([200, 304].includes(response.status()));
                if (avifSupported === undefined) {
                  avifSupported = await page.evaluate(async (src) => {
                    const probe = new Image();
                    probe.src = src;
                    try {
                      await probe.decode();
                      return probe.naturalWidth > 0;
                    } catch {
                      return false;
                    }
                  }, `${base}/media/ayman-portrait-480.avif`);
                  report.codecSupport[name] = {
                    avif: avifSupported,
                    browserVersion: browser.version(),
                    probe:
                      'Actual AVIF response decoded with Image.decode(); unsupported engines must naturally select WebP.',
                  };
                }
                await page.evaluate(() => document.fonts.ready);
                for (const image of await page
                  .locator('.project-image img[src]')
                  .all()) {
                  await image.scrollIntoViewIfNeeded();
                  await image.evaluate((el) => el.decode());
                }
                await page.evaluate(() => scrollTo(0, 0));
                const facts = await page.evaluate(() => ({
                  overflow: document.documentElement.scrollWidth - innerWidth,
                  images: [
                    ...document.querySelectorAll('.project-image img'),
                  ].map((img) => {
                    const rect = img.getBoundingClientRect();
                    const stage = img
                      .closest('.media-stage')
                      .getBoundingClientRect();
                    return {
                      currentSrc: img.currentSrc,
                      alt: img.alt,
                      loaded: img.complete && img.naturalWidth > 0,
                      avifEligible: /\/media\/(ayman-portrait|helixtra)-/.test(
                        img.src,
                      ),
                      imageBox: rect.toJSON(),
                      stageBox: stage.toJSON(),
                      objectFit: getComputedStyle(img).objectFit,
                    };
                  }),
                }));
                assert.equal(
                  facts.overflow,
                  0,
                  'picture wrapper keeps page within viewport',
                );
                for (const image of facts.images) {
                  assert.equal(
                    image.loaded,
                    true,
                    `${image.alt}: image decodes`,
                  );
                  assert.match(
                    image.currentSrc,
                    image.avifEligible && mode === 'avif' && avifSupported
                      ? /\.avif$/
                      : /\.webp$/,
                    `${image.alt}: expected format selected`,
                  );
                  for (const side of ['x', 'y', 'width', 'height'])
                    assert.ok(
                      Math.abs(image.imageBox[side] - image.stageBox[side]) <=
                        1,
                      `${image.alt}: image ${side} remains inside unchanged stage geometry`,
                    );
                  assert.equal(
                    image.objectFit,
                    /Ayman at/.test(image.alt) ? 'cover' : 'contain',
                  );
                }
                if (route === '/') {
                  const hero = await page.locator('.hero').evaluate((el) => {
                    const portrait = el
                      .querySelector('.hero-portrait')
                      .getBoundingClientRect();
                    const stack = el
                      .querySelector('.hero-stack')
                      .getBoundingClientRect();
                    const box = el.getBoundingClientRect();
                    const label =
                      [...el.querySelectorAll('.hero-stack span')].find(
                        (span) => span.textContent.trim() === 'Cloudflare',
                      ) ??
                      [...el.querySelectorAll('.hero-stack li')].find(
                        (li) => li.textContent.trim() === 'Cloudflare',
                      );
                    const range = document.createRange();
                    range.selectNodeContents(label);
                    const text = range.getBoundingClientRect();
                    return {
                      hero: box.toJSON(),
                      portrait: portrait.toJSON(),
                      stack: stack.toJSON(),
                      cloudflare: text.toJSON(),
                    };
                  });
                  const expected = {
                    390: {
                      x: 65,
                      y: 564,
                      width: 260,
                      height: 346.65625,
                      stackY: 942.65625,
                    },
                    768: {
                      x: 234,
                      y: 577,
                      width: 300,
                      height: 400,
                      stackY: 1015,
                    },
                    1440: {
                      x: 962,
                      y: 164,
                      width: 360,
                      height: 537,
                      stackY: 677,
                    },
                  }[width];
                  for (const side of ['x', 'y', 'width', 'height'])
                    assert.ok(
                      Math.abs(hero.portrait[side] - expected[side]) <= 1,
                      `portrait ${side} retains pre-picture geometry`,
                    );
                  assert.ok(
                    Math.abs(hero.stack.y - expected.stackY) <= 1,
                    'stack retains approved spacing',
                  );
                  for (const bounds of [hero.hero, hero.stack])
                    assert.ok(
                      hero.cloudflare.left >= bounds.left - 1 &&
                        hero.cloudflare.right <= bounds.right + 1 &&
                        hero.cloudflare.top >= bounds.top - 1 &&
                        hero.cloudflare.bottom <= bounds.bottom + 1,
                      'complete Cloudflare text fits hero and stack',
                    );
                  facts.hero = hero;
                  if (width === 390 && mode === 'avif') {
                    for (const [selector, suffix] of [
                      ['.hero', 'hero-complete'],
                      ['.hero-stack', 'stack-complete'],
                    ]) {
                      const target = new URL(
                        `${name}-390-${suffix}.png`,
                        output,
                      );
                      await page
                        .locator(selector)
                        .screenshot({ path: fileURLToPath(target) });
                      report.screenshots.push(fileURLToPath(target));
                    }
                  }
                }
                report.checks.push({
                  browser: name,
                  mode,
                  width,
                  route,
                  passed: true,
                  ...facts,
                });
                console.log(`PASS ${label}`);
              } catch (error) {
                fail(label, error);
              }
            }
          }
        } finally {
          await context.close();
        }
      }
    } finally {
      await browser.close();
    }
  }),
);
report.finished = new Date().toISOString();
report.summary = {
  browserChecks: report.checks.length,
  originalHashes: report.sourceHashes.length,
  unchangedWebPVariants: report.sourceHashes.reduce(
    (sum, item) => sum + item.unchangedWebPVariants,
    0,
  ),
  failures: report.failures.length,
};
for (const path of [
  'output/media-acceptance.json',
  'design/phase-4-media.json',
])
  await writeFile(new URL(path, root), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report.summary, null, 2));
if (report.failures.length) process.exitCode = 1;
