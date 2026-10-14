# Phase 4 browser and performance verification

Browser acceptance passed locally on 14 October 2026. This report describes the static build served on loopback; it does not establish deployed-host behavior or field Web Vitals. Performance results and their measured limits are recorded separately in [the Lighthouse report](phase-4-performance.md).

## Browser acceptance

[The expanded acceptance record](phase-4-acceptance.json) contains 627 route/width/browser observations: nineteen routes at eleven widths in Chromium 153, Firefox 155 and WebKit 26.6. It records 130 passing scenarios, forty automated accessibility scans, thirty-eight text-resize checks and zero remaining failures. The complete matrix precedes the final link/source-size corrections; timestamped focused follow-ups verify the link corrections without rewriting earlier observations. The subsequent smoke run rechecks image availability with their corrected source sizes.

The suite checks direct entry and refresh, useful unknown-route HTTP 404s, unique metadata and working same-origin share images, sitemap and preview robots behavior, filter reload/history, keyboard focus, reduced motion, screenshot zoom/pan, landscape viewer geometry, original PDF bytes and download responses. An inventory of 981 rendered anchors across 38 JavaScript/no-JavaScript page views found 34 distinct internal destinations returning HTTP 200 and no missing local anchor targets. Fifteen external destinations responded successfully at test time; those observations are separate from internal acceptance.

The text stress test doubles every rendered element's original computed font size and line height while retaining layout/image dimensions. It is not native browser zoom. The 320px hero overlap regression and landscape viewer clipping are checked separately. Real mobile Close taps, CDP-emulated pinch/pan and post-gesture keyboard Escape were verified. The custom CDP multi-touch stream suppressed a subsequent compatibility click, so a post-pan touch Close pass is not claimed. Physical devices and OS screen readers were not used; automated scans do not prove complete WCAG conformance.

The 13:16 UTC build passed the [smoke script](../scripts/verify-site.mjs): 79 scenarios, fifty route/browser/width checks, eleven homepage widths and eight automated accessibility scans. Unlike the expanded matrix's eager decoding, this script scrolls actual lazy images into view without overriding their loading attributes. Its raw report and screenshots are in ignored `output/qa.json` and `output/screenshots/`. Subsequent CSS delivery, preload and AVIF changes are measured and checked separately.

## Corrections and preservation

- Converted the original Mona Sans faces to WOFF2 and then prepared Latin-1/punctuation web subsets. Final web faces total 145,204 bytes compared with 568,556 bytes for full source TTFs (74.5% smaller). These are file sizes, not complete HTTP transfers. [Initial full-font verification](phase-4-font-verification.json) records the intermediate 797-glyph conversion; final subsets retain 362 glyphs and 217 mapped codepoints per face. [Coverage and hashes](assets/fonts/web/coverage.json) and [browser font acceptance](phase-4-fonts.json) record 5,076 text measurements matching full originals at zero width difference and 36 passing layout checks. The final [metadata-only correction](phase-4-font-metadata.json) changes WWS naming; all other font tables except the checksum header remain byte-identical to those tested subsets. Original native TTFs and OFL notice remain. The modified subset family is named Ayman Sans Web to respect the reserved original name. Site builds copy precompiled files and check character coverage; optional font regeneration alone needs Python fontTools.
- Matched responsive image `sizes` to portrait, collection, selected-lead, row and case-cover slots, and loaded the first collection image eagerly. Added eight AVIF derivatives of the original portrait and Helixtra capture at 480/640/960/1440px. The fourteen original sources and forty-two WebP variants remain unchanged; WebP stays available as a format fallback.
- Inlined the small stylesheet bundles and preloaded all four font faces used by initial navigation, headings, copy and buttons. These delivery changes preserve the same styles and faces; measured effects belong in the performance report.
- Preserved visible link wording in accessible names and removed filter labels that disagreed with their responsive visible text.
- Allowed long text and header/timeline content to wrap at 320px and doubled text. Moved the hero technology stack into normal flow at smaller widths; normal 390/768/1440px hero, portrait and stack positions match the preceding implementation.
- Constrained the screenshot dialog with flex layout so controls, canvas and instructions fit in short landscape viewports.
- Removed trailing slashes from internal links to match `trailingSlash: 'never'`. Actual card/case/back/contact clicks and filter refresh/history now succeed, as does the complete rendered-link inventory.

The native design SHA-256 remains `c961aadd12e7335a5db33987f019985a29915b84d759f40cf28ef07ba822bc43`. Selected work order, original imagery, approved Blitz demo label, five-role career timeline and original CV bytes remain intact. No deployment or domain change was made.

## Reproduction

Build the site and keep its static preview running on loopback port 4321. With the matching Playwright browsers installed:

```sh
npm run check
npm run lint
npm run test:smoke
npm run test:acceptance
npm run test:media
npm run test:fonts
npm run test:performance -- --label=current
```

Run performance measurements after the acceptance browsers have closed. `npm run test:acceptance -- --links` repeats only the actual-link/filter follow-up and preserves earlier full-matrix timestamps. Rebuild first after source changes; `preview` serves existing files.

The ordinary build stays `noindex`. A separate local build under ignored `output/seo-dist/`, served only on 127.0.0.1:4322, enables `PUBLIC_SITE_INDEXABLE=true` solely to measure the real indexable output. Its home HTML equals the ordinary build except for the robots meta value. This is not a public deployment or a production indexing change.

[Final media checks](phase-4-media.json) passed 54 format/layout scenarios across three engines, three widths and Home/Projects/Helixtra. Chromium and Firefox decode AVIF; the tested Windows WebKit uses its working WebP fallback. Forcing the optional AVIF sources out of navigation HTML also verifies real WebP responses/decoding in all three engines. The original fourteen sources and forty-two WebP variants retain their hashes. This pass covers the later picture markup and stylesheet/font-preload delivery changes; the following font pass separately covers the final glyph subset.

## Guard checks

- `home.css` / `index.astro` — removed the confirmed enlarged-text portrait/stack overlap while preserving normal geometry.
- `ProjectImage.astro` / `ProjectCard.astro` — corrected source-size declarations that caused tablet case under-resolution and card overfetch.
- `prepare_web_fonts.py` — renamed WWS family/style metadata in addition to primary/typographic names for the modified font subsets.

clean-code-guard: 3 fixed, 0 flagged for author.

Test Guard reviewed the browser and measurement scripts: real browsers and HTTP responses, behavior assertions, raw Lighthouse results, explicit field-INP and touch-emulation limits. Final Astro checking reported zero errors, warnings or hints; formatting passed; `npm audit --omit=dev --audit-level=high` reported zero production dependency vulnerabilities.

Research filesystem cleanup remains incomplete for the reason already recorded in [the cleanup report](cleanup-report.json). It was not retried or bypassed during this phase.
