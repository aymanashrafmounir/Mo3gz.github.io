# Phase 4 performance measurements

The measured representative local lab targets pass on 14 October 2026: mobile Performance **99–100**, Accessibility and Best Practices **100**, mobile LCP **1.881–2.257 s**, and CLS **0**. Six separate SEO audits score **100** on the genuine isolated indexable build. The normal preview deliberately remains `noindex` and its raw SEO score remains **69**. INP field acceptance remains unmeasured.

## Final measurements

Lighthouse 13.5.0 used Playwright 1.63.0's Chromium 153. Mobile runs use default simulated throttling (412 × 823 viewport, 1.75 DPR, 4× CPU slowdown); the desktop run uses Lighthouse's desktop preset. The eight navigation audits cover seven distinct routes. Each row is a measured run, not a median or a production/field result.

| Page / preset                   | Performance | Accessibility | Best Practices | Preview SEO |     LCP | CLS |  TBT |
| ------------------------------- | ----------: | ------------: | -------------: | ----------: | ------: | --: | ---: |
| Home / mobile                   |          99 |           100 |            100 |          69 | 1.956 s |   0 | 3 ms |
| Home / desktop                  |         100 |           100 |            100 |          69 | 0.426 s |   0 | 0 ms |
| Projects / mobile               |          99 |           100 |            100 |          69 | 1.956 s |   0 | 0 ms |
| BlitzChatbot / mobile           |         100 |           100 |            100 |          69 | 1.881 s |   0 | 4 ms |
| Secure Notes Organizer / mobile |         100 |           100 |            100 |          69 | 1.882 s |   0 | 3 ms |
| Resume / mobile                 |         100 |           100 |            100 |          69 | 1.881 s |   0 | 0 ms |
| Supreme Sparkle / mobile        |          99 |           100 |            100 |          69 | 2.257 s |   0 | 0 ms |
| Arkedia / mobile                |          99 |           100 |            100 |          69 | 2.183 s |   0 | 6 ms |

All eight runs meet Performance ≥90, Accessibility/Best Practices ≥95, LCP ≤2.5 s and CLS ≤0.1. Their raw JSON/HTML and summary are in ignored `output/lighthouse/final-verified/`. [The compact tracked record](phase-4-performance.json) preserves exact values, targets, environment, final HTML hashes and raw paths.

SEO was measured separately against `http://127.0.0.1:4322`, serving an actual static build created with `PUBLIC_SITE_INDEXABLE=true` in `output/seo-dist/`. All six SEO audits (Home mobile/desktop, Projects, BlitzChatbot, Secure Notes and Resume; five distinct routes) score **100**. Raw reports are in `output/lighthouse/indexable-seo/`. The normal `http://127.0.0.1:4321` build still contains `noindex, nofollow`; its only failed weighted SEO audit is `is-crawlable`. No indexing audit was excluded or rewritten to derive the passing score. The temporary port 4322 server was stopped after measurement; its build remains in `output/seo-dist/`. The user preview on port 4321 remains running. Neither build was deployed.

## Improvement and evidence

Home mobile improved from **78 / 4.967 s LCP** to **99 / 1.956 s**. Projects mobile improved from **78 / 4.962 s** to **99 / 1.956 s**. Home mobile transfer fell from **762,762 to 268,671 bytes** (64.78%); these are observed local transfer sizes, not source-file totals or production estimates.

The four original TTFs remain intact for the native design. Web delivery uses derivatives of their original Mona Sans outlines, renamed **Ayman Sans Web** under the retained OFL license. Their combined file size fell from 568,556 bytes to 145,204 bytes through WOFF2 compression and a content-appropriate subset. Baseline font transfer was 569,836 bytes; final transfer was 146,484 bytes, including response overhead. The build checks character coverage. [Font regression QA](phase-4-fonts.json) records 5,076 text advance comparisons with **0 px difference** from the full originals and 36 passing geometry checks across Chromium, Firefox and WebKit; [the final metadata check](phase-4-font-metadata.json) verifies the final rename preserved every table except names and the checksum header. [Coverage and provenance](assets/fonts/web/coverage.json) distinguish retained subset glyphs from the full original fonts.

Other implemented changes provide accurate responsive image sizes, eager loading for the first collection image, inline critical CSS, preloads for the four initially used font weights, and AVIF alternatives for the original portrait/Helixtra images with WebP fallback. Approved original images and 42 WebP variants remain. CSS inlining and font preloading improved FCP; AVIF reduced transferred image bytes. Those intermediate changes alone left Home/Projects LCP near 2.556 s. The measured font subset brought both below the LCP target. Raw intermediate results remain under `output/lighthouse/optimized/`, `inlined-initial/`, `preloaded-initial/`, `avif-initial/` and `subset-initial/`; the compact record retains these stages. The earlier `final/` reports precede the last font metadata correction and are not the final evidence.

The baseline's unweighted label/name mismatches in “Read case study” links and the “Public code” filter are corrected; the corresponding final audits pass. A score of 100 does not certify manual accessibility criteria.

## Reproduction

Install locked dependencies, build the site and run the local static preview using the commands in the [repository README](../README.md). With the preview running, run the six default representative audits:

```sh
node scripts/lighthouse-audit.mjs --label=current
```

The script runs audits sequentially and writes raw JSON/HTML plus a summary under ignored `output/lighthouse/current/`. It selects the installed Playwright Chromium binary through `CHROME_PATH` and uses a temporary browser profile. To repeat the final eight-audit scope:

```sh
node scripts/lighthouse-audit.mjs --label=final-repeat --cases=home-mobile,home-desktop,projects-mobile,blitzchatbot-mobile,secure-notes-mobile,resume-mobile,supreme-sparkle-mobile,arkedia-mobile
```

With an independently built and running local indexable server on port 4322, repeat the six SEO-only audits:

```sh
node scripts/lighthouse-audit.mjs --base=http://127.0.0.1:4322 --label=seo-repeat --categories=seo
```

Do not rebuild served files or run other browser workloads during performance measurement. The SEO command does not create or change the indexable build.

## Limits

Navigation Lighthouse does not measure INP. TBT of 0–6 ms does not establish the INP ≤200 ms field target. Production network, cache headers, HTTPS delivery and real visitor interaction distributions remain unmeasured. These representative audits do not establish every page/device combination, and scores can vary across runs and hosts.

Method references: [official Lighthouse CLI](https://github.com/GoogleChrome/lighthouse/blob/main/readme.md), [performance scoring and variability](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring), [INP measurement](https://web.dev/articles/inp).
