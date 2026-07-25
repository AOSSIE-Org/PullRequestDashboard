# Edge Cases & Agent Lessons Learned

## 🔴 Critical — Will Break Things

- **GitHub API Rate Limits (403/429):** Unauthenticated GitHub API requests are limited to 60 requests/hour per IP. Unhandled 403 or 429 API errors will break page rendering. Always route requests through `github.js` and show the `RateLimitBanner` or prompt the user via `PATModal` when quota is exhausted.
- **D3 Simulation Memory Leaks:** Creating D3 force simulations (`d3.forceSimulation()`) inside React components without calling `simulation.stop()` on unmount causes background CPU leaks and detached DOM references. Always stop simulations in the `useEffect` cleanup function.
- **IndexedDB Schema Corruptions:** If the schema or store structure in IndexedDB changes without version handling, calls to read/write cache will fail. Wrap IndexedDB operations in try/catch blocks and fall back gracefully to direct API fetching if IndexedDB errors out.

## 🟡 Caution — Common Agent Mistakes

- **Large Payload Pagination:** Organizations with hundreds of repositories or contributors can exceed response size limits. Ensure GraphQL queries and REST calls implement pagination cursors (`page`, `per_page`, `after`).
- **PAT Token Storage:** Personal Access Tokens must be stored strictly in `localStorage` or `sessionStorage` on the client. Never log, commit, or transmit user PAT tokens to third-party endpoints.
- **Theme Hydration Flicker:** When toggling themes between light and dark modes, ensure the `dark` class on the `<html>` element is updated synchronously in `ThemeContext.jsx` to prevent visual flashing.
- **Empty State Fallbacks:** When querying organizations with 0 public repositories or missing activity data, ensure components render `EmptyStateCard` instead of crashing on undefined array access (`repos.map()`).

## 🟢 Info — Good to Know

- Test the application locally using `npm run dev` and test production builds using `npm run build` followed by `npm run preview`.
- IndexedDB cache can be cleared anytime from the Settings page (`SettingsPage.jsx`).
