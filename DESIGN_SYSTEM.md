# Ayman Portfolio V2 design handoff

**Selected direction A:** on 14 October 2026 the user chose the warm light background and rust palette, with their original portrait and approved project imagery. That direction is now applied to all responsive native screens. The rejected blue/3D iteration is preserved in `design/rejected-v1/`.

The user approved the complete design and final application imagery on 14 October 2026. The native file was saved and verified inside the repository before Phase 3 frontend implementation began. The approved hero, colors and Mona Sans typography remain. [The approved handoff](design/approved-handoff.json) records the canonical native SHA256, assets and checks. The Astro implementation has separate Phase 4 local browser/performance evidence and a user-authorized [Phase 5 hosted review preview](design/phase-5-preview.md). After reviewing that preview, the user requested link icons and explicitly approved the [production release](design/production-release.md) to [aymanashraf.me](https://aymanashraf.me); the saved native baseline remains unchanged.

## Source of truth

- Editable document: `design/ayman-portfolio-v2.figcraft`; approval and immutable baseline hash: [design/approved-handoff.json](design/approved-handoff.json).
- Screen exports and review index: `design/README.md` and `design/screens/`.
- Frame IDs, viewport widths, heights and export paths: `design/screen-manifest.json`.
- Native layer inspection: `design/screen-inspection.json`.
- Screen-level verification: `design/screen-qa.json`.
- Active media classification, dimensions, permissions and responsive variants: `design/selected-media-manifest.json`. Rejected generated art remains recorded separately in `design/asset-manifest.json` and is not used.
- Editable technology/social component IDs: `design/technology-components.json`; source SVGs, MIT license and provenance: `design/assets/icons/`.
- Factual qualification and publication limits: `PROJECT_CONTENT.md`.

These deliverables were authored through the real Figcraft 0.5.1 MCP server and exported with its native renderer. Screens contain editable text, image fills, frames, components and instances. The screens are native editable layouts. One embedded project image is the separately classified, user-approved AI-edited BlitzChatbot demo; its contacts and chat are fictional.

## Color

| Token           | Value     | Purpose                                           |
| --------------- | --------- | ------------------------------------------------- |
| Paper           | `#F5F2EC` | Page background and primary button text           |
| Surface         | `#EEE7DE` | Tags and quiet contained surfaces                 |
| Foreground      | `#26251F` | Headings and primary text                         |
| Secondary       | `#645D53` | Descriptions and navigation                       |
| Quiet           | `#70675D` | Small image captions                              |
| Rust            | `#AE3A24` | Primary actions, project labels and active filter |
| Focus           | `#8B2F20` | Keyboard outline and professional metadata        |
| Line            | `#D4C9BC` | Decorative dividers and secondary outlines        |
| Primary hover   | `#922E1D` | Hover state                                       |
| Primary pressed | `#762517` | Pressed state                                     |

Text contrast against Paper measures 13.75:1 for Foreground, 5.81:1 for Secondary, 4.96:1 for Quiet, 5.48:1 for Rust and 7.44:1 for Focus. Paper text on Rust also measures 5.48:1. All project labels use Rust; authentic branding remains inside genuine captures. Treat Line as decoration and retain clear control labels/focus. Actual browser accessibility and focus behavior still require implementation QA.

## Typography

Mona Sans Regular, Medium, SemiBold and Bold are retained with their OFL license in `design/assets/fonts/`. They were registered as current-user fonts so the native design engine could render the actual family.

Web delivery uses prebuilt Latin-1/punctuation subsets with the same retained outlines and metrics, stored in `design/assets/fonts/web/`. The OFL reserves “Mona”, so the modified subsets are named **Ayman Sans Web**; this changes their identity, not the approved letterforms. Four web faces total 145,204 bytes. `coverage.json` records retained glyphs, codepoints and source/output hashes. The Node preparation step checks source/content coverage and copies these files; regular builds do not require Python. For regeneration, install Python fontTools and locked npm dependencies, then run `python design/.tools/prepare_web_fonts.py`. The original full TTFs and OFL notice stay unchanged.

Homepage display: 80px desktop, 60px tablet and 46px mobile. Collection and information-page headings use 68px desktop and 46–48px at smaller widths. Case titles use 60/46/38px. Section headings use 28–40px according to their hierarchy. Reading text uses 18–22px; metadata uses 14–16px. Large display type uses 1.25 line height; smaller text uses approximately 1.42. Long text determines section height; fixed offsets must not cause wrapped headings to overlap content.

Use responsive type sizing in implementation. Preserve readable line lengths rather than scaling an entire desktop frame down to mobile. Typeface weights and page heading hierarchy should remain consistent with the exports.

## Layout and image treatment

Reference widths are 1440, 768 and 390px, with horizontal margins of 80, 40 and 24px. Desktop content width is 1280px. These are design anchors, not an assertion that intermediate widths have passed browser tests.

The desktop homepage follows direction A's left-aligned name/actions and unchanged 360×480px portrait. Selected work appears in this order: Helixtra, Wear Instant, BlitzChatbot and Secure Notes Organizer. BlitzChatbot uses its approved AI-edited main-chat demo with fictional contacts/messages; Secure Notes uses its original Qt notes editor with C++/Qt marks. Arkedia and Tapora remain in the full collection and their case studies. Tablet and mobile stack identity, portrait and reading sections, preserving the portrait's 3:4 aspect ratio. Captured projects use three/two/one collection columns.

Desktop case studies use a 210px section-navigation area and a reading column capped at 800px. Smaller widths use one column. All twelve retain their own content; the portfolio's accent is consistently Rust. Secure Notes uses its original notes editor as the collection and case-hero cover, with its sign-in screen in the case gallery at all three widths. Terminal captures are excluded. Supported contribution sections appear only where the evidence allows them. Career dates retain overlapping roles. Resume content includes Hala Kazim as CV project experience without inventing a thirteenth dedicated case study.

Experience uses a vertical timeline on the homepage, Experience and Resume at 1440, 768 and 390px. All nine timeline blocks contain the same five roles. Original dates and overlaps are preserved.

Use 6px image/button corners and 8px tag corners; larger gallery containers retain 12px corners. Generate spacing from measured text and shared rhythm. Native frames demonstrate the composition; frontend layout should use normal flow/grid/flex rather than copying every absolute coordinate.

Active imagery consists of 14 assets: 13 genuine photographs/captures and one approved AI-edited BlitzChatbot demo. They have 42 WebP copies targeting 480/960/1440px, capped at source resolution. Source hashes and classification are preserved in the selected media and capture manifests. Terminal screenshots and the earlier rejected thirteen-image illustration series are excluded from current screens. Keep the rejected thirteen-image series, native exports, logs and archive outside deployed assets. Use descriptive alt text, avoiding repeated nearby descriptions.

Seven live sites were recaptured at 1440×1000, DPR 1, after at least 12 seconds plus font and image decoding. Maysa's media loaded after about 23 seconds. Complete captures are fitted without zoom or crop. Additional genuine UI captures show Cheque Printer's empty form, Artline's unchanged locally rendered frontend, Quantitator's upload/configuration interface and Secure Notes' original Qt editor/sign-in screens. Quantitator shows inputs, not achieved business results. The genuine captures show no customer contacts, financial records or personal notes; Maysa couture media and private-project disclosure remain subject to publication review in the evidence ledger.

BlitzChatbot's approved main-chat image is an image-generator edit of the original empty interface. It includes six fictional Arabic contacts and a generic fictional exchange, with the visible “بيانات تجريبية” disclosure. Its case caption says “AI-edited demo”. The [approved provenance](design/provenance/blitzchatbot/approved-demo.json) links the original blank base, exact prompt and capture audit. Preserve this classification in implementation and alt/caption text; it does not verify real messaging or populated account workflows.

The user approved genuine Secure Notes application imagery and its Siemens Digital Industries Software (DISW) internship affiliation. Repository About and the six-author README support an internship team final project. This does not establish corporate ownership, endorsement or official product status.

The original C++/Qt widgets, resource assets and QSS were rebuilt from commit `bee56c5cd8de4504fd601f090c12145ec5be234e` in isolated Docker with Qt 6.4. Original files remain hash-identical. A separate capture harness opens the original offline editor and clears account inputs; a separate compatibility header adapts debug logging. The resulting editor and sign-in captures contain no notes or credentials. Backend authentication and saved-note workflows were not verified. `design/secure-notes-application-provenance.json` records the build and source verification; the capture and selected-media manifests record final image hashes, captions and variants.

## Components and behavior

The native document has six shared paint styles, four text styles, primary/secondary button components and hover/pressed/disabled examples with editable labels. Foundations also shows keyboard focus and a separate board of 18 editable Devicon SVG components. `design/assets/icons/LICENSE` retains MIT terms; `provenance.json` records each source, and trademark terms still apply to the marks.

Java, Spring Boot, TypeScript and Cloudflare form the compact core stack. Project summaries use at most three evidence-backed stack labels; the complete stack remains in project content. Skills are grouped by backend, frontend, data/persistence, cloud/infrastructure, testing/quality and architecture/collaboration. Text labels remain alongside marks. Active navigation uses an underline; GitHub/LinkedIn marks and directional arrows clarify links. The final user-requested implementation update uses shared `LinkIcon.astro` marks on Contact, footer and project actions: the existing GitHub/LinkedIn SVG assets plus email and external-link SVGs. Icons are decorative beside visible link labels and do not replace accessible link names.

The comparison and requested Astra debate supported retaining the approved personal hero while improving technical scanning and reading depth. Selective stack labels avoid overwhelming project summaries, grouped skills organize breadth, and the 800px case body keeps longer explanations readable.

Primary actions are 52px high, filter controls 48px and navigation targets at least 44px. Focus uses a visible 2px deep-rust outline with 4px separation. The disabled example has no interaction. Secondary controls must retain clear text and focus treatment.

The native prototype connects route navigation, filters, previous/next case studies, section anchors, external links, mailto and the original CV. It has three homepage flows, one per viewport. The final `design/screen-qa.json` records 852 prototype actions and no issues; active imagery is checked from current document fills and hashes.

The mobile/tablet menu has an explicit open state in the saved native prototype. The user's latest browser refinement replaces the prototype overlay with a dropdown anchored below the header: a 48px burger morphs into X, Escape returns focus to the trigger, and outside interaction, focus departure or link selection closes the list. The dropdown has no modal behavior or focus trap. Existing enlarged Helixtra public-marketing gallery states remain at all three widths.

Case-hero and Secure Notes gallery image actions open full-size local PNGs in the native prototype; BlitzChatbot's action explicitly identifies its AI-edited demo. The implemented site must serve public image URLs and support accessible enlargement, zoom and touch pinch, with lightbox close/Escape handling and focus returned to the trigger. Those browser interactions are requirements, not claimed native test results.

Collection filters have All, Products & Client Work, and Public Repositories states at each width. In implementation, retain shareable URL state and a useful no-JavaScript collection. Public website/public code buttons follow the per-project ledger. The CV prototype opens the local original file; the website must provide an actual same-origin PDF URL/download response.

The user's latest motion refinement uses a fullscreen paper background and centered rust AA signature. The logo draws for up to 560ms; the overlay fades from 640–1000ms while the site reveals from 640–1120ms, with inline cleanup at 1200ms. Keyboard or pointer input dismisses it immediately. Reduced motion and history Back skip the intro, and content stays visible without JavaScript. The attached dropdown enters in 220ms and exits in 150ms; existing once-only section/card/timeline entrances and hover details remain. See the [intro and dropdown direction](design/intro-dropdown-direction.md). No endless animation, availability indicators, skill percentages or unsupported business metrics.

## Coverage and verification limits

All nineteen routes have desktop/tablet/mobile designs: 57 route frames. Eleven additional frames cover six filtered collections, two menu states and three enlarged-gallery states. All 68 screen exports were refreshed while retaining their frame IDs. Foundations boards are separate from those screen frames.

Geometry verification found zero text overlaps, text overflow, content-margin violations or invalid cross-viewport prototype destinations in the final native inspection. Representative exported screens were also visually reviewed, including home at all three widths, collection, case studies, resume, contact, menu, error page and foundations. The saved document was reopened successfully through MCP, confirming its pages, image resources and shared styles persist.

These are design-verification results. The static Astro 7.3.8 implementation has Tailwind CSS 4, twelve schema-validated project entries and all nineteen routes building. Website behavior, PDF serving, real HTTP 404s, responsiveness and accessibility have separate [Phase 4 evidence](design/phase-4-verification.md); [performance measurements](design/phase-4-performance.md) state their lab/field limits. The isolated Phase 5 review preview has [remote acceptance evidence](design/phase-5-preview-qa.json). The later user-authorized [production release](design/production-release.md) has separate build and deployment evidence; it does not change the native-design verification scope.

## Figcraft connection

After the user selected direction A and explicitly requested local MCP viewing, the Codex server configuration was changed to `figcraft-cli.exe mcp --attach 47800`. Initialize confirmed attachment to the local Figcraft app. The GUI was started visibly with `--control 47800` for that explicit request; no automatic GUI launcher or startup hook was added. The existing authoring scripts can still use the headless engine for offline exports.

The latest user-requested review uses a dedicated local Figcraft app connection on loopback, shown through attached MCP with separate timeline and Selected work tabs. The configured 47800 session was left unchanged. The user subsequently approved the timeline, Selected work and final application-image corrections, including the BlitzChatbot fictional demo.

Figcraft tools were used for the A/B/C studies. Responsive authoring used an explicit headless MCP client. `design/figcraft-mcp-calls.json` records those authoring calls; `design/attached-mcp-calls.json` and `design/attached-ui.json` record the live attached viewing session. `show_in_figcraft.py` opens the selected direction A document and frames the desktop homepage through attached MCP. The live window screenshot is `design/screens/figcraft-app.png`. All design actions remain native Figcraft MCP operations.

## Implementation correspondence

`astro.config.mjs` selects static output. `src/content.config.ts` validates `src/content/projects.json`, generated from approved `design/screen-content.json` by `scripts/prepare-content.mjs`. The same preparation step copies the fourteen selected media assets and 42 WebP variants, local fonts/icons, unchanged original CV and share image to public assets. Rejected artwork, native archives and research directories are outside the public asset selection.

The implementation uses normal-flow components, a five-role career timeline, URL-backed collection filters, dropdown navigation and native dialog-based image viewing. Browser behavior is validated separately from this native baseline. The dedicated preview build forces noindex and applies a global noindex response header; the ordinary build indexes eligible pages only when `PUBLIC_SITE_INDEXABLE` is explicitly `true`. The approved production helper forces that value for its separate artifact and uses `https://aymanashraf.me` as the site origin. The existing review project remains isolated; production is deployed on the separate `ayman-portfolio-v2` project after explicit user approval.
