---
version: alpha
colors:
  ink: "#06091e"
  surface: "#121521"
  surfaceRaised: "#1a1f2d"
  text: "#eef6ff"
  textMuted: "#9aa9bc"
  primary: "#9dc3f7"
  accent: "#f0a33a"
  success: "#62d5a1"
  danger: "#ff7b78"
typography:
  display:
    fontFamily: "Hubot Sans, Avenir Next, system-ui, sans-serif"
  body:
    fontFamily: "Inter, Avenir Next, system-ui, sans-serif"
rounded:
  control: "0.75rem"
  panel: "1.25rem"
spacing:
  compact: "0.5rem"
  default: "1rem"
  section: "clamp(4rem, 10vw, 8rem)"
components:
  button: {}
  dialog: {}
  table: {}
---

## Overview

Printed keeps the visual identity of the original project: a dark workshop-at-night interface, icy blue light, fine technical grid lines, and the green Benchy model as the product signature. The public page is expressive; the admin demo is denser and operational. It should never look like a generic corporate dashboard or a new brand pasted over the original student-built product.

Runtime CSS in `static/demo.css` is canonical. This document mirrors its durable tokens and intent.

## Colors

Navy surfaces create the nighttime workshop setting. Icy blue is the main interactive and focus color. Warm orange is reserved for demo labels and small highlights. Success and danger colors always appear with text or an icon, never alone.

## Typography

The display stack favors Hubot Sans when available to preserve the original wordmark character. Body and data use a neutral system stack for reliable rendering and compact tables.

## Layout

The landing page uses a centered hero with a technical grid and large negative space. The admin demo uses a constrained content frame, a compact top navigation, summary cards, and horizontally scrollable semantic tables at narrow widths.

## Elevation & Depth

Surfaces are separated primarily by border and tonal change. Shadows are soft and blue-tinted; they are used for floating dialogs and the hero model, not every card.

## Shapes

Controls use 12px corners and panels use 20px corners. The glowing, chamfered primary CTA is the one expressive control; routine dashboard controls remain restrained.

## Components

Buttons have a stable 44px minimum height, visible hover/focus/active states, and semantic intent. Dialogs stay within the visual viewport and scroll internally. Tables retain headers and horizontal scrolling so the original operational data remains inspectable on small screens.

## Do's and Don'ts

- Do preserve the original dark, luminous, 3D-printing atmosphere.
- Do make demo-only behavior explicit and safe to explore.
- Do keep navigation and actions usable at phone widths.
- Do not reintroduce fixed-position header buttons or browser alerts.
- Do not imply that demo mutations persist to a backend.
