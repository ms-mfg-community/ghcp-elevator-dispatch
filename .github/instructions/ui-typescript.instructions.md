---
description: >-
  Conventions for the elevator dispatch dashboard
  TypeScript source. Use when writing, editing, or
  reviewing TypeScript files under workspace/ui/.
applyTo: "workspace/ui/**/*.ts"
---

# UI TypeScript Conventions

- Keep the frontend framework-free. Use vanilla DOM APIs
  (`document.createElement`, `querySelector`,
  `innerHTML`) — no React, Vue, Angular, or Lit.
- Do not add runtime npm dependencies. The only npm
  packages should be dev dependencies like `typescript`.
- Keep the `Snapshot`, `ElevatorState`, `FloorState`, and
  `Passenger` type aliases in sync with the Python
  `to_dict()` return shapes. When a field is added or
  renamed in the simulation dataclass, update the
  corresponding TypeScript type.
- Use `const` for DOM element references and
  `function` declarations for named render helpers. Avoid
  classes for UI logic.
- Render functions should accept state as parameters and
  return HTML strings or append to a container. Do not
  read global mutable state inside render functions.
- Prefer `textContent` over `innerHTML` when inserting
  user-visible text that does not require nested markup,
  to avoid XSS from dynamic values.
- After editing `.ts` source, always run `npm run build`
  from `workspace/` to regenerate the served
  `ui/static/main.js`. Never edit `main.js` directly.
- Keep CSS class names in `styles.css` and reference them
  by string in TypeScript. Do not generate class names
  dynamically.
