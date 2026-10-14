# Fullscreen intro and dropdown release

The user's explicit correction is implemented: a fullscreen AA signature at the viewport center, followed by a smooth site reveal, and a burger dropdown anchored below the header. The previous menu dialog and small header signature are superseded. The [current direction](intro-dropdown-direction.md) records the timing, keyboard/pointer dismissal and no-JavaScript/reduced-motion fallbacks.

Published on 14 October 2026 to the existing Cloudflare Pages production project `ayman-portfolio-v2`, branch `main`. Live site: [aymanashraf.me](https://aymanashraf.me/). Immutable release: [255c86a4](https://255c86a4.ayman-portfolio-v2.pages.dev/). Domain, DNS, TLS, preview configuration, approved imagery and original PDF remain as in the preceding release.

## Verification

- Production build: all 19 routes built. Final Astro check: 42 files, zero diagnostics. Formatting and Git whitespace checks passed.
- [Local browser QA](intro-dropdown-qa.json): 60 unique accepted scenarios across Chromium, Firefox and WebKit, including 12 intro viewport observations and two axe audits with zero violations. Full acceptance was followed by focused repairs and reruns; the record distinguishes those stages.
- Confirmed fullscreen coverage, centered AA, finite cleanup and reveal, initial/runtime reduced motion, early keyboard dismissal, no JavaScript, blocked bundled modules, history navigation, nonmodal dropdown focus flow, landscape scrolling, doubled text, native links and independent image viewing.
- Browser testing caught premature focus-based menu closure during link activation, stale Safari/WebKit focus closure after Escape, and the dropdown exit handler consuming Escape intended for the image viewer. The final implementation closes on settled outside focus, defers anchor-selection cleanup until activation and handles menu Escape only while open. Focused reruns verified all three corrections.
- [Mobile Lighthouse](intro-dropdown-performance.json), measured on the final isolated production artifact with QA browsers closed: Home and Projects performance 99, accessibility/best practices/SEO 100. Home LCP 2.107s/TBT 0ms; Projects LCP 1.956s/TBT 1ms; both CLS 0. These simulated lab navigation results do not establish field INP.
- [Hosted verification](intro-dropdown-hosted-qa.json): six checks passed. Apex and immutable Home/Projects/Contact match the final artifact, indexing and native email are retained, the original PDF hash matches, and native dropdown Contact navigation/Escape/focus restoration work with normal and reduced motion.
- Final code and documentation guard review: clean. No added dependency or client router.

The local real-time 5.72-second review video and fullscreen AA/dropdown screenshots remain under ignored `output/intro-dropdown/`. Automated engines and emulated viewports do not establish physical-device or screen-reader coverage. History and failure-path distinctions are recorded in the QA evidence.
