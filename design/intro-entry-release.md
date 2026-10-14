# Intro on site entry and refresh

The user's latest correction restricts the fullscreen AA animation to direct/external site entry and refresh. Same-origin internal page links and Back/Forward skip it. Refresh overrides an internal referrer, so reloading any route still shows the intro. Reduced-motion and no-JavaScript behavior remain unchanged.

The source change is confined to the inline guard in `src/components/PageMotion.astro`: compare the browser-supplied referrer origin and navigation type before adding `intro-active`. No storage flag, intercepted link, new dependency, menu change or animation timing change is introduced. Code guard review was clean.

Published to [aymanashraf.me](https://aymanashraf.me/) on 14 October 2026 using the existing production Pages project `ayman-portfolio-v2`, branch `main`. Immutable deployment: [226fe316](https://226fe316.ayman-portfolio-v2.pages.dev/).

- [Local focused QA](intro-entry-qa.json): 60 passing scenarios across Chromium, Firefox and WebKit at 390px and 1440px. Real links, fresh deep entry, external entry, refresh after internal navigation, history traversal, reduced motion and navigation without JavaScript passed. Frame samples confirmed no fullscreen intro or concealed content during internal route navigation.
- [Hosted QA](intro-entry-hosted-qa.json): 12 passing Chromium scenarios on the live custom domain, including fresh entry, actual internal navigation through Projects/case/Contact, refresh, Back/Forward, external referral, reduced motion and no-JavaScript navigation.
- Production build: 19 routes. Astro check: 42 files, zero diagnostics. Formatting and whitespace checks passed. Existing performance and visual measurements belong to their preceding release; this focused gate change did not repeat those matrices.

Automated engines and emulated viewport sizes do not establish physical-device or screen-reader coverage. The QA records identify observation methods and history-restoration limits.
