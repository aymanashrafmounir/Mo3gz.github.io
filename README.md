# Ayman Portfolio V2

The user approved the final warm-paper/rust design on 14 October 2026, including the experience timeline, Selected work order, original Secure Notes application screens and the AI-edited BlitzChatbot demo. The native design was saved and verified inside this repository **before Phase 3 frontend implementation began**. [Approved design handoff](design/approved-handoff.json) records its SHA256, assets and checks.

The static Astro 7.3.8 application uses TypeScript, Tailwind CSS 4 and a self-hosted web subset of the approved Mona Sans faces. Twelve validated project entries generate the case studies; all nineteen required page routes build. The user approved the online review and explicitly authorized production deployment on 14 October 2026. The site is live at **[aymanashraf.me](https://aymanashraf.me)**, with GitHub, LinkedIn, email and external-link icons added to the relevant actions. [Production release](design/production-release.md) records the separate Cloudflare Pages project, domain setup, verification and recovery. The original [online review preview](https://review.ayman-portfolio-v2-preview.pages.dev) remains isolated and noindex; [Phase 5](design/phase-5-preview.md) preserves its historical deployment and checks. [Phase 4 verification](design/phase-4-verification.md) and the [performance report](design/phase-4-performance.md) retain local measurement evidence and limits.

## Run locally

Use Node.js >=22.12.0 and npm. Dependency versions are pinned in `package-lock.json`; the implementation was built with Node 24.

```sh
npm ci
npm run dev
```

The development server binds to loopback. Open the local URL printed by Astro. To verify and inspect the static build:

```sh
npm run check
npm run lint
npm run build
npm run preview
```

`check` runs Astro/TypeScript diagnostics. `lint` checks formatting with Prettier. `build` prepares approved content/assets and writes static output to `dist/`; `preview` serves that existing output locally. `npm run format` applies the configured formatting. Development and build both run `prepare:content` first.

Phase 4 expanded browser acceptance records 627 navigations across Chromium, Firefox and WebKit, eleven widths, 130 passing scenarios and forty clean automated accessibility scans. Separate final media/font checks retain their own revision timestamps and coverage. [Verification details](design/phase-4-verification.md) describe actual coverage and limits; [Phase 3 evidence](design/phase-3-verification.md) remains historical. With the local preview running on port 4321, use `npm run test:smoke`, `npm run test:acceptance` and `npm run test:performance -- --label=current`; matching Playwright browser binaries are required. Run performance checks after other test browsers close. The separate hosted preview has [focused remote acceptance evidence](design/phase-5-preview-qa.json).

The ordinary build is **noindex** unless `PUBLIC_SITE_INDEXABLE` is explicitly `true`. `npm run build:preview` always forces noindex and writes `output/preview-dist/`. The user-approved `npm run build:production` forces indexing on eligible pages, sets the production origin and writes `output/production-dist/`. The production build has 18 indexable pages; the error page and generated legacy redirect remain noindex. See the [release procedure](design/production-release.md) before deploying.

## Source and design

- [Canonical editable design](design/ayman-portfolio-v2.figcraft), [approval/hash record](design/approved-handoff.json), [screen review](design/README.md) and [design system](DESIGN_SYSTEM.md).
- [Product context](PRODUCT.md) and [project evidence ledger](PROJECT_CONTENT.md) preserve contribution, publication and release-status limits.
- `design/screen-content.json` and `design/selected-media-manifest.json` are the approved project/media inputs. `scripts/prepare-content.mjs` writes `src/content/projects.json`, `src/data/media.json` and the selected public assets. Update approved inputs instead of editing those generated files.
- `src/content.config.ts` validates the twelve project entries. `src/pages/projects/[slug].astro` renders their shared case-study route; the other page files supply the overview, collection and information pages.
- `src/data/profile.ts` holds career, education, skills and certifications. Shared components, styles and small gallery/filter scripts live under `src/`.
- The original supplied CV is copied unchanged to `/ayman-ashraf-mounir-cv.pdf`. The user approved publishing the original PDF, including its phone number.

The native design has 57 route frames, 11 interaction states and 68 exports across 1440/768/390px. Its verification records 852 prototype actions and zero native geometry/prototype issues. These design checks do not establish browser accessibility, HTTP status behavior, application workflows or performance.

Selected work is **Helixtra, Wear Instant, BlitzChatbot, Secure Notes Organizer**. Experience is a five-role vertical timeline on Home, Experience and Resume, preserving overlapping dates. The portfolio uses Paper `#F5F2EC`, Foreground `#26251F`, Rust `#AE3A24`, Mona Sans, readable technology labels and 18 editable Devicon marks. Desktop case text is capped at 800px.

Fourteen active media assets have 42 responsive WebP variants: **13 genuine photographs/captures and one approved AI-edited demo**. Eight additional AVIF derivatives optimize the original portrait and Helixtra capture; [source/variant hashes](design/phase-4-media-verification.json) and [browser fallback checks](design/phase-4-media.json) retain evidence. BlitzChatbot's fictional Arabic contacts/chat are visibly marked “بيانات تجريبية”; its caption identifies an AI-edited demo. The [original blank base, exact prompt and provenance](design/provenance/blitzchatbot/approved-demo.json) remain in the repository. Secure Notes uses the original Qt editor and sign-in screen captured offline, with no notes or account credentials; authentication/persistence were not verified. Terminal captures and the earlier rejected thirteen-image illustration series are excluded from active output.

`prepare:content` copies only selected media, fonts, icons, the approved CV and a share image into `public/`. Research, native exports, rejected art and `reference/` are excluded from the deployed asset set. The archived project remains in ignored `reference/` as factual reference; its previous visual design is rejected.

## Routes and behavior

| Route                              | Content                                                                                                                                                           |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/`                                | CV overview: identity and three CTAs, engineering snapshot, featured projects, career preview, education, skills, certifications and closing contact CTA.         |
| `/projects`                        | All twelve projects with All, Products & Client Work and Public Repositories filters; shareable filter state and usable no-JS collection.                         |
| `/projects/helixtra`               | Clinic SaaS story; distinguish marketing and operational app evidence.                                                                                            |
| `/projects/wear-instant`           | Virtual try-on, private uploads and asynchronous reliability; explicit development status.                                                                        |
| `/projects/ibrahim-awad`           | RTL clinic site and static/frontend delivery; contact-only review and inactive provider integration.                                                              |
| `/projects/tapora`                 | Memory cards/digital-memory pages and documented commerce/backend work.                                                                                           |
| `/projects/maysa-waheed`           | Couture catalog, order requests and atelier administration.                                                                                                       |
| `/projects/supreme-sparkle`        | Beauty ecommerce, COD workflows and verified operational fixes.                                                                                                   |
| `/projects/blitzchatbot`           | Tenant-scoped WhatsApp messaging, WebSockets and webhook validation.                                                                                              |
| `/projects/arkedia`                | Catalog/commerce and the CV-supported Java platform; avoid conflating migration variants.                                                                         |
| `/projects/cheque-printer`         | Bilingual desktop document layout, printing and local history; public code.                                                                                       |
| `/projects/artline`                | Panorama/image controls and multimodal integration; public code.                                                                                                  |
| `/projects/quantitator`            | Java/Python optimization and verified simulation examples; public code.                                                                                           |
| `/projects/secure-notes-organizer` | Siemens DISW internship team final project: C++/Qt notes, sockets, storage and genuine offline application captures; public code.                                 |
| `/about`                           | Professional introduction, focus, education and collaboration approach.                                                                                           |
| `/experience`                      | Vertical timeline of all five CV roles with their real dates, overlaps and qualified responsibilities.                                                            |
| `/resume`                          | Accessible browser-readable CV with the five-role experience timeline and genuine PDF download. Preserve chronology, verified certifications and original source. |
| `/contact`                         | Professional mailto, GitHub and LinkedIn; no contact backend needed.                                                                                              |
| `/404`                             | Useful error page, return-home/projects links; unknown URLs must return actual HTTP 404.                                                                          |

The static build also supplies a sitemap, robots response and an HTML redirect page for the old `/portfolio-landing-page` alias. The production build adds real HTTP 301 redirects for both forms of that legacy path. The production `www` hostname redirects to the apex over HTTPS while preserving path and query. Hosted preview checks confirm direct entry, refresh, alias navigation and actual unknown-path HTTP 404 responses. Cloudflare Pages normalizes directory routes with trailing slashes; the filters and navigation were checked against that hosted behavior. [Production release evidence](design/production-release.md) distinguishes the domain checks from earlier preview checks.

Project filters retain category state in the URL. Without JavaScript, the complete collection remains readable. The mobile navigation and image viewer use native dialogs; the image viewer supplies full-size images, zoom, pan and pinch controls. Browser verification must confirm keyboard, focus, Escape, touch and reduced-motion behavior.

## Verification and release

Phase 4 checks responsive behavior in Chromium, Firefox and WebKit, route/direct-entry/refresh behavior, actual internal links, image loading, PDF responses, metadata, filters, keyboard/focus, reduced motion, zoom and touch. Tested widths are 320, 360, 375, 390, 414, 768, 1024, 1280, 1440, 1920 and 2560px, with representative landscape and doubled-text checks. Automated checks supplement visual comparison with the native exports.

Performance targets are mobile Lighthouse Performance >=90; Accessibility, Best Practices and SEO >=95; LCP <=2.5s and CLS <=0.1. [Measured results](design/phase-4-performance.md) distinguish the ordinary noindex preview from a separate indexable local build. INP <=200ms requires suitable field measurement and is not established by navigation Lighthouse or its TBT metric. Local QA does not establish production readiness.

Phase 5 delivered an isolated HTTPS review preview on the `review` branch of `ayman-portfolio-v2-preview`, after account and zone verification. Its build forces noindex, uses the review origin for metadata and applies `X-Robots-Tag: noindex, nofollow` to every response, including the original PDF. Hosted checks passed for routes, assets, downloads and interactions. [Deployment evidence and reproduction](design/phase-5-preview.md) include the immutable review URL; those results describe the preview revision.

After the user's explicit go-live approval, production was deployed to the separate `ayman-portfolio-v2` project on branch `main`, with apex and `www` custom domains active. The authenticated Chrome session opened Home and Contact through ordinary networking with the new icons. [Production release](design/production-release.md) records the exact artifact, DNS changes and verification limits. Earlier local Lighthouse results remain lab measurements, not field Web Vitals for the production domain.

## Research cleanup

The [cleanup report](design/cleanup-report.json) records removal of the task-specific `codex-secure-notes-capture:local` Docker image and its twelve identified build-cache records, approximately 1.374 GB of logical storage. No global prune was used, and physical Docker disk shrink was not measured.

Filesystem cleanup remains incomplete: 238,860,297 bytes of inventoried research/temp files were **not deleted**. Automatic approval review rejected both the verified-path removal and the simplified exact-path removal as “blocked by policy”, with no further reason supplied. Approved design assets, the generated-image prompt/base and provenance were preserved permanently before cleanup. Original user projects and unrelated/global caches were left untouched.

## Phase 0 audit of the archived portfolio

| Finding                                             | Evidence and implication                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frontend is a client-rendered single-page portfolio | Archived React 18/Vite/JavaScript source has `/` and `/portfolio-landing-page`, with case-study modals rather than dedicated routes. Rebuild as static multipage content.                                                                                                                                                                                                                 |
| Requested scope outgrew the original content        | Eight archived project entries do not cover the twelve requested case studies. Career information also differs from the current CV. Use the CV/current evidence ledger, not stale copy.                                                                                                                                                                                                   |
| Dependency footprint exceeds visible requirements   | Archived package declares Redux, D3, Recharts, Axios, form/date libraries and more. A scoped search of src found no imports for the queried packages. These are candidates to remove in a fresh implementation, not an assertion that every dependency is unused.                                                                                                                         |
| Build artifacts are substantial                     | Existing JS file is 1,333,177 bytes; CSS 58,654 bytes; source map 3,251,203 bytes. These are file sizes, not transfer sizes, Lighthouse measurements or measured bundle attribution.                                                                                                                                                                                                      |
| Deployment configuration is inconsistent            | Vite outputs `build`; deploy script uses `gh-pages -d build`; the archived workflow text publishes `dist` and uses Node 18. The workflow filename has no .yml/.yaml extension. Do not treat it as verified active CI.                                                                                                                                                                     |
| SEO depends heavily on a JS shell                   | index.html has general metadata but no page-specific static case studies, canonical/OG system or JSON-LD. robots.txt exists; no sitemap was found in the inspected archived source.                                                                                                                                                                                                       |
| Unneeded external scripts are present               | Archived HTML loads Google Analytics and a Rocket script. New site should use only approved telemetry and required assets.                                                                                                                                                                                                                                                                |
| The old .env is Git-tracked                         | Inspected variable names include several VITE-prefixed provider API-key fields, Supabase fields and analytics IDs; values were not printed or assessed for validity. Ignoring reference does not remove historical files from Git. New build inputs must exclude archived configuration and any secret-bearing client variables.                                                          |
| Personal information needs current authority        | Old source uses a different LinkedIn handle and displays a phone number. Use the supplied professional URLs. The user separately authorized the original CV PDF with its phone number.                                                                                                                                                                                                    |
| Design does not meet the new brief                  | Stabilized archived desktop/mobile captures show a centered profile hero, broad empty space, section navigation and generic repeated presentation. Source includes simulated loading, repeated motion and an availability-looking dot without verified status. Do not carry that status indicator into V2.                                                                                |
| Domain could not be reached during this audit       | Chromium returned ERR_NAME_NOT_RESOLVED for aymanashraf.me. Google public DNS returned an apex A query with Status 0 and no Answer, an apex AAAA query with Status 2, and Cloudflare nameservers for the NS query. The www checks also did not establish working resolution. This is not proof of registration/ownership failure. Account/zone/DNS checks remain for deployment planning. |

The Git remote is the existing `aymanashrafmounir/Mo3gz.github.io` repository. This historical audit did not move the domain or alter its remote deployment. The V2 source update replaces the old tracked paths; their preserved original copies remain local in ignored `reference/`. The user separately authorized the later Cloudflare production release and publication of these updates to GitHub.

## Approval record

The user approved the plan, required imagery and native Figcraft screens before frontend coding, rejected the original blue/cyan illustration direction, selected A, and approved the final timeline/Selected work/application-image corrections. The approved BlitzChatbot image-generator edit is the one generated demo allowed in current media. The earlier illustration series remains rejected. Visible Figcraft MCP viewing was explicitly requested; no automatic GUI launch hook was added.

The [approved handoff](design/approved-handoff.json) is the immutable native-design baseline. The user subsequently approved the hosted review, requested link icons and explicitly authorized deployment to `aymanashraf.me`; [the release record](design/production-release.md) documents that separate production action.
