# Hamburger navigation and motion release

The user's post-release request replaces the text Menu control with a three-stroke hamburger and adds a polished native menu, animated AA arrival/reload signature, page-lead settling, once-only card/section/timeline entrances, filter feedback, hover details and viewer entrance motion. The direction was debated with GPT-6 Astra; [the decision record](motion-direction.md) describes the result and the WebKit transition issue discovered during QA.

Published to the existing Cloudflare Pages production project `ayman-portfolio-v2`, branch `main`, on 2026-10-14. The live site is [aymanashraf.me](https://aymanashraf.me/); the immutable release is [a27a7ae4](https://a27a7ae4.ayman-portfolio-v2.pages.dev/). This release uses the existing domains and does not change the preview configuration.

## Verification

- Production build: all 19 routes built. Astro check: 42 files, zero errors, warnings or hints. Formatting passed.
- [Local browser acceptance](motion-qa.json): 126 passing checks, 60 route/viewport observations, 11 homepage widths, Chromium/Firefox/WebKit, five axe scans with zero violations. Covers keyboard/focus, short landscape navigation, filters/history, no JavaScript, reload/scroll motion, runtime reduced motion and emulated touch image controls.
- [Measured mobile Lighthouse results](motion-performance.json), on the isolated final production artifact after QA browsers closed: Home and Projects performance 99; accessibility, best practices and SEO 100. Home LCP 2.106s, TBT 61ms; Projects LCP 1.958s, TBT 0ms. Both CLS 0. These are simulated lab navigation measurements; field INP was not measured.
- [Hosted checks](motion-hosted-qa.json): apex and immutable release match the final Home/Projects/Contact artifact; indexing and original PDF hash preserved. Live 390px hamburger, Home current state, Escape/focus restoration, Contact navigation and reduced motion passed. The normal user Chrome session also opened the published homepage successfully.
- Code review resolved an animation cancellation tracking race and the Home current-page marker. `clean-code-guard: 2 fixed, 0 flagged for author.`

Browser QA caught and verified fixes for a decorative AA overlap with doubled text and a WebKit native cross-document transition crash. The optional cross-document transition was removed; ordinary document navigation and incoming page motion remain. The seal is omitted if the actual header lacks clear space. Main content is visible throughout and the menu retains native dialog focus handling.

Automated engines and touch emulation do not establish physical-device or screen-reader coverage. Actual Back navigations used fresh documents in this run; a separately dispatched persisted `pageshow` tested cleanup, without claiming native BFCache restoration. Full local real-time desktop/mobile recordings remain under ignored `output/motion/`.
