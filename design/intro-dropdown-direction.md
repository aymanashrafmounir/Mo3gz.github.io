# Fullscreen AA intro and header dropdown

The user explicitly requested a full-screen loading animation with AA in the center, followed by a smooth appearance of the site, and a burger dropdown rather than an open dialog. This is the current runtime direction following the earlier [Astra motion debate](motion-direction.md). The approved warm-paper/rust palette, portrait, project imagery, native Figcraft baseline and existing scroll/hover motion remain.

## Intro sequence

`PageMotion.astro` runs a small inline bootstrap before the page content. The user's latest correction restricts `intro-active` to direct/external site entry and explicit refresh, with reduced motion off. Same-origin internal links and history traversal skip the fullscreen intro. A refresh still plays it when the retained referrer is an internal page. The production build already inlines its CSS, so the initial content state is established before its first paint.

- A paper overlay covers the viewport; the rust AA vector sits at the viewport center at 112–152px.
- Ring and signature strokes draw for up to 560ms. At 640ms, the overlay begins a 360ms fade and the site begins a 480ms fade/12px settle. The inline script removes the state at 1200ms.
- The intro is a decorative sequence, with no percentage or claim about actual network progress. It does not wait for fonts, images or application modules.
- Keyboard or pointer input cancels the sequence immediately. Initial or runtime reduced motion exposes content without movement. No JavaScript leaves the overlay absent and content visible. The inline cleanup is independent of bundled modules; page departure also clears it.
- Internal links skip the intro using the browser's same-origin referrer; explicit `reload` navigation overrides that check. There is no storage flag or intercepted link. Native Back/Forward traversal also skips it; restored-document cleanup has separate browser-test limitations.

## Dropdown behavior

`SiteHeader.astro` implements an ordinary navigation disclosure inside the header. Its 48px circular burger morphs into an X. The paper panel is anchored below the header, caps at 360px and scrolls within the available viewport height in short landscapes.

The panel enters in 220ms with a short link stagger and exits in 150ms. Repeated activation, Escape, outside interaction, focus leaving the header, link selection and switching to the desktop breakpoint close it. Escape restores trigger focus; other interactions preserve the user's natural focus destination. Links retain native navigation behavior. The panel has no dialog, backdrop, focus trap or inert background. Reduced motion removes animation and close delay. The existing no-JavaScript navigation fallback remains.

The original image viewer retains its independent native dialog and zoom/pan/pinch behavior. Collection filters retain synchronous URL/count/visibility changes and their existing finite entrance feedback. No new dependency, client router, generated image or automatic Figcraft launch is introduced.

The [release record](intro-dropdown-release.md) links final local browser acceptance, measured performance and hosted verification. Historical failures and focused repair runs are identified separately from final accepted behavior.

The later [entry/refresh correction](intro-entry-release.md) verifies the current condition for showing the intro, with separate focused local and hosted browser evidence.
