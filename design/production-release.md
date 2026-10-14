# Production release — 14 October 2026

The user approved the hosted review, requested GitHub/LinkedIn and related link icons, and explicitly instructed deployment to **[aymanashraf.me](https://aymanashraf.me)**. This is the separate go-live authorization previously reserved by the design and preview phases.

The approved release is deployed through Cloudflare Pages Direct Upload:

- Production project: `ayman-portfolio-v2`; branch `main`; environment `production`.
- Final deployment ID: `a7b80225-9acd-4bf6-a72b-ccb692e504fc`.
- Immutable deployment: [a7b80225.ayman-portfolio-v2.pages.dev](https://a7b80225.ayman-portfolio-v2.pages.dev).
- Primary URL: [aymanashraf.me](https://aymanashraf.me); `www.aymanashraf.me` is the redirecting alternate hostname.
- Account: `947dc4e40901fd4d5e90c10035a04435`; zone: `f4dd69fbac1852ab22a88dbd85da81c1`.

[Build evidence](production-build.json), [deployment evidence](production-deployment.json) and the [prechange snapshot](production-preflight.json) retain exact timestamps and artifact details. The original `ayman-portfolio-v2-preview` project, its `review` branch, original immutable deployment and noindex artifact were left unchanged. Cloudflare uploads preceded source publication and used the working tree; their source metadata identifies the earlier HEAD. The user subsequently authorized committing and pushing the V2 updates to the existing GitHub repository. Publishing source does not redeploy or change those recorded Cloudflare deployments.

## Released changes and indexing

The final implementation update adds shared GitHub, LinkedIn, email and external-link icons beside the existing text labels on Contact, the footer and applicable project actions. `src/components/LinkIcon.astro` reuses the selected local GitHub/LinkedIn assets; email/external marks are inline SVGs. The icons are decorative and do not replace visible or accessible link names. No native design file, portrait, project screenshot, content qualification or original CV bytes changed.

Hosted verification found that the zone's existing Email Address Obfuscation rewrote Contact's email links to depend on a decoder script. The final release brackets only the approved public email section with [Cloudflare's documented `email_off` markers](https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/#prevent-cloudflare-from-obfuscating-email), emitted as constant Astro Fragment HTML. The zone setting remains unchanged. The final raw response has both direct mailto links and readable email text, with no injected email decoder; Contact works with JavaScript disabled in Chromium and Firefox. The initial deployment `e90831bc-36e3-42bc-a398-ce0c92df9e92` and an identical intermediate deployment remain recorded separately in the deployment evidence.

`npm run build:production` prepares approved content and builds a separate `output/production-dist/` artifact with `PUBLIC_SITE_INDEXABLE=true` and site origin `https://aymanashraf.me`. It does not reuse the preview artifact. The production artifact has 18 indexable pages; `/404` and Astro's generated legacy redirect HTML remain noindex. `robots.txt` allows crawling and names the production sitemap. Canonicals, Open Graph and structured-data URLs use the production origin. No preview-wide `_headers` noindex rule is included.

The helper writes `_redirects` with real HTTP 301 redirects from `/portfolio-landing-page` and `/portfolio-landing-page/` to `/`. The generated redirect HTML remains a noindex fallback, separate from the host's HTTP redirect handling. Cloudflare Pages may normalize directory routes to trailing slashes.

## Domain changes

Preflight API reads found no overlapping Worker routes, Worker custom domains or Pages custom domains for the apex and `www`. Public DNS returned no address/CNAME answers. Wrangler's OAuth session could read the account, zone and Pages configuration but returned 403 for DNS and redirect-rule API reads. The authenticated Cloudflare Chrome dashboard then confirmed **zero existing DNS records** in this zone before changes; this evidence is saved as `authenticatedDashboardDns` in the preflight snapshot.

Exactly two portfolio DNS records were added through that authenticated dashboard, both proxied CNAMEs with automatic TTL:

| Host                   | Target                         |
| ---------------------- | ------------------------------ |
| `aymanashraf.me` (`@`) | `ayman-portfolio-v2.pages.dev` |
| `www.aymanashraf.me`   | `ayman-portfolio-v2.pages.dev` |

Both hostnames were associated with the production project through Pages Custom Domains. Follow-up Pages API reads reported both domain statuses, validation and verification **active**. No nameserver change or unrelated project/domain change was made.

The Cloudflare Single Redirect rule `f64436445784461c9fa1fc0ec80bd562` redirects HTTPS requests for `www.aymanashraf.me` to the apex with HTTP 301, preserving path and query. An actual request for `/projects?category=public` returned `https://aymanashraf.me/projects?category=public` as its destination.

The authenticated Edge Certificates dashboard showed an active Universal SSL certificate covering the apex and `*.aymanashraf.me`, expiring 11 January 2027. Always Use HTTPS was off before this release and was enabled through that dashboard to upgrade HTTP requests on both hostnames. No HSTS, minimum TLS version or other TLS setting was changed. Actual HTTP response checks are separate from the saved dashboard setting.

## Verification and limits

The final icon update passed Astro/TypeScript checks, formatting checks and six local automated accessibility scans with no violations. The production build records the original native-design and CV SHA-256 hashes. Earlier [Phase 4 browser/performance evidence](phase-4-verification.md) and [Phase 5 preview acceptance](phase-5-preview-qa.json) describe their own revisions; their counts are not presented as a new production acceptance run.

The existing Chrome session opened the production Home and Contact pages through ordinary networking and displayed the new icons, without a DNS override or certificate bypass. Pages API domain activation and the `www` redirect were also checked. The Windows resolver used by Node/Playwright continued returning a cached negative answer during the cutover. Additional automated production checks therefore use current Google public DNS answers (`104.21.60.170` and `172.67.198.110`) while preserving the original hostname, normal TLS certificate validation and HTTPS requests. This scoped resolver choice does not establish propagation through every visitor's resolver.

[Final production QA](production-qa.json) records 14 browser observations and 14 focused checks with zero final failures or transport limitations. It covers the final Contact correction with JavaScript enabled and disabled in Chromium and Firefox, key routes at 390/1440px, production metadata, original CV bytes, unchanged assets and redirects. All 93 non-HTML asset hashes remain unchanged; Home and the PDF match the final immutable deployment. Actual HTTP-to-HTTPS, query-preserving WWW-to-apex and both legacy-path redirects return HTTP 301. Relative `Location: /` is resolved against the request URL when verifying the legacy redirects.

[First-release evidence](production-preliminary-qa.json) retains the earlier full 19-route Chromium direct-entry/refresh checks at both widths, all 93 deployed asset SHA/MIME checks, interactions and three clean automated accessibility scans. Only Contact HTML changed in the final correction; the other 112 uploaded files were reused. The report distinguishes this evidence from the final focused run and records the corrected redirect assertions. Final screenshots are in ignored `output/production/`. No field Web Vitals or physical-device/OS-screen-reader result is claimed by this release.

## Build and update production

Use the pinned lockfile, Node.js >=22.12.0 and an authenticated Wrangler session with Pages write access. The current `wrangler.json` remains the preview configuration. The production script explicitly selects the production project and branch instead of changing that preview config.

```powershell
npm ci
npx wrangler whoami
$previousAccountId = $env:CLOUDFLARE_ACCOUNT_ID
$env:CLOUDFLARE_ACCOUNT_ID = '947dc4e40901fd4d5e90c10035a04435'
try {
  npm run check
  if ($LASTEXITCODE -ne 0) { throw 'Type checking failed.' }
  npm run lint
  if ($LASTEXITCODE -ne 0) { throw 'Formatting checks failed.' }
  npm run deploy:production
  if ($LASTEXITCODE -ne 0) { throw 'Production deployment failed.' }
} finally {
  if ($null -eq $previousAccountId) {
    Remove-Item Env:CLOUDFLARE_ACCOUNT_ID -ErrorAction SilentlyContinue
  } else {
    $env:CLOUDFLARE_ACCOUNT_ID = $previousAccountId
  }
}
```

`build:production` only builds the artifact. `deploy:production` rebuilds and runs `wrangler pages deploy ./output/production-dist --project-name ayman-portfolio-v2 --branch main --commit-dirty=true`. Project creation and custom-domain attachment are already complete and must not be repeated for routine updates. Confirm the intended account from `whoami`, preserve the last successful artifact/deployment before another release, and verify the new immutable URL, production host, indexable metadata, redirects, core interactions and actual CV download afterward.

To update only the review preview, follow [the separate Phase 5 procedure](phase-5-preview.md); `deploy:preview` targets its original project and branch. Do not upload the indexable production artifact to the review project.

## Recovery

This was the first production deployment of this project, and the authenticated prechange DNS snapshot contained no records. There is no earlier functioning production server or previous production deployment to roll back to. The saved preview is a review baseline, not an indexable production rollback artifact.

Before future releases, retain the last successful production deployment ID and artifact. If a later release fails, restore that verified production deployment or reupload its preserved production artifact to the same production project and `main` branch, then recheck the custom domain. Keep DNS stable for content-only recovery.

If this initial domain cutover must be reversed, remove only the two newly added portfolio CNAMEs, the newly attached apex/`www` Pages custom domains and the release-specific `www` redirect rule, and restore Always Use HTTPS to its recorded prior off setting if a complete configuration rollback is intended. Preserve the independent preview project and unrelated account projects. Do not delete the production project or purge global resources as a rollback shortcut.

Cloudflare references: [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/), [custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/), [Pages redirects](https://developers.cloudflare.com/pages/configuration/redirects/) and [rollbacks](https://developers.cloudflare.com/pages/configuration/rollbacks/). The saved deployment responses and authenticated dashboard observations describe this release's actual configuration.
