# Native Figcraft screen review

**Rejected visual direction:** on 14 October 2026 the user identified the imagery and palette as not representing them. The screens and generated artworks linked below are retained as a record of that iteration. Do not implement their image/color treatment. New direction explorations are separate from this rejected document.

[Review the new image and palette options](directions/README.md). No replacement has been selected yet.

Completed 14 October 2026: 13 conceptual assets, 57 route frames, 11 interaction-state frames and one foundation board. No frontend implementation or deployment has started.

[Editable native document](ayman-portfolio-v2.figcraft) | [Design handoff](../DESIGN_SYSTEM.md) | [Verification results](screen-qa.json)

Figcraft MCP is configured as a headless native engine. Open the native file manually in Figcraft when you want to edit or inspect the prototype. Authoring did not launch its GUI. The document has separate Foundations, Desktop, Tablet and Mobile pages, with a homepage prototype flow on each viewport page.

## Quick previews

[Desktop homepage, first fold](screens/home-preview-1440.png) | [Mobile homepage, first fold](screens/home-preview-390.png) | [Foundations and button states](screens/foundations.png)

## Route screens

| Route | Desktop 1440 | Tablet 768 | Mobile 390 |
| --- | --- | --- | --- |
| `/` | [PNG](screens/home-1440.png) | [PNG](screens/home-768.png) | [PNG](screens/home-390.png) |
| `/projects` | [PNG](screens/projects-1440.png) | [PNG](screens/projects-768.png) | [PNG](screens/projects-390.png) |
| `/projects/helixtra` | [PNG](screens/project-helixtra-1440.png) | [PNG](screens/project-helixtra-768.png) | [PNG](screens/project-helixtra-390.png) |
| `/projects/wear-instant` | [PNG](screens/project-wear-instant-1440.png) | [PNG](screens/project-wear-instant-768.png) | [PNG](screens/project-wear-instant-390.png) |
| `/projects/ibrahim-awad` | [PNG](screens/project-ibrahim-awad-1440.png) | [PNG](screens/project-ibrahim-awad-768.png) | [PNG](screens/project-ibrahim-awad-390.png) |
| `/projects/tapora` | [PNG](screens/project-tapora-1440.png) | [PNG](screens/project-tapora-768.png) | [PNG](screens/project-tapora-390.png) |
| `/projects/maysa-waheed` | [PNG](screens/project-maysa-waheed-1440.png) | [PNG](screens/project-maysa-waheed-768.png) | [PNG](screens/project-maysa-waheed-390.png) |
| `/projects/supreme-sparkle` | [PNG](screens/project-supreme-sparkle-1440.png) | [PNG](screens/project-supreme-sparkle-768.png) | [PNG](screens/project-supreme-sparkle-390.png) |
| `/projects/blitzchatbot` | [PNG](screens/project-blitzchatbot-1440.png) | [PNG](screens/project-blitzchatbot-768.png) | [PNG](screens/project-blitzchatbot-390.png) |
| `/projects/arkedia` | [PNG](screens/project-arkedia-1440.png) | [PNG](screens/project-arkedia-768.png) | [PNG](screens/project-arkedia-390.png) |
| `/projects/cheque-printer` | [PNG](screens/project-cheque-printer-1440.png) | [PNG](screens/project-cheque-printer-768.png) | [PNG](screens/project-cheque-printer-390.png) |
| `/projects/artline` | [PNG](screens/project-artline-1440.png) | [PNG](screens/project-artline-768.png) | [PNG](screens/project-artline-390.png) |
| `/projects/quantitator` | [PNG](screens/project-quantitator-1440.png) | [PNG](screens/project-quantitator-768.png) | [PNG](screens/project-quantitator-390.png) |
| `/projects/secure-notes-organizer` | [PNG](screens/project-secure-notes-organizer-1440.png) | [PNG](screens/project-secure-notes-organizer-768.png) | [PNG](screens/project-secure-notes-organizer-390.png) |
| `/about` | [PNG](screens/about-1440.png) | [PNG](screens/about-768.png) | [PNG](screens/about-390.png) |
| `/experience` | [PNG](screens/experience-1440.png) | [PNG](screens/experience-768.png) | [PNG](screens/experience-390.png) |
| `/resume` | [PNG](screens/resume-1440.png) | [PNG](screens/resume-768.png) | [PNG](screens/resume-390.png) |
| `/contact` | [PNG](screens/contact-1440.png) | [PNG](screens/contact-768.png) | [PNG](screens/contact-390.png) |
| `/404` | [PNG](screens/404-1440.png) | [PNG](screens/404-768.png) | [PNG](screens/404-390.png) |

## Interaction states

| State | Desktop | Tablet | Mobile |
| --- | --- | --- | --- |
| filter-products | [PNG](screens/filter-products-1440.png) | [PNG](screens/filter-products-768.png) | [PNG](screens/filter-products-390.png) |
| filter-public | [PNG](screens/filter-public-1440.png) | [PNG](screens/filter-public-768.png) | [PNG](screens/filter-public-390.png) |
| menu-open | Expanded desktop navigation | [PNG](screens/menu-open-768.png) | [PNG](screens/menu-open-390.png) |
| gallery-helixtra | [PNG](screens/gallery-helixtra-1440.png) | [PNG](screens/gallery-helixtra-768.png) | [PNG](screens/gallery-helixtra-390.png) |

The gallery state shows an enlarged genuine Helixtra marketing capture. Menu Close returns home in this design prototype; production implementation should close in place and restore trigger focus. Button hover, pressed, disabled and keyboard-focus treatments are on the foundation board.

## Assets and evidence

- [Generated asset manifest](asset-manifest.json): prompts, classification, permissions, alt text, hashes, masters and 39 WebP variants.
- [Public capture manifest](capture-manifest.json): six genuine public-site captures for local design review.
- [Screen content](screen-content.json): factual public-facing copy. Publication qualifications remain in [the evidence ledger](../PROJECT_CONTENT.md).
- [Native MCP discovery](figcraft-tool-discovery.json) and [authoring calls](figcraft-mcp-calls.json): actual headless server/schema and operation provenance.

Verification covers native geometry, text contrast on Ink, route coverage and valid prototype destinations. It does not claim browser, keyboard, HTTP, CV-download or performance tests. The original CV is linked locally in the prototype and will require a same-origin download in the implemented site.

## Authoring tools

`design/.tools/` contains a small Python stdio MCP client, native screen-authoring script and screen verifier. These are design tooling, not application code. `create_screens.py` recreates the generated design file and PNG exports; `verify_screens.py` checks the saved inspection JSON. Run the verifier after authoring. Preserve manual design edits before recreating the document.
