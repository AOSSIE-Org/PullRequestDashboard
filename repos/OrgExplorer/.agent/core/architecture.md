# Core Project Architecture

## Architecture Overview

**OrgExplorer** is a browser-based, client-side intelligence and visualization platform that transforms GitHub organizations into interactive dashboards. It runs **entirely in the browser** without requiring a backend server.

- **Frontend Framework:** React 18 with Vite 5 and TailwindCSS 4 (`@tailwindcss/vite`).
- **Data & API Pipeline:** `src/services/github.js` handles data fetching from GitHub REST & GraphQL APIs with IndexedDB persistence for client-side caching.
- **Analytics Engine:** `src/services/analytics.js` computes organization metrics, bus factor, contributor density, activity velocity, and risk indicators.
- **Visualizations:** D3.js 7 powers force-directed contributor network graphs, and Recharts 2 renders time-series activity charts.
- **Routing & State:** React Router DOM 6 manages page navigation (`HomePage`, `OverviewPage`, `RepositoriesPage`, `AnalyticsPage`, `ContributorsPage`, `NetworkPage`, `GovernancePage`, `SettingsPage`), while React Context (`AppContext`, `ThemeContext`) manages global application state and theme modes.

## Architecture Boundaries

1. **Zero-Backend Constraint:** All data fetching, caching, and analytics calculation must occur strictly client-side in the browser. Do NOT introduce server dependencies or node-based runtime requirements for client features.
2. **IndexedDB Caching Layer:** API requests must pass through the IndexedDB caching layer (`src/services/github.js`) to minimize rate limit consumption.
3. **Graph Lifecycle Safety:** D3 force simulations must be cleanly initialized inside React `useEffect` hooks and stopped/cleaned up on unmount (`simulation.stop()`) to prevent memory leaks.
4. **Theme Consistency:** UI components must support dark/light modes cleanly using Tailwind theme utility classes and CSS variables.

## Conceptual Data Flow

```
User Action / Page Load → AppContext / Page Component
                        → Check IndexedDB Cache (github.js)
                        ├── Cache Hit  ──► Render Analytics & Visualizations
                        └── Cache Miss ──► Fetch GitHub REST/GraphQL API
                                           ├── Save to IndexedDB Cache
                                           └── Compute Analytics (analytics.js)
                                           └── Render Dashboard (D3 / Recharts)
```

## Dependency Map

| Dependency | Purpose | Location |
| :--- | :--- | :--- |
| `react` / `react-dom` | UI Rendering Framework | `package.json` |
| `vite` | Dev Server & Production Bundler | `package.json` |
| `tailwindcss` | Utility-First Styling | `package.json` |
| `d3` | Force-Directed Network Graphs | `package.json` |
| `recharts` | Time-Series Metric Charts | `package.json` |
| `react-router-dom` | Client-Side Page Routing | `package.json` |
