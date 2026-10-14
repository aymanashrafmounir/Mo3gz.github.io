# Motion refinement and Astra debate

The user requested an icon-only hamburger, a more professional menu, an animated reload experience and visibly richer animation throughout the portfolio. This update extends the approved warm-paper/rust design with motion; the editable Figcraft baseline and approved imagery remain the saved reference.

The implementation direction was debated with **GPT-6 Astra**. The initial proposal included an opaque 450ms loading screen. Astra challenged the artificial wait, potential LCP delay and dependence on JavaScript/font readiness. The accepted direction uses a conspicuous **AA signature and rust stroke in the header band**, with readable content and immediate interaction throughout. AA represents Ayman Ashraf.

The second debate resolved how to make the whole site feel more animated without adding a client router. Native document navigation and existing per-document scripts preserve the site's working links, downloads, filters and image viewer. A progressive cross-document transition was implemented, then removed after browser QA reproduced a WebKit crash when navigating from the open menu and rotating the viewport. Disabling only that transition fixed the reproduction; canceling menu animations did not. Page-lead settling still introduces each new page. The implementation omits a separate navigation indicator and does not intercept or postpone clicks.

## Accepted motion language

| Surface | Treatment | Timing |
| --- | --- | --- |
| Open/reload | AA signature and rust stroke, decorative and nonblocking | 480–600ms |
| Page navigation | Ordinary browser navigation; the incoming page lead settles without hiding its text | 480ms |
| Hero/page lead | Immediately readable text settles up to 12px; portrait settles from at most 1.015 scale | 480–600ms |
| Sections, project cards, career roles | Once-only entrance; short sibling stagger with no nested parent/child reveal | 420–520ms; stagger capped at 180ms |
| Burger/menu | 48px icon target; native dialog entrance and separate accessible X control | 240ms enter; up to 160ms exit |
| Buttons, links and media | Small lift, arrow movement, growing underline and modest image scale on appropriate hover devices | 160–350ms |
| Project filters | URL, count and visibility update immediately; entering cards animate afterward | 220–280ms |
| Image viewer | Animate the shell independently of screenshot pan, pinch and zoom | About 180ms |

## Interaction and accessibility contract

- Main content is visible by default, including when scripts fail or JavaScript is disabled. There is no loading gate, fake percentage, font/image wait or opaque full-page overlay.
- The decorative AA seal is omitted if enlarged text leaves insufficient header space; it never covers the wordmark or navigation controls.
- The hamburger has an accessible name, expanded state and a native modal target. Escape, close control and backdrop use one close path; focus returns after the dialog actually closes. Focused menu items remain visible during staggered entrances.
- Scroll entrances use IntersectionObserver and finite animations. Elements stop being observed after entrance; focus and anchor access must not leave content concealed.
- Filter state changes synchronously. Motion follows the existing filter function's explicit event rather than a DOM-wide mutation observer.
- Download, mailto, external, targeted, modified-click and same-document anchor behavior stays native. Page history and BFCache restore cancel active entrance animations without replaying a loading state.
- Reduced motion bypasses startup, scroll, navigation, menu and hover movement. A runtime preference change cancels active animations and any pending close delay.
- No animation library, replacement router, scroll hijacking, continuous decorative motion or new generated imagery is needed.

The [release record](motion-release.md) links the final browser, performance and hosted verification evidence. Checks cover real menu interaction, route changes, filters/history, no-JavaScript behavior, reduced-motion changes, image controls and representative responsive/performance behavior. Saved performance measurements describe their actual revision and lab conditions.

References: [Impeccable animate guidance](C:/Users/sigma/.agents/skills/impeccable/reference/animate.md), [MDN cross-document view transitions](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API/Using), and [Astro script behavior with client routing](https://docs.astro.build/en/guides/view-transitions/#script-behavior-with-view-transitions). The latter informs the decision to keep ordinary document navigation.
