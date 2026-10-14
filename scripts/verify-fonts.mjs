import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { chromium, firefox, webkit } from '@playwright/test';

const root = new URL('../', import.meta.url);
const base = process.env.QA_BASE_URL ?? 'http://127.0.0.1:4321';
const coverage = JSON.parse(
  await readFile(
    new URL('design/assets/fonts/web/coverage.json', root),
    'utf8',
  ),
);
const previous = JSON.parse(
  await readFile(new URL('design/phase-4-acceptance.json', root), 'utf8'),
);
const routes = previous.scope.routes;
const original = await Promise.all(
  coverage.fonts.map(async (font, index) => {
    const bytes = await readFile(
      new URL(`design/assets/fonts/MonaSans-${font.weight}.ttf`, root),
    );
    assert.equal(
      createHash('sha256').update(bytes).digest('hex'),
      font.sourceSha256,
      'native original TTF unchanged',
    );
    for (const folder of [
      'design/assets/fonts/web',
      'public/fonts',
      'dist/fonts',
    ])
      assert.equal(
        createHash('sha256')
          .update(
            await readFile(
              new URL(`${folder}/AymanSansWeb-${font.weight}.woff2`, root),
            ),
          )
          .digest('hex'),
        font.webSha256,
        'served derivative matches checked artifact',
      );
    return {
      weight: [400, 500, 600, 700][index],
      src: `data:font/ttf;base64,${bytes.toString('base64')}`,
    };
  }),
);
const report = {
  started: new Date().toISOString(),
  base,
  scope: {
    routes,
    geometryRoutes: ['/', '/projects', '/resume'],
    widths: [320, 390, 768, 1440],
    fontFamily: coverage.family,
    comparisonFamily: 'OriginalMona',
    method:
      'Actual rendered text nodes across all19 routes are collected with their computed font sizes. Original full TTFs are loaded through FontFace data URLs; canvas.measureText compares each string at weights400/500/600/700 against the delivered subset. Maximum allowed advance-width difference is0.01px. Only browser network requests to /fonts/ count as runtime font delivery.',
  },
  hashes: {
    unchangedOriginalTTFs: original.length,
    matchingSubsetCopies: coverage.fonts.length * 3,
  },
  browsers: {},
  geometry: [],
  failures: [],
};
function fail(name, error) {
  report.failures.push({ name, message: error.message });
  console.error(`FAIL ${name}: ${error.message}`);
}
await Promise.all(
  Object.entries({ chromium, firefox, webkit }).map(async ([name, engine]) => {
    const browser = await engine.launch();
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      reducedMotion: 'reduce',
    });
    const page = await context.newPage();
    const requests = new Set();
    page.on('request', (request) => {
      if (request.url().startsWith(`${base}/fonts/`))
        requests.add(new URL(request.url()).pathname);
    });
    try {
      const samples = new Map();
      const codepoints = new Set();
      for (const route of routes) {
        await page.goto(`${base}${route}`);
        await page.evaluate(() => document.fonts.ready);
        const text = await page.evaluate(() => {
          const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
          );
          const samples = [];
          while (walker.nextNode()) {
            const node = walker.currentNode;
            const parent = node.parentElement;
            if (
              !parent ||
              ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(parent.tagName)
            )
              continue;
            const value = node.textContent.replace(/\s+/g, ' ').trim();
            if (!value) continue;
            const range = document.createRange();
            range.selectNodeContents(node);
            if (
              ![...range.getClientRects()].some(
                (rect) => rect.width > 0 && rect.height > 0,
              )
            )
              continue;
            const style = getComputedStyle(parent);
            if (style.visibility === 'hidden' || style.display === 'none')
              continue;
            samples.push({
              text: value,
              size: parseFloat(style.fontSize),
              family: style.fontFamily,
            });
          }
          return samples;
        });
        for (const sample of text) {
          for (const char of sample.text) codepoints.add(char.codePointAt(0));
          assert.ok(
            sample.family.includes(coverage.family),
            `${route}: actual text uses delivered family`,
          );
          samples.set(`${sample.size}:${sample.text}`, sample);
        }
      }
      const originalCoverage = new Set(coverage.originalCodepoints);
      const subsetCoverage = new Set(coverage.codepoints);
      const missing = [...codepoints].filter(
        (value) => originalCoverage.has(value) && !subsetCoverage.has(value),
      );
      assert.deepEqual(
        missing,
        [],
        'subset covers all actual original-supported text',
      );
      const metrics = await page.evaluate(
        async ({ originals, samples, family }) => {
          for (const original of originals) {
            const face = new FontFace('OriginalMona', `url(${original.src})`, {
              weight: `${original.weight}`,
            });
            await face.load();
            document.fonts.add(face);
          }
          await Promise.all(
            originals.map(({ weight }) =>
              document.fonts.load(`${weight} 16px "${family}"`),
            ),
          );
          const context = document.createElement('canvas').getContext('2d');
          context.fontKerning = 'normal';
          const mismatches = [];
          let comparisons = 0;
          let maximumDifference = 0;
          for (const { text, size } of samples)
            for (const { weight } of originals) {
              context.font = `${weight} ${size}px "OriginalMona", sans-serif`;
              const full = context.measureText(text).width;
              context.font = `${weight} ${size}px "${family}", sans-serif`;
              const subset = context.measureText(text).width;
              const difference = Math.abs(full - subset);
              comparisons++;
              maximumDifference = Math.max(maximumDifference, difference);
              if (difference >= 0.01)
                mismatches.push({
                  text,
                  size,
                  weight,
                  full,
                  subset,
                  difference,
                });
            }
          return { comparisons, maximumDifference, mismatches };
        },
        {
          originals: original,
          samples: [...samples.values()],
          family: coverage.family,
        },
      );
      assert.deepEqual(
        metrics.mismatches,
        [],
        'original and derivative text shaping retain matching advances',
      );
      const expectedRequests = coverage.fonts
        .map((font) => `/fonts/AymanSansWeb-${font.weight}.woff2`)
        .sort();
      assert.deepEqual(
        [...requests].sort(),
        expectedRequests,
        'only the four subset faces are requested',
      );
      report.browsers[name] = {
        version: browser.version(),
        samples: samples.size,
        actualCodepoints: codepoints.size,
        subsetSupportedActualCodepoints: [...codepoints].filter((value) =>
          originalCoverage.has(value),
        ).length,
        originalUnsupportedFallbackCodepoints: [...codepoints].filter(
          (value) => !originalCoverage.has(value),
        ),
        fontRequests: [...requests].sort(),
        ...metrics,
        passed: true,
      };
      console.log(
        `PASS ${name}: ${metrics.comparisons} advance comparisons; max delta ${metrics.maximumDifference}px`,
      );
      for (const width of report.scope.widths) {
        await page.setViewportSize({ width, height: 1000 });
        for (const route of report.scope.geometryRoutes) {
          try {
            await page.goto(`${base}${route}`);
            await page.evaluate(() => document.fonts.ready);
            const geometry = await page.evaluate(() => ({
              overflow: document.documentElement.scrollWidth - innerWidth,
              h1: document.querySelector('h1').getBoundingClientRect().toJSON(),
              hero: document
                .querySelector('.hero')
                ?.getBoundingClientRect()
                .toJSON(),
              portrait: document
                .querySelector('.hero-portrait')
                ?.getBoundingClientRect()
                .toJSON(),
              stack: document
                .querySelector('.hero-stack')
                ?.getBoundingClientRect()
                .toJSON(),
            }));
            assert.equal(
              geometry.overflow,
              0,
              'font subset keeps text inside viewport',
            );
            if (route === '/' && width !== 320) {
              const expected = {
                390: {
                  x: 65,
                  y: 564,
                  width: 260,
                  height: 346.65625,
                  stackY: 942.65625,
                },
                768: { x: 234, y: 577, width: 300, height: 400, stackY: 1015 },
                1440: { x: 962, y: 164, width: 360, height: 537, stackY: 677 },
              }[width];
              for (const field of ['x', 'y', 'width', 'height'])
                assert.ok(
                  Math.abs(geometry.portrait[field] - expected[field]) <= 1,
                  `portrait ${field} retains original-font position`,
                );
              assert.ok(
                Math.abs(geometry.stack.y - expected.stackY) <= 1,
                'technology labels retain original-font position',
              );
            }
            report.geometry.push({
              browser: name,
              width,
              route,
              ...geometry,
              passed: true,
            });
          } catch (error) {
            fail(`${name} ${width}px ${route}`, error);
          }
        }
      }
    } catch (error) {
      fail(`${name} font comparison`, error);
    } finally {
      await context.close();
      await browser.close();
    }
  }),
);
report.finished = new Date().toISOString();
report.summary = {
  browsers: Object.keys(report.browsers).length,
  advanceComparisons: Object.values(report.browsers).reduce(
    (sum, browser) => sum + browser.comparisons,
    0,
  ),
  maximumAdvanceDifferencePx: Math.max(
    ...Object.values(report.browsers).map(
      (browser) => browser.maximumDifference,
    ),
  ),
  geometryChecks: report.geometry.length,
  unchangedOriginalTTFs: original.length,
  failures: report.failures.length,
};
for (const path of ['output/font-acceptance.json', 'design/phase-4-fonts.json'])
  await writeFile(new URL(path, root), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report.summary, null, 2));
if (report.failures.length) process.exitCode = 1;
