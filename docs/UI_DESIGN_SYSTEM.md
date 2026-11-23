# UI Design System

Repository: https://github.com/glitter-node/data-toolkit

Use semantic HTML, external CSS and JavaScript, a responsive layout, keyboard-accessible controls, visible status messages, and four locale catalogs: en, ko, ja, zh-CN. The HTML source begins with `<html lang="en">`. Never use inline styles, scripts, or event handlers. The initial UI includes upload, preview table, output selection, download, locale, and theme.

## v0.1.1 UI refinement (2026-11-22)

The language and theme dropdowns use explicit foreground/background colors for light and dark themes. Native option popup rendering may still depend on the operating system and browser. The native file picker remains accessible through a visually hidden input and a localized label styled as a button; selected filenames and multi-file counts are displayed separately. Supported UI locales: en, ko, ja, zh-CN. No backend conversion, SQLite schema, or API changes were made in this refinement.

## UI usability

Keep file selection, clear action, preview empty state, and button enabled state synchronized. Maintain translations in English, Korean, Japanese, and Simplified Chinese. Preserve external JavaScript/CSS and `<html lang="en">` in source.

## v0.1.4 workspace layout

The UI uses a neutral card header with no colored header background, an operations navigation row, a 60/40 workspace and results grid, a collapsible transform section, and responsive stacking. Existing API and SQLite schema remain unchanged. Job history requires an existing job ID and access token; there is no unauthenticated global job listing.


## v0.1.5 layout update

- Keep the neutral card header and existing Convert, Validate, Batch, and Job history workflows.
- Place the Operation controls inside the Workspace card below the file selection area.
- Use content-driven Workspace height instead of stretching to match the Results card.
- Provide a transparent, fixed bottom-right Back to top control, shown after scrolling and respecting reduced-motion preferences.
- Keep HTML, CSS, and JavaScript separate and preserve existing API and SQLite behavior.
