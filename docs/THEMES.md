# Theme palette and surface depth

The interface offers System, Light, Dark, and Warm. System follows the operating system color scheme and updates when the system preference changes. Explicit selections override the system setting. The selection persists in `localStorage` under `dataToolkit.theme`.

| Theme | Background | Surface | Accent |
| --- | --- | --- | --- |
| Light | `#f3f6fc` | `#ffffff` | `#4665c4` |
| Dark | `#141a28` | `#222d43` | `#7894ed` |
| Warm | `#f8f4ec` | `#fffdf9` | `#a96d48` |

CSS variables define surface, border, accent, shadow, focus, and input colors. The header, workspace, results, operation section, and transform panel use restrained layered shadows and borders. Existing layouts and API contracts are unchanged. JavaScript remains in external files; the CSP does not require `unsafe-inline` or `unsafe-eval`.

## Soft 3D surface system

`/static/css/soft3d.css` is loaded after the base stylesheet. The three palettes have independent elevation, inset, highlight, and button-shadow tokens. The header and primary panels use raised multi-layer surfaces; the operation panel and empty preview use recessed surfaces. Buttons and tabs provide hover, pressed, disabled, and keyboard-focus feedback. Reduced-motion preferences disable movement. The existing page layout, theme persistence, external scripts, and CSP remain unchanged.
