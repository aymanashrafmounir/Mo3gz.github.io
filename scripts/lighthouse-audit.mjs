import { execFile } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { promisify } from 'node:util';
import { chromium } from '@playwright/test';

const execute = promisify(execFile);
const root = fileURLToPath(new URL('../', import.meta.url));
const options = Object.fromEntries(
  process.argv.slice(2).map((argument) => {
    const separator = argument.indexOf('=');
    if (!argument.startsWith('--') || separator < 3) {
      throw new Error(`Use --name=value arguments: ${argument}`);
    }
    return [argument.slice(2, separator), argument.slice(separator + 1)];
  }),
);
const base = options.base ?? 'http://127.0.0.1:4321';
const label = options.label ?? 'current';
for (const name of Object.keys(options)) {
  if (!['base', 'label', 'cases', 'categories'].includes(name)) {
    throw new Error(`Unknown option: ${name}`);
  }
}
if (
  options.categories &&
  options.categories
    .split(',')
    .some(
      (category) =>
        !['performance', 'accessibility', 'best-practices', 'seo'].includes(
          category,
        ),
    )
) {
  throw new Error('Invalid Lighthouse category');
}
if (!/^[a-z0-9-]+$/i.test(label)) throw new Error('Invalid report label');
const cases = [
  { name: 'home-mobile', route: '/', preset: 'mobile' },
  { name: 'home-desktop', route: '/', preset: 'desktop' },
  { name: 'projects-mobile', route: '/projects', preset: 'mobile' },
  {
    name: 'blitzchatbot-mobile',
    route: '/projects/blitzchatbot',
    preset: 'mobile',
  },
  {
    name: 'secure-notes-mobile',
    route: '/projects/secure-notes-organizer',
    preset: 'mobile',
  },
  { name: 'resume-mobile', route: '/resume', preset: 'mobile' },
  {
    name: 'supreme-sparkle-mobile',
    route: '/projects/supreme-sparkle',
    preset: 'mobile',
    optional: true,
  },
  {
    name: 'arkedia-mobile',
    route: '/projects/arkedia',
    preset: 'mobile',
    optional: true,
  },
].filter((item) =>
  options.cases ? options.cases.split(',').includes(item.name) : !item.optional,
);
if (!cases.length) throw new Error('No matching audit cases');
const output = path.join(root, 'output/lighthouse', label);
await mkdir(output, { recursive: true });
const version = JSON.parse(
  await readFile(
    path.join(root, 'node_modules/lighthouse/package.json'),
    'utf8',
  ),
).version;
const report = {
  generatedAt: new Date().toISOString(),
  label,
  base,
  lighthouseVersion: version,
  chromiumExecutable: chromium.executablePath(),
  method:
    'Lighthouse CLI; default simulated mobile and desktop preset; cold browser storage',
  inp: 'Not measured by navigation Lighthouse. TBT is not an INP substitute.',
  cases: [],
};
for (const item of cases) {
  const url = new URL(item.route, base).href;
  const outputPath = path.join(output, item.name);
  const arguments_ = [
    path.join(root, 'node_modules/lighthouse/cli/index.js'),
    url,
    '--output=json',
    '--output=html',
    `--output-path=${outputPath}`,
    '--chrome-flags=--headless=new',
    '--no-enable-error-reporting',
    '--quiet',
  ];
  if (item.preset === 'desktop') arguments_.push('--preset=desktop');
  if (options.categories) {
    arguments_.push(`--only-categories=${options.categories}`);
  }
  const start = Date.now();
  const { stdout, stderr } = await execute(process.execPath, arguments_, {
    cwd: root,
    env: { ...process.env, CHROME_PATH: chromium.executablePath() },
    maxBuffer: 4 * 1024 * 1024,
    timeout: 240_000,
    windowsHide: true,
  });
  await writeFile(`${outputPath}.log`, stdout + stderr);
  const result = JSON.parse(
    await readFile(`${outputPath}.report.json`, 'utf8'),
  );
  if (result.runtimeError) throw new Error(JSON.stringify(result.runtimeError));
  const metric = (id) => result.audits[id]?.numericValue ?? null;
  const summary = {
    ...item,
    requestedUrl: result.requestedUrl,
    finalDisplayedUrl: result.finalDisplayedUrl,
    fetchTime: result.fetchTime,
    durationMs: Date.now() - start,
    environment: result.environment,
    configSettings: result.configSettings,
    scores: Object.fromEntries(
      Object.entries(result.categories).map(([key, category]) => [
        key,
        Math.round(category.score * 100),
      ]),
    ),
    metrics: {
      fcpMs: metric('first-contentful-paint'),
      lcpMs: metric('largest-contentful-paint'),
      speedIndexMs: metric('speed-index'),
      tbtMs: metric('total-blocking-time'),
      cls: metric('cumulative-layout-shift'),
      transferredBytes: metric('total-byte-weight'),
    },
    findings: Object.values(result.audits)
      .filter(
        (audit) =>
          audit.score !== null &&
          audit.score !== 1 &&
          !['informative', 'manual', 'notApplicable'].includes(
            audit.scoreDisplayMode,
          ),
      )
      .map((audit) => ({
        id: audit.id,
        title: audit.title,
        score: audit.score,
        displayValue: audit.displayValue,
        numericValue: audit.numericValue,
        metricSavings: audit.metricSavings,
        overallSavingsMs: audit.details?.overallSavingsMs,
        overallSavingsBytes: audit.details?.overallSavingsBytes,
      })),
    warnings: result.runWarnings,
    rawReport: path
      .relative(root, `${outputPath}.report.json`)
      .replaceAll('\\', '/'),
  };
  report.cases.push(summary);
  await writeFile(
    path.join(output, 'summary.json'),
    JSON.stringify(report, null, 2) + '\n',
  );
  console.log(
    JSON.stringify({
      name: item.name,
      scores: summary.scores,
      metrics: summary.metrics,
    }),
  );
}
console.log(`Saved ${cases.length} reports to ${path.relative(root, output)}`);
