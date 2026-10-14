import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium, firefox, expect } from '@playwright/test';

const root = fileURLToPath(new URL('../', import.meta.url));
const base =
  process.env.QA_BASE_URL ??
  'https://review.ayman-portfolio-v2-preview.pages.dev';
const immutable =
  process.env.QA_IMMUTABLE_URL ??
  'https://14a3e489.ayman-portfolio-v2-preview.pages.dev';
const build = path.resolve(
  root,
  process.env.QA_BUILD_DIR ?? 'output/preview-dist',
);
const output = path.join(root, 'output/phase5');
await mkdir(output, { recursive: true });
const report = {
  started: new Date().toISOString(),
  base,
  immutable,
  buildDirectory: path.relative(root, build),
  scope:
    'Public HTTPS Pages preview. No deployment, production domain, source content or approved design changes.',
  browsers: {},
  assets: [],
  http: [],
  routes: [],
  interactions: [],
  screenshots: [],
  failures: [],
  limitations: [
    'Automated desktop browser engines with emulated viewport widths; no physical devices or OS screen readers.',
    'Focused deployed-host acceptance, not a repeat of the 627-observation local matrix or a field Web Vitals measurement.',
    'Pattern and inaccessible-path checks are not an exhaustive security audit.',
  ],
};
const sha = (value) => createHash('sha256').update(value).digest('hex');
async function scenario(name, run) {
  try {
    const details = await run();
    report.interactions.push({ name, passed: true, ...details });
    console.log(`PASS ${name}`);
  } catch (error) {
    report.failures.push({ name, message: error.message });
    console.error(`FAIL ${name}: ${error.message}`);
  }
}
async function walk(directory) {
  return (
    await Promise.all(
      (await readdir(directory, { withFileTypes: true })).map((entry) => {
        const target = path.join(directory, entry.name);
        return entry.isDirectory() ? walk(target) : [target];
      }),
    )
  ).flat();
}
const files = await walk(build);
const routeFiles = files.filter(
  (file) => file.endsWith('.html') && !file.includes('portfolio-landing-page'),
);
const routes = routeFiles
  .map((file) => {
    const relative = path.relative(build, file).replaceAll('\\', '/');
    return relative === 'index.html'
      ? '/'
      : relative === '404.html'
        ? '/404'
        : `/${relative.replace(/\/index\.html$/, '')}`;
  })
  .sort();
const assetFiles = files.filter(
  (file) => !file.endsWith('.html') && !path.basename(file).startsWith('_'),
);
const mime = {
  '.woff2': /^font\/woff2/,
  '.svg': /^image\/svg\+xml/,
  '.webp': /^image\/webp/,
  '.avif': /^image\/avif/,
  '.png': /^image\/png/,
  '.jpg': /^image\/jpeg/,
  '.pdf': /^application\/pdf/,
  '.txt': /^text\/plain/,
  '.xml': /^(?:application|text)\/xml/,
};
// Keep uploads and checks separate: every deployed public file is compared with
// the already-built artifact, without changing its bytes or loading behavior.
for (let offset = 0; offset < assetFiles.length; offset += 4) {
  await Promise.all(
    assetFiles.slice(offset, offset + 4).map((file) =>
      scenario(`asset ${path.relative(build, file)}`, async () => {
        const relative = path.relative(build, file).replaceAll('\\', '/');
        const response = await fetch(`${base}/${relative}`);
        const actual = Buffer.from(await response.arrayBuffer());
        const expected = await readFile(file);
        const entry = {
          path: `/${relative}`,
          status: response.status,
          contentType: response.headers.get('content-type'),
          bytes: actual.length,
          sha256: sha(actual),
          localSha256: sha(expected),
          robots: response.headers.get('x-robots-tag'),
        };
        report.assets.push(entry);
        assert.equal(response.status, 200);
        assert.equal(
          entry.sha256,
          entry.localSha256,
          'deployed bytes match preview artifact',
        );
        if (mime[path.extname(file)])
          assert.match(entry.contentType ?? '', mime[path.extname(file)]);
        assert.match(entry.robots ?? '', /noindex/);
        return { bytes: actual.length };
      }),
    ),
  );
}
await scenario('robots and preview sitemap', async () => {
  const robots = await (await fetch(`${base}/robots.txt`)).text();
  assert.match(robots, /Disallow:\s*\//);
  const sitemap = await (await fetch(`${base}/sitemap.xml`)).text();
  const locations = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(
    (match) => match[1],
  );
  assert.equal(locations.length, 18);
  assert.ok(locations.every((location) => new URL(location).origin === base));
  return { robots, sitemapLocations: locations.length };
});
const absent = [
  '/phase-5-unknown-route',
  '/projects/phase-5-unknown-route',
  '/reference/',
  '/design/research-candidates/',
  '/design/ayman-portfolio-v2.figcraft',
  '/src/content/projects.json',
  '/package.json',
  '/.env',
  '/.git/config',
  '/output/preview-dist/',
  '/_headers',
];
for (const route of absent)
  await scenario(`not public ${route}`, async () => {
    const response = await fetch(`${base}${route}`);
    const text = await response.text();
    report.http.push({
      route,
      status: response.status,
      contentType: response.headers.get('content-type'),
    });
    assert.equal(response.status, 404);
    assert.match(text, /404|Page not found|lost this page/i);
  });
for (const route of ['/', '/ayman-ashraf-mounir-cv.pdf'])
  await scenario(`immutable deployment ${route}`, async () => {
    const [stableResponse, immutableResponse] = await Promise.all([
      fetch(`${base}${route}`),
      fetch(`${immutable}${route}`),
    ]);
    const [stableBytes, immutableBytes] = await Promise.all([
      stableResponse.arrayBuffer(),
      immutableResponse.arrayBuffer(),
    ]);
    assert.equal(immutableResponse.status, 200);
    assert.equal(
      sha(Buffer.from(stableBytes)),
      sha(Buffer.from(immutableBytes)),
    );
    assert.match(
      immutableResponse.headers.get('x-robots-tag') ?? '',
      /noindex/,
    );
    return { sha256: sha(Buffer.from(immutableBytes)) };
  });
async function settle(page) {
  await page.evaluate(() => document.fonts.ready);
  for (const image of await page.locator('img[src]').all())
    if (await image.isVisible()) await image.scrollIntoViewIfNeeded();
  await page.waitForFunction(
    () =>
      [...document.images]
        .filter((image) => image.hasAttribute('src'))
        .every((image) => image.complete),
    null,
    { timeout: 20000 },
  );
  await page.evaluate(() => window.scrollTo(0, 0));
}
async function capture(page, filename) {
  await page.screenshot({ path: path.join(output, filename), fullPage: true });
  report.screenshots.push(`output/phase5/${filename}`);
}
for (const [browserName, engine] of Object.entries({ chromium, firefox })) {
  const browser = await engine.launch();
  report.browsers[browserName] = browser.version();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    reducedMotion: 'reduce',
    acceptDownloads: true,
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error' && !message.text().includes('404'))
      errors.push(message.text());
  });
  const selectedRoutes =
    browserName === 'chromium'
      ? routes
      : [
          '/',
          '/projects',
          '/projects/blitzchatbot',
          '/projects/secure-notes-organizer',
          '/resume',
        ];
  for (const width of [390, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const route of selectedRoutes)
      await scenario(
        `${browserName} ${width}px direct and refresh ${route}`,
        async () => {
          errors.length = 0;
          const response = await page.goto(`${base}${route}`);
          assert.ok(
            [200, 304, ...(route === '/404' ? [404] : [])].includes(
              response.status(),
            ),
          );
          await settle(page);
          const facts = await page.evaluate(() => ({
            url: location.href,
            title: document.title,
            canonical: document.querySelector('link[rel="canonical"]')?.href,
            ogImage: document.querySelector('meta[property="og:image"]')
              ?.content,
            robots: document.querySelector('meta[name="robots"]')?.content,
            h1s: document.querySelectorAll('h1').length,
            overflow: document.documentElement.scrollWidth - innerWidth,
            brokenImages: [...document.images]
              .filter(
                (image) =>
                  image.hasAttribute('src') &&
                  (!image.complete || !image.naturalWidth),
              )
              .map((image) => image.currentSrc),
          }));
          assert.equal(new URL(facts.canonical).origin, base);
          assert.equal(new URL(facts.ogImage).origin, base);
          assert.match(facts.robots, /noindex/);
          assert.match(response.headers()['x-robots-tag'] ?? '', /noindex/);
          assert.equal(facts.h1s, 1);
          assert.equal(facts.overflow, 0);
          assert.deepEqual(facts.brokenImages, []);
          const refresh = await page.reload();
          await page.evaluate(() => document.fonts.ready);
          assert.ok(
            [200, 304, ...(route === '/404' ? [404] : [])].includes(
              refresh.status(),
            ),
          );
          assert.deepEqual(errors, []);
          report.routes.push({
            browser: browserName,
            width,
            route,
            status: response.status(),
            refreshStatus: refresh.status(),
            ...facts,
          });
          if (
            browserName === 'chromium' &&
            [
              '/',
              '/projects/blitzchatbot',
              '/projects/secure-notes-organizer',
            ].includes(route)
          ) {
            await settle(page);
            await capture(
              page,
              `${browserName}-${width}-${route === '/' ? 'home' : route.split('/').at(-1)}.png`,
            );
          }
        },
      );
    await scenario(
      `${browserName} ${width}px filters reload back and forward`,
      async () => {
        await page.goto(`${base}/projects`);
        await page.locator('[data-project-filter="public"]').click();
        await expect(
          page.locator('[data-project-category]:visible'),
        ).toHaveCount(4);
        assert.equal(
          new URL(page.url()).searchParams.get('category'),
          'public',
        );
        await page.reload();
        await expect(
          page.locator('[data-project-category]:visible'),
        ).toHaveCount(4);
        await page.locator('[data-project-filter="client"]').click();
        await expect(
          page.locator('[data-project-category]:visible'),
        ).toHaveCount(8);
        await page.goBack();
        await expect(
          page.locator('[data-project-category]:visible'),
        ).toHaveCount(4);
        await page.goForward();
        await expect(
          page.locator('[data-project-category]:visible'),
        ).toHaveCount(8);
        await page.locator('[data-project-filter="all"]').click();
        await expect(
          page.locator('[data-project-category]:visible'),
        ).toHaveCount(12);
      },
    );
    if (width === 390)
      await scenario(
        `${browserName} mobile menu keyboard and actual navigation`,
        async () => {
          await page.goto(base);
          await page.locator('#open-menu').click();
          await expect(page.locator('#mobile-menu')).toBeVisible();
          await page.keyboard.press('Escape');
          await expect(page.locator('#mobile-menu')).not.toBeVisible();
          await expect(page.locator('#open-menu')).toBeFocused();
          await page.locator('#open-menu').click();
          await page.locator('#mobile-menu a[href="/experience"]').click();
          await expect(page).toHaveURL(/\/experience\/?$/);
          await expect(page.locator('h1')).toHaveText('Experience');
        },
      );
    for (const slug of ['blitzchatbot', 'secure-notes-organizer'])
      await scenario(
        `${browserName} ${width}px ${slug} screenshot zoom and Escape`,
        async () => {
          await page.goto(`${base}/projects/${slug}`);
          await settle(page);
          const trigger = page.locator('[data-gallery-image]').first();
          await trigger.click();
          await expect(page.locator('#image-viewer')).toBeVisible();
          await page.waitForFunction(() => {
            const image = document.querySelector('#viewer-image');
            return image.complete && image.naturalWidth > 0;
          });
          await page.locator('[data-zoom="in"]').click();
          await expect(page.locator('[data-zoom="reset"]')).toHaveText('150%');
          await page.keyboard.press('Escape');
          await expect(page.locator('#image-viewer')).not.toBeVisible();
          await expect(trigger).toBeFocused();
        },
      );
  }
  await scenario(`${browserName} actual original CV download`, async () => {
    await page.goto(`${base}/resume`);
    const event = page.waitForEvent('download');
    await page.locator('a[download]').first().click();
    const download = await event;
    const filename = download.suggestedFilename();
    const target = path.join(output, `${browserName}-${filename}`);
    await download.saveAs(target);
    assert.equal(
      sha(await readFile(target)),
      sha(await readFile(path.join(root, 'Ayman Kamel - CV.pdf'))),
    );
    return { filename, sha256: sha(await readFile(target)) };
  });
  await scenario(`${browserName} legacy alias reaches Home`, async () => {
    await page.goto(`${base}/portfolio-landing-page`);
    await expect(page).toHaveURL(`${base}/`);
    await expect(page.locator('h1')).toContainText('Ayman Ashraf');
    return { mechanism: 'Existing HTML meta refresh', finalUrl: page.url() };
  });
  await context.close();
  await browser.close();
}
report.completed = new Date().toISOString();
report.summary = {
  browserRouteWidthObservations: report.routes.length,
  assetHashChecks: report.assets.length,
  passedScenarios: report.interactions.filter((entry) => entry.passed).length,
  failures: report.failures.length,
};
await writeFile(
  path.join(root, 'design/phase-5-preview-qa.json'),
  `${JSON.stringify(report, null, 2)}\n`,
);
console.log(JSON.stringify(report.summary));
if (report.failures.length) process.exitCode = 1;
