import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { chromium, firefox, webkit } from '@playwright/test';

const base = process.env.QA_BASE_URL ?? 'http://127.0.0.1:4321';
const output = new URL('../output/', import.meta.url);
await mkdir(new URL('screenshots/', output), { recursive: true });
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
  '/404',
];
const widths = [320, 360, 375, 390, 414, 768, 1024, 1280, 1440, 1920, 2560];
const report = {
  base,
  started: new Date().toISOString(),
  browsers: {},
  routes: [],
  responsive: [],
  interactions: [],
  accessibility: [],
  screenshots: [],
  failures: [],
};

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

async function settle(page) {
  await page.evaluate(() => document.fonts.ready);
  // Scroll real lazy images into view instead of overriding their loading behavior.
  const images = page.locator('img[src]');
  for (const image of await images.all()) {
    if (await image.isVisible()) await image.scrollIntoViewIfNeeded();
  }
  await page.waitForFunction(
    () =>
      [...document.images]
        .filter((image) => image.hasAttribute('src'))
        .every((image) => image.complete),
    null,
    { timeout: 15000 },
  );
  await page.evaluate(() => window.scrollTo(0, 0));
}

async function pageFacts(page) {
  return page.evaluate(() => ({
    title: document.title,
    description: document.querySelector('meta[name="description"]')?.content,
    robots: document.querySelector('meta[name="robots"]')?.content,
    h1s: [...document.querySelectorAll('h1')].map((heading) =>
      heading.textContent.trim(),
    ),
    overflow: document.documentElement.scrollWidth - window.innerWidth,
    brokenImages: [...document.images]
      .filter(
        (image) =>
          image.hasAttribute('src') &&
          (!image.complete || image.naturalWidth === 0),
      )
      .map((image) => image.currentSrc || image.src),
    images: [...document.images].filter((image) => image.hasAttribute('src'))
      .length,
    canonical: document.querySelector('link[rel="canonical"]')?.href,
  }));
}

async function audit(page, name) {
  await page.evaluate(axeSource);
  const result = await page.evaluate(async () => {
    const { violations, incomplete } = await axe.run(document, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa'] },
    });
    return {
      violations: violations.map(({ id, impact, description, nodes }) => ({
        id,
        impact,
        description,
        nodes: nodes.map(({ target, failureSummary }) => ({
          target,
          failureSummary,
        })),
      })),
      incompleteCount: incomplete.length,
    };
  });
  report.accessibility.push({ name, ...result });
  assert.equal(
    result.violations.length,
    0,
    `${name}: axe ${result.violations.map((violation) => violation.id).join(', ')}`,
  );
}

async function capture(page, name) {
  const path = new URL(`screenshots/${name}.png`, output);
  await settle(page);
  await page.screenshot({
    path: path.pathname.replace(/^\/(\w:)/, '$1'),
    fullPage: true,
  });
  report.screenshots.push(`output/screenshots/${name}.png`);
}

for (const [name, engine] of Object.entries({ chromium, firefox, webkit })) {
  let browser;
  try {
    browser = await engine.launch();
    report.browsers[name] = { version: browser.version(), launched: true };
  } catch (error) {
    report.browsers[name] = { launched: false, error: error.message };
    report.failures.push({ name: `${name} launch`, message: error.message });
    continue;
  }
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  let browserErrors = [];
  page.on('pageerror', (error) => browserErrors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error' && !message.text().includes('404'))
      browserErrors.push(message.text());
  });
  const selectedRoutes =
    name === 'chromium'
      ? routes
      : ['/', '/projects', '/projects/secure-notes-organizer'];
  for (const width of [390, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const route of selectedRoutes) {
      await scenario(`${name} ${width}px ${route}`, async () => {
        browserErrors = [];
        const response = await page.goto(`${base}${route}`);
        await settle(page);
        const facts = await pageFacts(page);
        const result = {
          browser: name,
          width,
          route,
          status: response.status(),
          ...facts,
          errors: [...browserErrors],
        };
        report.routes.push(result);
        // The explicitly requested static error asset is served as 200 by Astro
        // preview. Unknown URLs are separately required to return an actual 404.
        assert.ok(
          [200, 304].includes(response.status()),
          `explicit static route HTTP status ${response.status()}`,
        );
        assert.equal(facts.h1s.length, 1, 'one page heading');
        assert.ok(facts.title && facts.description, 'metadata present');
        assert.match(
          facts.robots,
          /noindex/,
          'local preview must remain noindex',
        );
        assert.equal(
          facts.overflow,
          0,
          `horizontal overflow ${facts.overflow}px`,
        );
        assert.deepEqual(facts.brokenImages, [], 'all page images load');
        assert.deepEqual(browserErrors, [], 'no JavaScript or console errors');
        return { images: facts.images };
      });
    }
  }

  if (name === 'chromium') {
    await scenario('unique route titles and descriptions', async () => {
      const pages = report.routes.filter(
        (route) => route.browser === 'chromium' && route.width === 1440,
      );
      assert.equal(
        new Set(pages.map((route) => route.title)).size,
        routes.length,
      );
      assert.equal(
        new Set(pages.map((route) => route.description)).size,
        routes.length,
      );
    });
    for (const width of widths) {
      await scenario(`home responsive ${width}px`, async () => {
        await page.setViewportSize({ width, height: 1000 });
        await page.goto(base);
        await settle(page);
        const facts = await pageFacts(page);
        report.responsive.push({
          width,
          overflow: facts.overflow,
          brokenImages: facts.brokenImages,
        });
        assert.equal(
          facts.overflow,
          0,
          `horizontal overflow ${facts.overflow}px`,
        );
        assert.deepEqual(facts.brokenImages, []);
      });
    }
    await scenario(
      'project category URL, visible counts and back navigation',
      async () => {
        await page.setViewportSize({ width: 1440, height: 1000 });
        await page.goto(`${base}/projects`);
        const cards = page.locator('[data-project-category]');
        const total = await cards.count();
        assert.equal(total, 12);
        for (const category of ['client', 'public']) {
          await page.locator(`[data-project-filter="${category}"]`).click();
          assert.equal(
            new URL(page.url()).searchParams.get('category'),
            category,
          );
          const matching = page.locator(
            `[data-project-category="${category}"]`,
          );
          const expected = await matching.count();
          assert.ok(expected > 0 && expected < total);
          assert.equal(
            await page.locator('[data-project-category]:visible').count(),
            expected,
          );
          assert.equal(
            await page.locator('[data-project-count]').textContent(),
            `${expected} projects`,
          );
          assert.equal(
            await page
              .locator(`[data-project-filter="${category}"]`)
              .getAttribute('aria-current'),
            'true',
          );
        }
        await page.goBack();
        assert.equal(
          new URL(page.url()).searchParams.get('category'),
          'client',
        );
        assert.equal(
          await page.locator('[data-project-category]:visible').count(),
          await page.locator('[data-project-category="client"]').count(),
        );
        await page.goBack();
        assert.equal(new URL(page.url()).searchParams.get('category'), null);
        assert.equal(
          await page.locator('[data-project-category]:visible').count(),
          total,
        );
        await page.goto(`${base}/projects?category=public`);
        assert.equal(
          await page.locator('[data-project-category]:visible').count(),
          await page.locator('[data-project-category="public"]').count(),
        );
        return {
          total,
          client: await page
            .locator('[data-project-category="client"]')
            .count(),
          public: await page
            .locator('[data-project-category="public"]')
            .count(),
        };
      },
    );
    await scenario(
      'mobile menu keyboard, Escape and focus restoration',
      async () => {
        await page.setViewportSize({ width: 390, height: 844 });
        await page.goto(base);
        const trigger = page.getByRole('button', { name: 'Menu', exact: true });
        await trigger.focus();
        await page.keyboard.press('Enter');
        const menu = page.getByRole('dialog', {
          name: 'Navigation',
          exact: true,
        });
        await menu.waitFor({ state: 'visible' });
        assert.equal(await trigger.getAttribute('aria-expanded'), 'true');
        await audit(page, 'mobile menu');
        await page.keyboard.press('Escape');
        await menu.waitFor({ state: 'hidden' });
        assert.equal(await trigger.getAttribute('aria-expanded'), 'false');
        assert.equal(
          await trigger.evaluate(
            (element) => document.activeElement === element,
          ),
          true,
        );
      },
    );
    await scenario(
      'application screenshot enlarge, zoom, Escape and focus restoration',
      async () => {
        await page.goto(`${base}/projects/secure-notes-organizer`);
        const trigger = page.locator('[data-gallery-image]').first();
        await trigger.click();
        const viewer = page.getByRole('dialog', {
          name: 'Project screenshot',
          exact: true,
        });
        await viewer.waitFor({ state: 'visible' });
        await page.waitForFunction(
          () => document.querySelector('#viewer-image').naturalWidth > 0,
        );
        const fittedWidth = await page
          .locator('#viewer-image')
          .evaluate((image) => image.getBoundingClientRect().width);
        await page
          .getByRole('button', { name: 'Zoom in', exact: true })
          .click();
        assert.equal(
          await page.getByRole('button', { name: 'Reset zoom' }).textContent(),
          '150%',
        );
        assert.ok(
          (await page
            .locator('#viewer-image')
            .evaluate((image) => image.getBoundingClientRect().width)) >
            fittedWidth,
        );
        await page.keyboard.press('+');
        assert.equal(
          await page.getByRole('button', { name: 'Reset zoom' }).textContent(),
          '200%',
        );
        await page.getByRole('button', { name: 'Reset zoom' }).click();
        assert.equal(
          await page.getByRole('button', { name: 'Reset zoom' }).textContent(),
          '100%',
        );
        await audit(page, 'mobile screenshot viewer');
        await page.keyboard.press('Escape');
        await viewer.waitFor({ state: 'hidden' });
        assert.equal(
          await trigger.evaluate(
            (element) => document.activeElement === element,
          ),
          true,
        );
      },
    );
    await scenario('download serves original CV bytes', async () => {
      await page.goto(`${base}/resume`);
      const response = await context.request.get(
        `${base}/ayman-ashraf-mounir-cv.pdf`,
      );
      assert.equal(response.status(), 200);
      const hash = (value) => createHash('sha256').update(value).digest('hex');
      const actual = hash(await response.body());
      assert.equal(
        actual,
        hash(
          await readFile(new URL('../Ayman Kamel - CV.pdf', import.meta.url)),
        ),
      );
      const downloadEvent = page.waitForEvent('download');
      await page
        .getByRole('link', { name: 'Download original CV', exact: true })
        .click();
      const download = await downloadEvent;
      assert.equal(download.suggestedFilename(), 'ayman-ashraf-mounir-cv.pdf');
      return { sha256: actual, filename: download.suggestedFilename() };
    });
    await scenario('unknown URL uses custom non-indexable 404', async () => {
      const response = await page.goto(`${base}/qa-missing-page-93825`);
      assert.equal(response.status(), 404);
      const facts = await pageFacts(page);
      assert.equal(facts.h1s.length, 1);
      assert.match(facts.h1s[0], /not|404|found/i);
      assert.match(facts.robots, /noindex/);
    });
    await scenario(
      'no JavaScript retains complete collection and navigation',
      async () => {
        const noScript = await browser.newContext({
          javaScriptEnabled: false,
          viewport: { width: 390, height: 844 },
        });
        const staticPage = await noScript.newPage();
        await staticPage.goto(`${base}/projects?category=public`);
        assert.equal(
          await staticPage.locator('[data-project-category]:visible').count(),
          12,
        );
        assert.equal(
          await staticPage
            .getByRole('navigation', { name: 'Navigation without JavaScript' })
            .isVisible(),
          true,
        );
        await noScript.close();
      },
    );
    for (const [route, width] of [
      ['/', 1440],
      ['/', 390],
      ['/experience', 390],
      ['/resume', 1440],
      ['/projects/secure-notes-organizer', 1440],
      ['/projects/blitzchatbot', 390],
    ]) {
      await scenario(`axe ${route} ${width}px`, async () => {
        await page.setViewportSize({ width, height: 1000 });
        await page.goto(`${base}${route}`);
        await settle(page);
        await audit(page, `${route} ${width}px`);
      });
    }
    for (const [route, width, name] of [
      ['/', 1440, 'home-1440'],
      ['/', 390, 'home-390'],
      ['/projects', 1440, 'projects-1440'],
      ['/experience', 390, 'experience-390'],
      ['/projects/blitzchatbot', 390, 'blitzchatbot-390'],
    ]) {
      await scenario(`screenshot ${name}`, async () => {
        await page.setViewportSize({ width, height: 1000 });
        await page.goto(`${base}${route}`);
        await capture(page, name);
      });
    }
  }
  await context.close();
  await browser.close();
}

report.finished = new Date().toISOString();
report.summary = {
  routeChecks: report.routes.length,
  responsiveWidths: report.responsive.length,
  scenarios: report.interactions.length,
  accessibilityScans: report.accessibility.length,
  failures: report.failures.length,
};
await writeFile(new URL('qa.json', output), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report.summary, null, 2));
if (report.failures.length) process.exitCode = 1;
