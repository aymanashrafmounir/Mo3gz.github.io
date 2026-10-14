# Ayman Portfolio V2 design handoff

**Superseded image/color direction:** the user rejected this iteration on 14 October 2026, citing its images and palette. This document records the rejected treatment and previous verification; it is not the current visual implementation target. Retain the content and technical scope while a replacement image/color direction is selected.

Native screens completed on 14 October 2026, before frontend implementation. The design follows the approved dark blue/cyan direction and uses the supplied career information and twelve-project evidence ledger.

## Source of truth

- Editable document: `design/ayman-portfolio-v2.figcraft`.
- Screen exports and review index: `design/README.md` and `design/screens/`.
- Frame IDs, viewport widths, heights and export paths: `design/screen-manifest.json`.
- Native layer inspection: `design/screen-inspection.json`.
- Screen-level verification: `design/screen-qa.json`.
- Original asset prompts, dimensions, permissions and responsive variants: `design/asset-manifest.json`.
- Factual qualification and publication limits: `PROJECT_CONTENT.md`.

These deliverables were authored through the real Figcraft 0.5.1 MCP server and exported with its native renderer. Screens contain editable text, image fills, frames, components and instances. They are not AI-generated UI screenshots.

## Color

| Token | Value | Purpose |
| --- | --- | --- |
| Ink | `#10151D` | Page background and dark button text |
| Surface | `#19222D` | Tags and quiet contained surfaces |
| Foreground | `#E8EEF4` | Headings and primary text |
| Secondary | `#A7B5C6` | Descriptions and navigation |
| Quiet | `#7E93AA` | Small illustration captions |
| Signal blue | `#5D9EFF` | Primary actions and active filter |
| Cyan | `#67D8E4` | Focus and professional labels |
| Line | `#354354` | Dividers and secondary outlines |
| Primary hover | `#82B4FF` | Hover state |
| Primary pressed | `#4389ED` | Pressed state |

Text contrast against Ink measures 15.66:1 for Foreground, 8.78:1 for Secondary and 5.79:1 for Quiet. All twelve project accent colors exceed 4.5:1 against Ink. Treat Line as decoration; do not rely on its contrast alone to identify a control. Actual browser accessibility and focus behavior still require implementation QA.

## Typography

Mona Sans Regular, Medium, SemiBold and Bold are retained with their OFL license in `design/assets/fonts/`. They were registered as current-user fonts so the native design engine could render the actual family.

Homepage display: 78px desktop, 60px tablet and 46px mobile. Collection and information-page headings use 68px desktop and 46–48px at smaller widths. Case titles use 60/46/38px. Section headings use 28–40px according to their hierarchy. Reading text uses 18–21px; metadata uses 14–16px. Line height is approximately 1.42. Long text determines section height; fixed offsets must not cause wrapped headings to overlap content.

Use responsive type sizing in implementation. Preserve readable line lengths rather than scaling an entire desktop frame down to mobile. Typeface weights and page heading hierarchy should remain consistent with the exports.

## Layout and image treatment

Reference widths are 1440, 768 and 390px, with horizontal margins of 80, 40 and 24px. Desktop content width is 1280px. These are design anchors, not an assertion that intermediate widths have passed browser tests.

The desktop homepage pairs left-aligned identity and useful actions with one large artwork. Selected work gives Helixtra greater visual emphasis, followed by Wear Instant and compact Arkedia/Tapora entries. Tablet and mobile stack the identity, artwork and reading sections. The collection uses three, two and one columns respectively.

Desktop case studies use a 210px section-navigation area and a wider reading column. Smaller widths use one column. All twelve case studies have their own content and accent; supported contribution sections appear only where the evidence allows them. Career dates retain overlapping roles. Resume content includes Hala Kazim as CV project experience without inventing a thirteenth dedicated case study.

Use 16px image corners, 10px button corners and 8px tag corners. Generate spacing from measured text and shared rhythm. Native frames demonstrate the composition; frontend layout should use normal flow/grid/flex rather than copying every absolute coordinate.

All thirteen generated assets are conceptual illustrations. Each has an original PNG and 480/960/1440px WebP variants. Keep masters, authoring logs and design exports outside deployed assets. Use descriptive alt text or empty alt when adjacent text already communicates a purely decorative cover.

Six genuine public-site captures are included for local design review. They remain separate from conceptual artwork. Maysa couture media needs publication review; patient/customer/financial records and private application screenshots are absent. Apply the evidence ledger before choosing public gallery media.

## Components and behavior

The native document has six shared paint styles, four text styles, primary/secondary button components and hover/pressed/disabled component examples. Eighty-three button instances use editable label properties. The foundation board also shows a keyboard-focus treatment.

Primary actions are 52px high, filter controls 48px and navigation targets at least 44px. Focus should use a visible 2px cyan outline with 4px separation. The low-contrast disabled example has no interaction. Secondary controls must retain clear text and focus treatment.

The native prototype connects route navigation, filters, previous/next case studies, section anchors, external links, mailto and the original CV. It has three homepage flows, one per viewport, with 772 native prototype actions whose destinations were inspected.

The mobile/tablet menu has an explicit open state. Its design prototype Close action returns to the homepage; the implemented menu should close in place, restore focus to its trigger, handle Escape and keep focus within the open overlay. The gallery prototype shows an enlarged Helixtra public-marketing capture at all three widths; implementation should return focus to its image trigger after closing. These keyboard interactions are implementation requirements, not claimed native test results.

Collection filters have All, Products & Client Work, and Public Repositories states at each width. In implementation, retain shareable URL state and a useful no-JavaScript collection. Public website/public code buttons follow the per-project ledger. The CV prototype opens the local original file; the website must provide an actual same-origin PDF URL/download response.

Use short transform/opacity feedback, around 150–200ms, and at most one restrained hero entrance. Reduced motion removes the entrance, scrolling animation and image movement. Essential navigation must work without motion. No endless animation, availability indicators, skill percentages or unsupported business metrics.

## Coverage and verification limits

All nineteen routes have desktop/tablet/mobile designs: 57 route frames. Eleven additional frames cover six filtered collections, two menu states and three enlarged-gallery states. The foundation board is separate from those 68 screen frames.

Geometry verification found zero text overlaps, text overflow, content-margin violations or invalid cross-viewport prototype destinations in the final native inspection. Representative exported screens were also visually reviewed, including home at all three widths, collection, case studies, resume, contact, menu, error page and foundations. The saved document was reopened successfully through MCP, confirming its pages, image resources and shared styles persist.

This is design verification. Website behavior, PDF serving, real HTTP 404s, browser responsiveness, keyboard accessibility and Lighthouse performance remain Phase 3/4 work. No frontend application, preview deployment or production change was made in this phase.

## Figcraft connection

The existing Codex Figcraft server now runs the installed `figcraft-cli.exe mcp` command. Its initialize response confirms a headless in-process engine with no window. No GUI launcher or auto-start hook was added. The authoring tools in `design/.tools/` use the discovered MCP JSON-RPC tools and do not start the desktop GUI.

The live tool catalog of the already-running chat did not reload the newly enabled server, so authoring used the same actual MCP server through an explicit stdio client. `design/figcraft-tool-discovery.json` records its reported backend and schemas; `design/figcraft-mcp-calls.json` records successful authoring calls. A fresh Codex tool session may be needed to expose the configured server directly in the app's tool list.
