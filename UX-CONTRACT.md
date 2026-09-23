# Printed demo UX contract

This contract covers the static GitHub Pages showcase. The original Flask routes in `modules/` remain the source evidence for the real workflow; demo actions never call those routes or claim persistence.

## Routes and titles

- `index.html` — `Printed — 3D printing orders`
- `prints.html` — `Prints — Printed demo`
- `submissions.html` — `Submissions — Printed demo`
- The Printed wordmark returns to `index.html`; dashboard navigation preserves the current-page state.

## Demo boundary

- Every interactive application page displays a visible `Demo mode` label.
- Order submission, saving, approving, denying, and archiving update only the current page state.
- Feedback says when a change is simulated and does not imply server persistence.

## Canonical UI Map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
| --- | --- | --- | --- | --- |
| Select/Listbox | Native `<select>` | This contract | Native platform popup | Keyboard and browser interaction check |
| Form | Semantic HTML + `static/demo.js` | This contract | Order intake | Validation browser check |
| Scrollbar | Global rules in `static/demo.css` | `DESIGN.md` | Stable table gutter | Computed style and narrow viewport check |
| Toast | `[data-toast]` live region | This contract | Success only | Browser interaction check |
| CRUD | Local simulation in `static/demo.js` | This contract | Approve, deny, archive, save | Full demo-flow browser check |

The native select decision accepts browser/operating-system popup geometry because this portfolio demo does not require authored popup dimensions. Native `<dialog>` enhanced by `static/demo.js` owns modal behavior; Escape/Cancel are supported and focus returns to the trigger.

## Order flow

`Create an order` opens the order dialog. The form switches between an existing-model link and custom-model details. Invalid fields receive inline text and accessible associations. A valid submission changes the dialog to a confirmation summary; `Start another` resets the form.

## Admin flow

- Prints: edit status controls, save simulated changes, inspect a record, or archive it locally.
- Submissions: inspect a request, approve it into the simulated print queue, or deny it locally.
- Risky demo actions use an app-owned confirmation dialog. No browser `alert`, `confirm`, or `prompt` is used.

## Responsive and accessibility behavior

- Header actions wrap below the wordmark before they can overlap.
- Admin tables own horizontal scrolling; the page retains normal vertical scrolling.
- Visible focus uses the primary blue token. Motion is reduced to near-instant opacity changes under `prefers-reduced-motion: reduce`.
- The accessibility target is WCAG 2.2 AA for the static showcase.
