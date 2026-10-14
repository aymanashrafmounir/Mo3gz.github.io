import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { chromium, firefox, webkit } from '@playwright/test';

const base = process.env.QA_BASE_URL ?? 'http://127.0.0.1:4321';
const output = new URL('../output/', import.meta.url);
await mkdir(new URL('acceptance-screenshots/', output), { recursive: true });
const axeSource = await readFile(
  new URL('../node_modules/axe-core/axe.min.js', import.meta.url),
  'utf8',
);
const routes = [
  '/',
  '/about',
  '/contact',
  '/experience',
  '/resume',
  '/projects',
  ...[
    'helixtra',
    'wear-instant',
    'ibrahim-awad',
    'maysa-waheed',
    'supreme-sparkle',
    'arkedia',
    'tapora',
    'blitzchatbot',
    'artline',
    'quantitator',
    'cheque-printer',
    'secure-notes-organizer',
  ].map((slug) => `/projects/${slug}`),
  '/qa-missing-page-93825',
];
const widths = [320, 360, 375, 390, 414, 768, 1024, 1280, 1440, 1920, 2560];
let report = {
  base,
  started: new Date().toISOString(),
  scope: {
    routes,
    widths,
    engines: ['chromium', 'firefox', 'webkit'],
    textResizeMethod:
      'Every rendered element receives twice its original computed font-size and line-height, without resizing images or layout dimensions. This is a text-only resize stress test, not browser-native zoom.',
    touchMethod:
      'Chromium CDP Input.dispatchTouchEvent in a hasTouch mobile context; browser-dispatched multi-touch generates real pointer events. Close is verified with a real tap before gestures and Escape after gestures. This is emulation, not a physical-device pass.',
    imageDecodeMethod:
      'The expanded matrix makes real img elements eager and awaits decoding to verify source availability. It does not establish native lazy-loading trigger timing or performance; the separate smoke suite scrolls images into view naturally.',
  },
  browsers: {},
  matrix: [],
  accessibility: [],
  scenarios: [],
  textResize: [],
  externalLinks: [],
  screenshots: [],
  failures: [],
  limitations: [
    'Automated checks supplement visual review and do not establish complete WCAG conformance.',
    'Desktop browser engines and Chromium mobile touch emulation are tested; no physical device or OS screen reader is used.',
    'External URL availability is reported separately and does not fail internal acceptance.',
    'After the custom CDP multi-touch/pan stream, Chromium suppressed the next compatibility click even at 1200 ms. Post-pan touch Close is therefore not claimed; pre-gesture touch Close and post-gesture Escape are checked separately.',
  ],
};
let failureCount = 0;
function failure(name, error, details = {}) {
  report.failures.push({ name, message: error.message, ...details });
  failureCount++;
  console.error(`FAIL ${name}: ${error.message}`);
}
async function scenario(name, run) {
  try {
    const details = await run();
    report.scenarios.push({ name, passed: true, ...details });
    console.log(`PASS ${name}`);
  } catch (error) {
    failure(name, error);
    report.scenarios.push({ name, passed: false });
  }
}
async function settle(page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    const imgs = [...document.images].filter((image) =>
      image.hasAttribute('src'),
    );
    for (const image of imgs) {
      image.loading = 'eager';
    }
    await Promise.all(imgs.map((image) => image.decode().catch(() => {})));
  });
}
async function facts(page) {
  return page.evaluate(() => ({
    title: document.title,
    description: document.querySelector('meta[name="description"]')?.content,
    h1s: [...document.querySelectorAll('h1')].map((el) =>
      el.textContent.trim(),
    ),
    overflow: document.documentElement.scrollWidth - window.innerWidth,
    brokenImages: [...document.images]
      .filter(
        (el) => el.hasAttribute('src') && (!el.complete || !el.naturalWidth),
      )
      .map((el) => el.currentSrc || el.src),
    canonical: document.querySelector('link[rel="canonical"]')?.href,
    robots: document.querySelector('meta[name="robots"]')?.content,
    og: Object.fromEntries(
      [...document.querySelectorAll('meta[property^="og:"]')].map((el) => [
        el.getAttribute('property'),
        el.content,
      ]),
    ),
    external: [
      ...new Set(
        [...document.querySelectorAll('a[href^="https://"]')].map(
          (el) => el.href,
        ),
      ),
    ],
  }));
}
async function shot(page, name) {
  const path = new URL(`acceptance-screenshots/${name}.png`, output);
  await page.screenshot({ path: fileURLToPath(path), fullPage: true });
  report.screenshots.push(`output/acceptance-screenshots/${name}.png`);
}
async function audit(page, name) {
  await page.evaluate(axeSource);
  const result = await page.evaluate(async () => {
    const result = await axe.run(document, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'],
      },
    });
    return {
      violations: result.violations.map(({ id, impact, nodes }) => ({
        id,
        impact,
        nodes: nodes.map(({ target, failureSummary }) => ({
          target,
          failureSummary,
        })),
      })),
      incomplete: result.incomplete.map(({ id }) => id),
    };
  });
  report.accessibility.push({ name, ...result });
  assert.equal(
    result.violations.length,
    0,
    result.violations
      .map(
        (item) =>
          `${item.id}: ${item.nodes.map((node) => node.target.join(' ')).join(', ')}`,
      )
      .join('; '),
  );
}
async function focusContained(page, dialog) {
  const escapes = [];
  let browserChromeVisits = 0;
  for (const [key, count] of [
    ['Tab', 18],
    ['Shift+Tab', 10],
  ]) {
    for (let i = 0; i < count; i++) {
      await page.keyboard.press(key);
      const state = await dialog.evaluate((el) => ({
        inside: el.contains(document.activeElement),
        documentFocused: document.hasFocus(),
      }));
      if (!state.documentFocused) browserChromeVisits++;
      else if (!state.inside) escapes.push(`${key}-${i}`);
    }
  }
  assert.deepEqual(
    escapes,
    [],
    'keyboard cannot focus background content while modal is open',
  );
  const prevented = await page.locator('.wordmark').evaluate((el) => {
    el.focus();
    return document.activeElement !== el;
  });
  assert.equal(
    prevented,
    true,
    'background cannot receive programmatic focus while modal is open',
  );
  return { browserChromeVisits };
}

const filterScenario =
  'invalid filter URL falls back to all; valid state persists through reload and history';
async function filterHistory(page) {
  await page.goto(`${base}/projects?category=unknown&extra=retained#main`);
  assert.equal(await page.locator('[data-project-category]').count(), 12);
  assert.equal(
    await page.locator('[data-project-category]:visible').count(),
    12,
  );
  assert.equal(
    await page
      .locator('[data-project-filter="all"]')
      .getAttribute('aria-current'),
    'true',
  );
  await page.locator('[data-project-filter="public"]').click();
  const selected = await page
    .locator('[data-project-category]:visible')
    .count();
  assert.ok(selected > 0 && selected < 12);
  const reloaded = await page.reload();
  assert.ok(
    [200, 304].includes(reloaded.status()),
    `filtered URL reload response ${reloaded.status()}`,
  );
  await page.waitForFunction(
    (expected) =>
      document.querySelectorAll('[data-project-category]:not([hidden])')
        .length === expected,
    selected,
  );
  assert.equal(
    await page.locator('[data-project-category]:visible').count(),
    selected,
  );
  await page.locator('[data-project-filter="client"]').click();
  await page.goBack();
  await page.waitForFunction(
    (expected) =>
      document.querySelectorAll('[data-project-category]:not([hidden])')
        .length === expected,
    selected,
  );
  assert.equal(
    await page.locator('[data-project-category]:visible').count(),
    selected,
  );
  await page.goForward();
  assert.equal(new URL(page.url()).searchParams.get('category'), 'client');
  await page.waitForFunction(
    () =>
      document
        .querySelector('[data-project-filter="client"]')
        .getAttribute('aria-current') === 'true',
  );
  assert.equal(
    await page.locator('[data-project-category]:visible').count(),
    await page.locator('[data-project-category="client"]').count(),
  );
  return {
    publicCount: selected,
    clientCount: await page.locator('[data-project-category]:visible').count(),
    finalURL: page.url(),
    reloadStatus: reloaded.status(),
  };
}

async function inventoryLinks(browser) {
  const inventory = { sources: [], requests: [], missingAnchors: [] };
  const links = [];
  const pageIds = new Map();
  const missingResponses = [];
  const requestContext = await browser.newContext();
  try {
    for (const javaScriptEnabled of [true, false]) {
      const context = await browser.newContext({ javaScriptEnabled });
      const page = await context.newPage();
      try {
        for (const route of routes) {
          await page.goto(`${base}${route}`);
          const data = await page.evaluate(() => ({
            ids: [...document.querySelectorAll('[id]')].map((el) => el.id),
            links: [...document.querySelectorAll('a[href]')].map((el) => ({
              href: el.href,
              raw: el.getAttribute('href'),
              text: el.textContent.trim().slice(0, 100),
            })),
          }));
          pageIds.set(new URL(`${base}${route}`).pathname, new Set(data.ids));
          const sameOrigin = data.links.filter(({ href }) => {
            try {
              return new URL(href).origin === new URL(base).origin;
            } catch {
              return false;
            }
          });
          inventory.sources.push({
            route,
            javaScriptEnabled,
            anchors: sameOrigin.length,
          });
          links.push(
            ...sameOrigin.map((link) => ({
              ...link,
              route,
              javaScriptEnabled,
            })),
          );
        }
      } finally {
        await context.close();
      }
    }
    const destinations = [
      ...new Set(
        links
          .filter(({ raw }) => !raw.startsWith('#'))
          .map(({ href }) => {
            const url = new URL(href);
            return `${url.pathname}${url.search}`;
          }),
      ),
    ];
    for (const destination of destinations) {
      const response = await requestContext.request.get(
        `${base}${destination}`,
        { failOnStatusCode: false },
      );
      const item = {
        destination,
        status: response.status(),
        contentType: response.headers()['content-type'],
      };
      inventory.requests.push(item);
      if (item.status !== 200) missingResponses.push(item);
    }
    for (const link of links) {
      const target = new URL(link.href);
      if (!target.hash) continue;
      const id = decodeURIComponent(target.hash.slice(1));
      if (!pageIds.get(target.pathname)?.has(id))
        inventory.missingAnchors.push({
          source: link.route,
          destination: `${target.pathname}${target.search}${target.hash}`,
          text: link.text,
        });
    }
    inventory.uniqueDestinations = destinations.length;
    inventory.totalAnchors = links.length;
    report.linkInventory = inventory;
    assert.deepEqual(
      missingResponses,
      [],
      'all real internal hrefs respond HTTP 200',
    );
    assert.deepEqual(
      inventory.missingAnchors,
      [],
      'all local section links resolve to actual targets',
    );
    return {
      sources: inventory.sources.length,
      anchors: links.length,
      uniqueDestinations: destinations.length,
    };
  } finally {
    await requestContext.close();
  }
}

async function clickNavigation(page) {
  const visits = [];
  async function checkClick(link, heading) {
    const href = await link.getAttribute('href');
    await link.click();
    await page.waitForURL(`${base}${href}`);
    await page
      .getByRole('heading', { name: heading, exact: true, level: 1 })
      .waitFor();
    const response = await page.reload();
    assert.ok(
      [200, 304].includes(response.status()),
      `${href} remains directly loadable`,
    );
    visits.push({ href, heading, refreshStatus: response.status() });
  }
  await page.goto(base);
  await checkClick(
    page.getByRole('link', { name: 'Read case study: Helixtra', exact: true }),
    'Helixtra',
  );
  await checkClick(
    page.getByRole('link', { name: 'Next: Wear Instant', exact: true }),
    'Wear Instant',
  );
  await checkClick(
    page.getByRole('link', { name: 'Previous: Helixtra', exact: true }),
    'Helixtra',
  );
  await checkClick(
    page.getByRole('link', { name: 'All projects', exact: true }),
    'Projects',
  );
  await page.goto(base);
  await checkClick(
    page.getByRole('link', { name: "Let's talk", exact: true }),
    "Let's talk",
  );
  return { visits };
}

if (process.argv.includes('--links')) {
  const followUpStarted = new Date().toISOString();
  report = JSON.parse(
    await readFile(new URL('acceptance.json', output), 'utf8'),
  );
  report.fullRunFinished ??= report.finished;
  report.fullRunSummary ??= { ...report.summary };
  const names = [
    filterScenario,
    'all real internal hrefs and local anchors including no-JS navigation',
    'project cards, case neighbors, back link and closing contact navigate and refresh',
  ];
  const priorFailures = report.failures.filter((failure) =>
    names.includes(failure.name),
  );
  report.failures = report.failures.filter(
    (failure) => !names.includes(failure.name),
  );
  report.scenarios = report.scenarios.filter(
    (scenario) => !names.includes(scenario.name),
  );
  failureCount = report.failures.length;
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
  });
  const page = await context.newPage();
  page.setDefaultTimeout(8000);
  try {
    await scenario(names[0], () => filterHistory(page));
    await scenario(names[1], () => inventoryLinks(browser));
    await scenario(names[2], () => clickNavigation(page));
  } finally {
    await context.close();
    await browser.close();
  }
  report.followUps ??= [];
  report.followUps.push({
    started: followUpStarted,
    finished: new Date().toISOString(),
    reason:
      'Targeted link revalidation after corrections to actual internal hrefs and responsive image sizes. The 627 passing route/width/browser observations remain from the complete prior build/run; timestamps distinguish these revisions.',
    priorFailures,
    scenarios: report.scenarios.filter((scenario) =>
      names.includes(scenario.name),
    ),
    passed: !report.failures.some((failure) => names.includes(failure.name)),
  });
} else
  await Promise.all(
    Object.entries({ chromium, firefox, webkit }).map(
      async ([name, engine]) => {
        let browser;
        try {
          browser = await engine.launch();
          report.browsers[name] = {
            launched: true,
            version: browser.version(),
          };
        } catch (error) {
          failure(`${name} launch`, error);
          report.browsers[name] = { launched: false };
          return;
        }
        const context = await browser.newContext({
          viewport: { width: 1440, height: 1000 },
          reducedMotion: 'reduce',
        });
        const page = await context.newPage();
        page.setDefaultTimeout(8000);
        let pageErrors = [];
        page.on('pageerror', (error) => pageErrors.push(error.message));
        for (const width of widths) {
          await page.setViewportSize({ width, height: 1000 });
          for (const route of routes) {
            const label = `${name} ${width}px ${route}`;
            try {
              pageErrors = [];
              const response = await page.goto(`${base}${route}`);
              await settle(page);
              const data = await facts(page);
              const item = {
                browser: name,
                width,
                route,
                status: response.status(),
                overflow: data.overflow,
                brokenImages: data.brokenImages,
                errors: [...pageErrors],
              };
              report.matrix.push(item);
              assert.ok(
                (route.includes('qa-missing') ? [404] : [200, 304]).includes(
                  item.status,
                ),
                `route response ${item.status}`,
              );
              assert.equal(data.h1s.length, 1, 'one readable page heading');
              assert.equal(
                data.overflow,
                0,
                `horizontal overflow ${data.overflow}px`,
              );
              assert.deepEqual(
                data.brokenImages,
                [],
                'loaded responsive image sources',
              );
              assert.deepEqual(pageErrors, [], 'no uncaught browser errors');
              if (name === 'chromium' && [390, 1440].includes(width)) {
                await scenario(`WCAG 2.2 AA ${width}px ${route}`, () =>
                  audit(page, `${width}px ${route}`),
                );
              }
            } catch (error) {
              failure(label, error, { browser: name, width, route });
            }
          }
          console.log(`MATRIX ${name}: ${width}px completed`);
        }
        for (const viewport of [
          { width: 844, height: 390 },
          { width: 932, height: 430 },
        ]) {
          await page.setViewportSize(viewport);
          for (const route of [
            '/',
            '/projects',
            '/projects/blitzchatbot',
            '/projects/secure-notes-organizer',
            '/experience',
            '/resume',
          ]) {
            await scenario(
              `${name} landscape ${viewport.width}x${viewport.height} ${route}`,
              async () => {
                await page.goto(`${base}${route}`);
                await settle(page);
                const data = await facts(page);
                assert.equal(
                  data.overflow,
                  0,
                  'landscape content fits viewport',
                );
                assert.deepEqual(data.brokenImages, []);
              },
            );
          }
          await scenario(
            `${name} landscape ${viewport.width}x${viewport.height} image viewer remains within dialog`,
            async () => {
              await page.goto(`${base}/projects/secure-notes-organizer`);
              await page.locator('[data-gallery-image]').first().click();
              await page.waitForFunction(
                () => document.querySelector('#viewer-image').naturalWidth > 0,
              );
              const clipped = await page
                .locator('#image-viewer')
                .evaluate((dialog) => {
                  const outer = dialog.getBoundingClientRect();
                  return [
                    ...dialog.querySelectorAll(
                      '.viewer-controls button, #viewer-canvas, .viewer-hint',
                    ),
                  ]
                    .filter((el) => {
                      const bounds = el.getBoundingClientRect();
                      return (
                        bounds.width > 0 &&
                        bounds.height > 0 &&
                        (bounds.top < outer.top ||
                          bounds.bottom > outer.bottom + 1 ||
                          bounds.left < outer.left ||
                          bounds.right > outer.right + 1)
                      );
                    })
                    .map(
                      (el) =>
                        el.id || el.className || el.getAttribute('aria-label'),
                    );
                });
              assert.deepEqual(
                clipped,
                [],
                'viewer canvas and controls remain visible inside the dialog',
              );
              await page.keyboard.press('Escape');
            },
          );
        }
        if (name === 'chromium') {
          const metadata = [];
          const external = new Set();
          await page.setViewportSize({ width: 1440, height: 1000 });
          await scenario(
            'all page metadata, same-origin OG image responses and sitemap coverage',
            async () => {
              for (const route of routes) {
                await page.goto(`${base}${route}`);
                const data = await facts(page);
                metadata.push({ route, ...data });
                data.external.forEach((url) => external.add(url));
                assert.ok(
                  data.title && data.description,
                  `${route}: title and description`,
                );
                const canonicalPath = route.includes('qa-missing')
                  ? '/404'
                  : route;
                assert.equal(
                  data.canonical,
                  `https://aymanashraf.me${canonicalPath}`,
                  `${route}: canonical`,
                );
                assert.equal(
                  data.og['og:url'],
                  data.canonical,
                  `${route}: OG URL`,
                );
                assert.equal(
                  data.og['og:title'],
                  data.title,
                  `${route}: OG title`,
                );
                assert.equal(
                  data.og['og:description'],
                  data.description,
                  `${route}: OG description`,
                );
                assert.match(data.robots, /noindex/, 'preview remains noindex');
                const og = await context.request.get(
                  `${base}${new URL(data.og['og:image']).pathname}`,
                );
                assert.equal(og.status(), 200, `${route}: local OG response`);
                assert.match(og.headers()['content-type'], /image\//);
              }
              assert.equal(
                new Set(metadata.map((data) => data.title)).size,
                routes.length,
                'unique page titles',
              );
              assert.equal(
                new Set(metadata.map((data) => data.description)).size,
                routes.length,
                'unique page descriptions',
              );
              const sitemap = await context.request.get(`${base}/sitemap.xml`);
              assert.equal(sitemap.status(), 200);
              const locations = [
                ...(await sitemap.text()).matchAll(/<loc>(.*?)<\/loc>/g),
              ].map((match) => match[1]);
              assert.deepEqual(
                locations.sort(),
                routes
                  .filter((route) => !route.includes('qa-missing'))
                  .map((route) => `https://aymanashraf.me${route}`)
                  .sort(),
              );
              const robots = await context.request.get(`${base}/robots.txt`);
              assert.equal(robots.status(), 200);
              assert.match(await robots.text(), /Disallow: \//);
              return {
                titles: metadata.length,
                sitemapLocations: locations.length,
                uniqueOGImages: new Set(
                  metadata.map((data) => data.og['og:image']),
                ).size,
              };
            },
          );
          await scenario(
            'every direct case URL survives refresh with its case identity',
            async () => {
              for (const route of routes.filter((item) =>
                item.startsWith('/projects/'),
              )) {
                await page.goto(`${base}${route}`);
                const first = await page.locator('h1').textContent();
                const response = await page.reload();
                assert.equal(response.status(), 200);
                assert.equal(await page.locator('h1').textContent(), first);
              }
              return { cases: 12 };
            },
          );
          await scenario(filterScenario, () => filterHistory(page));
          await scenario(
            'all real internal hrefs and local anchors including no-JS navigation',
            () => inventoryLinks(browser),
          );
          await scenario(
            'project cards, case neighbors, back link and closing contact navigate and refresh',
            () => clickNavigation(page),
          );
          await scenario(
            'mobile navigation traps tab focus and prevents background focus',
            async () => {
              await page.setViewportSize({ width: 390, height: 844 });
              await page.goto(base);
              const trigger = page.getByRole('button', {
                name: 'Menu',
                exact: true,
              });
              await trigger.click();
              const menu = page.getByRole('dialog', {
                name: 'Navigation',
                exact: true,
              });
              await menu.waitFor({ state: 'visible' });
              const focus = await focusContained(page, menu);
              await audit(page, 'mobile navigation focus state WCAG 2.2 AA');
              await page.keyboard.press('Escape');
              await menu.waitFor({ state: 'hidden' });
              assert.equal(
                await trigger.evaluate((el) => el === document.activeElement),
                true,
              );
              return focus;
            },
          );
          await scenario(
            'image viewer traps focus and clamps zoom at 100–400 percent',
            async () => {
              await page.goto(`${base}/projects/secure-notes-organizer`);
              const trigger = page.locator('[data-gallery-image]').first();
              await trigger.click();
              const dialog = page.getByRole('dialog', {
                name: 'Project screenshot',
                exact: true,
              });
              await dialog.waitFor({ state: 'visible' });
              await page.waitForFunction(
                () => document.querySelector('#viewer-image').naturalWidth > 0,
              );
              const focus = await focusContained(page, dialog);
              for (let i = 0; i < 12; i++) await page.keyboard.press('+');
              assert.equal(
                await page
                  .getByRole('button', { name: 'Reset zoom' })
                  .textContent(),
                '400%',
              );
              assert.equal(
                await page
                  .getByRole('button', { name: 'Zoom in', exact: true })
                  .isDisabled(),
                true,
              );
              for (let i = 0; i < 12; i++) await page.keyboard.press('-');
              assert.equal(
                await page
                  .getByRole('button', { name: 'Reset zoom' })
                  .textContent(),
                '100%',
              );
              assert.equal(
                await page
                  .getByRole('button', { name: 'Zoom out', exact: true })
                  .isDisabled(),
                true,
              );
              await audit(page, 'image viewer WCAG 2.2 AA');
              await page.keyboard.press('Escape');
              assert.equal(
                await trigger.evaluate((el) => el === document.activeElement),
                true,
              );
              return focus;
            },
          );
          for (const width of [320, 1440]) {
            await page.setViewportSize({ width, height: 1000 });
            for (const route of routes) {
              await scenario(
                `200% text resize ${width}px ${route}`,
                async () => {
                  await page.goto(`${base}${route}`);
                  await settle(page);
                  const resized = await page.evaluate(() => {
                    const measured = [
                      ...document.querySelectorAll('body, body *'),
                    ]
                      .filter(
                        (el) =>
                          el instanceof HTMLElement &&
                          getComputedStyle(el).display !== 'none',
                      )
                      .map((el) => {
                        const style = getComputedStyle(el);
                        return {
                          el,
                          size: parseFloat(style.fontSize),
                          line: parseFloat(style.lineHeight),
                        };
                      });
                    measured.forEach(({ el, size, line }) => {
                      el.style.fontSize = `${size * 2}px`;
                      if (Number.isFinite(line))
                        el.style.lineHeight = `${line * 2}px`;
                    });
                    return {
                      elements: measured.length,
                      bodyFontSize: getComputedStyle(document.body).fontSize,
                    };
                  });
                  const data = await facts(page);
                  report.textResize.push({
                    route,
                    width,
                    ...resized,
                    overflow: data.overflow,
                  });
                  if (['/', '/projects/secure-notes-organizer'].includes(route))
                    await shot(
                      page,
                      `text-200-${width}-${route === '/' ? 'home' : 'secure-notes'}`,
                    );
                  assert.equal(
                    data.overflow,
                    0,
                    `text resize horizontal overflow ${data.overflow}px`,
                  );
                  const clipped = await page.evaluate(() =>
                    [
                      ...document.querySelectorAll(
                        'main a, main button, h1, h2, h3, .wordmark',
                      ),
                    ]
                      .filter((el) => {
                        const style = getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        return (
                          rect.width > 0 &&
                          !el.classList.contains('sr-only') &&
                          style.overflowX === 'hidden' &&
                          el.scrollWidth > el.clientWidth + 1
                        );
                      })
                      .map((el) => el.textContent.trim()),
                  );
                  assert.deepEqual(
                    clipped,
                    [],
                    'controls/headings retain their text',
                  );
                  if (route === '/') {
                    const overlap = await page.evaluate(() => {
                      const stack = document
                        .querySelector('.hero-stack')
                        .getBoundingClientRect();
                      const portrait = document
                        .querySelector('.hero-portrait')
                        .getBoundingClientRect();
                      return {
                        width: Math.max(
                          0,
                          Math.min(stack.right, portrait.right) -
                            Math.max(stack.left, portrait.left),
                        ),
                        height: Math.max(
                          0,
                          Math.min(stack.bottom, portrait.bottom) -
                            Math.max(stack.top, portrait.top),
                        ),
                      };
                    });
                    assert.ok(
                      overlap.width <= 1 || overlap.height <= 1,
                      `hero stack overlaps portrait by ${overlap.width}×${overlap.height}px`,
                    );
                  }
                },
              );
            }
          }
          await scenario(
            'reduced motion removes CSS animation, transitions and smooth scrolling',
            async () => {
              await page.setViewportSize({ width: 1440, height: 1000 });
              await page.goto(base);
              const motion = await page.evaluate(() => {
                const durations = [...document.querySelectorAll('body *')]
                  .map((el) => getComputedStyle(el))
                  .filter(
                    (style) =>
                      style.animationName !== 'none' ||
                      style.transitionDuration
                        .split(',')
                        .some((duration) => parseFloat(duration) > 0),
                  );
                return {
                  media: matchMedia('(prefers-reduced-motion: reduce)').matches,
                  activeAnimations: durations.length,
                  scrolling: getComputedStyle(document.documentElement)
                    .scrollBehavior,
                };
              });
              assert.equal(motion.media, true);
              assert.equal(motion.activeAnimations, 0);
              assert.equal(motion.scrolling, 'auto');
              return motion;
            },
          );
          await scenario(
            'all prerendered pages retain useful headings and navigation without JavaScript',
            async () => {
              const noScript = await browser.newContext({
                javaScriptEnabled: false,
                viewport: { width: 390, height: 844 },
              });
              const staticPage = await noScript.newPage();
              try {
                for (const route of routes) {
                  await staticPage.goto(`${base}${route}`);
                  assert.equal(await staticPage.locator('h1').count(), 1);
                  assert.equal(
                    await staticPage
                      .getByRole('navigation', {
                        name: 'Navigation without JavaScript',
                      })
                      .isVisible(),
                    true,
                  );
                  assert.ok(
                    (await staticPage.locator('main').innerText()).length > 80,
                  );
                }
              } finally {
                await noScript.close();
              }
              return { routes: routes.length };
            },
          );
          await scenario(
            'PDF download content type, magic bytes and unchanged original hash',
            async () => {
              const response = await context.request.get(
                `${base}/ayman-ashraf-mounir-cv.pdf`,
              );
              const bytes = await response.body();
              assert.equal(response.status(), 200);
              assert.match(
                response.headers()['content-type'],
                /application\/pdf/,
              );
              assert.equal(bytes.subarray(0, 5).toString(), '%PDF-');
              const hash = (buffer) =>
                createHash('sha256').update(buffer).digest('hex');
              const sha256 = hash(bytes);
              assert.equal(
                sha256,
                hash(
                  await readFile(
                    new URL('../Ayman Kamel - CV.pdf', import.meta.url),
                  ),
                ),
              );
              return {
                contentType: response.headers()['content-type'],
                bytes: bytes.length,
                sha256,
              };
            },
          );
          await scenario(
            'built public text contains no local paths, research URLs or private file references',
            async () => {
              const issues = [];
              let scanned = 0;
              const walk = async (dir) => {
                for (const entry of await readdir(dir, {
                  withFileTypes: true,
                })) {
                  const file = new URL(
                    entry.name + (entry.isDirectory() ? '/' : ''),
                    dir,
                  );
                  if (entry.isDirectory()) await walk(file);
                  else if (/\.(html|css|js|json|xml|txt)$/i.test(entry.name)) {
                    scanned++;
                    const text = await readFile(file, 'utf8');
                    if (
                      /(?:\b[A-Z]:[\\/]|file:\/\/|research-candidates|\.codex[\\/]|github_pat_)/i.test(
                        text,
                      )
                    )
                      issues.push(fileURLToPath(file));
                  }
                }
              };
              await walk(new URL('../dist/', import.meta.url));
              assert.deepEqual(issues, []);
              return { textFilesScanned: scanned };
            },
          );
          await scenario(
            'touch pinch grows actual image and drag pans the enlarged canvas',
            async () => {
              const touch = await browser.newContext({
                viewport: { width: 390, height: 844 },
                isMobile: true,
                hasTouch: true,
                reducedMotion: 'reduce',
              });
              const touchPage = await touch.newPage();
              try {
                await touchPage.goto(`${base}/projects/blitzchatbot`);
                await touchPage.locator('[data-gallery-image]').first().tap();
                await touchPage
                  .getByRole('button', { name: 'Close screenshot' })
                  .tap();
                await touchPage
                  .locator('#image-viewer')
                  .waitFor({ state: 'hidden' });
                await touchPage.locator('[data-gallery-image]').first().tap();
                await touchPage.waitForFunction(
                  () =>
                    document.querySelector('#viewer-image').naturalWidth > 0,
                );
                const canvas = touchPage.locator('#viewer-canvas');
                const rect = await canvas.boundingBox();
                const y = rect.y + Math.min(150, rect.height / 2);
                const cdp = await touch.newCDPSession(touchPage);
                const dispatch = (type, points) =>
                  cdp.send('Input.dispatchTouchEvent', {
                    type,
                    touchPoints: points.map(([x, y, id]) => ({ x, y, id })),
                  });
                const x = rect.x + rect.width / 2;
                const firstWidth = await touchPage
                  .locator('#viewer-image')
                  .evaluate((el) => el.getBoundingClientRect().width);
                await dispatch('touchStart', [
                  [x - 35, y, 1],
                  [x + 35, y, 2],
                ]);
                for (const distance of [45, 65, 85, 115])
                  await dispatch('touchMove', [
                    [x - distance, y, 1],
                    [x + distance, y, 2],
                  ]);
                await dispatch('touchEnd', []);
                const enlarged = await touchPage
                  .locator('#viewer-image')
                  .evaluate((el) => el.getBoundingClientRect().width);
                assert.ok(
                  enlarged > firstWidth * 1.5,
                  `pinch ${firstWidth}px → ${enlarged}px`,
                );
                const before = await canvas.evaluate((el) => el.scrollLeft);
                await dispatch('touchStart', [[x + 80, y, 3]]);
                for (const delta of [40, 80, 120, 160])
                  await dispatch('touchMove', [[x + 80 - delta, y, 3]]);
                await dispatch('touchEnd', []);
                const after = await canvas.evaluate((el) => el.scrollLeft);
                assert.ok(
                  after > before + 30,
                  `drag scroll ${before}px → ${after}px`,
                );
                await shot(touchPage, 'touch-pinch-pan-blitzchatbot');
                await touchPage.keyboard.press('Escape');
                await touchPage
                  .locator('#image-viewer')
                  .waitFor({ state: 'hidden' });
                return {
                  firstWidth,
                  enlargedWidth: enlarged,
                  scrollBefore: before,
                  scrollAfter: after,
                  source: 'browser CDP touch emulation',
                  closePaths: [
                    'touch tap before gestures',
                    'Escape after gestures',
                  ],
                };
              } finally {
                await touch.close();
              }
            },
          );
          console.log(`EXTERNAL checking ${external.size} links separately`);
          await Promise.all(
            [...external].map(async (url) => {
              try {
                const response = await context.request.get(url, {
                  timeout: 15000,
                  failOnStatusCode: false,
                });
                report.externalLinks.push({
                  url,
                  status: response.status(),
                  finalUrl: response.url(),
                  ok: response.ok(),
                });
              } catch (error) {
                report.externalLinks.push({
                  url,
                  ok: false,
                  error: error.message.split('\n')[0],
                });
              }
            }),
          );
        }
        await context.close();
        await browser.close();
      },
    ),
  );
report.finished = new Date().toISOString();
report.summary = {
  matrixNavigations: report.matrix.length,
  browserEngines: Object.values(report.browsers).filter(
    (engine) => engine.launched,
  ).length,
  widths: widths.length,
  routeCount: routes.length,
  scenariosPassed: report.scenarios.filter((test) => test.passed).length,
  scenariosFailed: report.scenarios.filter((test) => !test.passed).length,
  accessibilityScans: report.accessibility.length,
  textResizeChecks: report.textResize.length,
  externalLinks: report.externalLinks.length,
  externalLinksUnavailable: report.externalLinks.filter((link) => !link.ok)
    .length,
  failures: failureCount,
};
await writeFile(
  new URL('acceptance.json', output),
  JSON.stringify(report, null, 2),
);
await writeFile(
  new URL('../design/phase-4-acceptance.json', import.meta.url),
  JSON.stringify(report, null, 2),
);
console.log(JSON.stringify(report.summary, null, 2));
if (failureCount) process.exitCode = 1;
