# Testing Strategy & Commands

## Test & Quality Verification Commands

| Command | Purpose |
| :--- | :--- |
| `npm run build` | Verifies production JavaScript bundling and JSX compilation |
| `npm run preview` | Serves production build locally for verification |

## Manual UI Verification Standards

For every PR or code change, perform **manual browser testing**:

1. **Organization Search & Load:**
   - Search for a public organization (e.g. `AOSSIE-Org` or `facebook`).
   - Confirm repository list, contributor metrics, and charts load properly.
2. **Interactive Visualizations:**
   - Navigate to the **Network Graph** page (`NetworkPage.jsx`) and verify D3 force graph nodes render, drag cleanly, and zoom.
   - Navigate to **Analytics** and check time-series activity charts (Recharts).
3. **PAT & Rate Limit Modal:**
   - Open `PATModal` from the header/settings, input a test token (or leave blank), and verify save/clear behavior.
4. **Theme Toggle:**
   - Toggle dark/light mode via `ThemeToggle` and verify all cards, tables, and modal backgrounds adjust without broken contrast.
5. **DevTools Console Audit:**
   - Open browser DevTools (`F12`), navigate across all views (`HomePage`, `OverviewPage`, `RepositoriesPage`, `AnalyticsPage`, `ContributorsPage`, `NetworkPage`, `GovernancePage`, `SettingsPage`), and verify **zero unhandled console errors or React key warnings** are thrown.

- **Completion Criterion:** `npm run build` completes cleanly, and all dashboard views are manually verified in the browser.
