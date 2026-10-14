# Phase 5 — online review preview

> Historical snapshot: this report describes the preview published and checked on 14 October 2026 before production approval. Later that day the user requested link icons and explicitly approved the separate [production release](production-release.md) to `aymanashraf.me`. The preview project and evidence below remain unchanged; statements about a future go-live decision describe the authority at this report's original timestamp.

Published and checked on 14 October 2026 following the user's explicit request to start Phase 5 and provide an online preview before production.

- Review URL: [review.ayman-portfolio-v2-preview.pages.dev](https://review.ayman-portfolio-v2-preview.pages.dev).
- This deployment: [14a3e489.ayman-portfolio-v2-preview.pages.dev](https://14a3e489.ayman-portfolio-v2-preview.pages.dev).
- Provider: Cloudflare Pages Direct Upload; project `ayman-portfolio-v2-preview`; branch `review`; environment **Preview**.
- Deployment ID: `14a3e489-ce57-46ce-a791-743b11cf62db`.
- Cloudflare account: `947dc4e40901fd4d5e90c10035a04435`.

[Deployment API evidence](phase-5-deployment.json), [artifact evidence](phase-5-preview-build.json) and [hosted acceptance results](phase-5-preview-qa.json) retain timestamps and verification details. The API reports a successful preview deployment, no custom domains and no canonical production deployment. The project's production branch is `main`; nothing was deployed to that branch.

The authenticated account also exposes the active `aymanashraf.me` zone, ID `f4dd69fbac1852ab22a88dbd85da81c1`. Its Cloudflare nameservers were verified read-only. This phase created the isolated preview project and uploaded its static artifact. It made no DNS, custom-domain, production-route or existing-project changes. No Git commit or push was made. The deployment's commit metadata points at the pre-existing HEAD with a dirty working tree; it is not a claim that HEAD contains this implementation.

## Build and indexing

`wrangler.json` names only the isolated preview project and `output/preview-dist` output. `npm run build:preview` runs the approved content preparation and Astro build, forces `PUBLIC_SITE_INDEXABLE=false` and overrides Astro's site origin with the review URL. Ordinary `dist/` output and the default production site configuration remain separate.

The artifact contains 20 HTML files: 19 required pages and the legacy redirect. All 20 carry meta noindex, including Astro's redirect page. `_headers` also applies `X-Robots-Tag: noindex, nofollow` to every path, including the original CV. `robots.txt` disallows crawling. Canonicals, Open Graph URLs, structured-data URLs and sitemap entries use the preview origin. Noindex controls indexing; the preview itself is publicly accessible for review.

Only the selected public assets are uploaded. Native design files, source, research candidates, `reference/`, local configuration and source maps are outside the artifact. The original approved CV and native design retain their recorded SHA-256 hashes. No portrait, project image, caption or layout change was required for deployment.

## Hosted verification

The focused HTTPS acceptance run passed **173 scenarios with zero failures**:

- 48 route/width/browser observations: all 19 routes at 390 and 1440px in Chromium, plus five key routes at both widths in Firefox. Direct entry, refresh, decoded images, overflow and browser-console checks pass.
- 93 non-HTML asset responses match the local artifact SHA-256 and expected MIME type, including every original image, WebP/AVIF variant, web font, icon and CV PDF.
- Collection filters retain state through reload and browser Back/Forward. Mobile menu navigation, Escape and trigger-focus restoration pass.
- BlitzChatbot and Secure Notes original image enlargement, 150% zoom, Escape and focus restoration pass. Actual CV browser downloads match the original PDF bytes in both engines.
- Preview-origin metadata, sitemap, crawl blocking and noindex response headers pass. Eleven private/unknown paths return HTTP 404. The legacy HTML redirect reaches Home.
- Stable and immutable deployment URLs serve matching Home and PDF content.

Cloudflare Pages normalizes directory routes to trailing slashes. Filters and navigation were checked on the deployed host with that normalization. The old `/portfolio-landing-page` alias uses Astro's existing HTML meta refresh; it is not an HTTP 301 redirect.

Six review screenshots and downloaded test PDFs are stored in ignored `output/phase5/`. The tracked report records their paths. The run uses automated desktop browser engines and emulated widths, not physical devices or OS screen readers. It does not repeat the full [Phase 4 matrix](phase-4-verification.md), establish field Web Vitals, or verify the underlying featured applications' workflows.

## Update the review preview

Use the pinned dependencies and an authenticated Wrangler session with Pages write access to the account above. Select the account explicitly in PowerShell before invoking the deployment script:

```powershell
npm ci
npx wrangler whoami
$env:CLOUDFLARE_ACCOUNT_ID = '947dc4e40901fd4d5e90c10035a04435'
npm run check
npm run lint
npm run deploy:preview
```

`deploy:preview` rebuilds and uploads only `output/preview-dist` to branch `review`. It does not select the account itself. Use the intended account in the shell and preserve any previous environment setting when running from an existing session. The review alias follows successful deployments to this branch; Wrangler also prints an immutable deployment URL.

Wrangler 4.151.0 is pinned. Its Pages deployment command uses the root `wrangler.json`; custom config paths and `account_id` inside a Pages config were rejected by this version. Project creation is already complete and must not be repeated for routine updates. Initial creation used the version's explicit Pages creation path; subsequent deployments target the existing project normally.

After an update, verify the emitted immutable URL and rerun the focused hosted checks against the matching local artifact:

```powershell
$env:QA_BASE_URL = 'https://review.ayman-portfolio-v2-preview.pages.dev'
$env:QA_IMMUTABLE_URL = 'https://<new-deployment-id>.ayman-portfolio-v2-preview.pages.dev'
node scripts/verify-preview.mjs
```

The script requires the matching Playwright Chromium and Firefox binaries. Without overrides it targets this document's original stable/immutable URLs and `output/preview-dist`. Update `QA_IMMUTABLE_URL` after each deployment so comparison uses the newly uploaded artifact. It writes the tracked JSON report and ignored screenshots; format the resulting report with Prettier before saving changes.

## Recovery and production boundary

Keep this immutable URL as the original review baseline. Before a later update, preserve the complete current artifact in a separate ignored directory if it may need to be uploaded again. To restore review content, upload that preserved artifact to the same existing project and `review` branch, including its `_headers`; then rerun hosted checks. Do not switch to `main`, attach the portfolio domain or delete the project as a preview recovery action.

The existing production/domain configuration was not replaced, so no production rollback is required by this phase. Production release still requires the user's explicit go-live decision, followed by a concrete release plan covering the intended production target, current DNS/routing snapshot, indexing, HTTPS, redirects and rollback. User review of this preview is the next step.

Cloudflare references: [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/), [preview deployments](https://developers.cloudflare.com/pages/configuration/preview-deployments/), [headers](https://developers.cloudflare.com/pages/configuration/headers/) and [Pages Wrangler commands](https://developers.cloudflare.com/workers/wrangler/commands/pages/). Installed CLI behavior and the saved deployment response were also checked directly.
