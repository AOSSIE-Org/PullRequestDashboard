# Code-to-Structure Mapping

## Directory Map

| Directory | Purpose | Primary Tech |
| :--- | :--- | :--- |
| `src/components/` | Reusable UI widgets, banners, modals, and navigation | React / Tailwind |
| `src/components/layout/` | Structural layout containers (Footer, Layout wrappers) | React |
| `src/pages/` | Primary application views and dashboard pages | React / Recharts / D3 |
| `src/services/` | GitHub API fetching, IndexedDB cache, analytics computations | Vanilla JS |
| `src/context/` | Global application state and dark/light theme context | React Context |
| `src/hooks/` | Custom hooks for data filtering, sorting, and state management | React Hooks |
| `src/styles/` | Global CSS definitions and custom utility classes | CSS / Tailwind |
| `public/` | SVG logos, static icons, sitemap, and web manifest assets | Static Assets |

## Key Files

| File | Purpose |
| :--- | :--- |
| `src/main.jsx` | React application entry point and root mounting |
| `src/App.jsx` | Main router configuration and layout wrapping |
| `src/services/github.js` | GitHub API service layer with IndexedDB persistent caching |
| `src/services/analytics.js` | Computed metrics for bus factor, activity, and org health |
| `src/context/AppContext.jsx` | App state, selected orgs, PAT token state, and cache triggers |
| `src/context/ThemeContext.jsx` | Dark/light theme state provider and toggle management |
| `src/hooks/useSortedData.js` | Custom hook for sorting and filtering repository/contributor tables |
| `src/components/Navbar.jsx` | Main header navigation bar |
| `src/components/PATModal.jsx` | Personal Access Token (PAT) configuration modal |
| `src/components/AnalysisBanner.jsx` | Banner showing current organizational analysis status |
| `src/components/RateLimitBanner.jsx` | Rate limit warning and quota awareness banner |
| `src/components/EmptyStateCard.jsx` | Fallback component for missing or loading datasets |
| `src/components/LearnModeModal.jsx` | Explanatory modal for metric terminology and usage guide |
| `src/components/ThemeToggle.jsx` | Dark/light mode theme switcher button |
| `src/pages/HomePage.jsx` | Landing search and org selection page |
| `src/pages/OverviewPage.jsx` | High-level organization dashboard |
| `src/pages/RepositoriesPage.jsx` | Filterable, sortable repository explorer table |
| `src/pages/AnalyticsPage.jsx` | Deep analytical metrics and time-series charts |
| `src/pages/ContributorsPage.jsx` | Contributor ranking, activity, and density dashboard |
| `src/pages/NetworkPage.jsx` | D3.js force-directed contributor network graph |
| `src/pages/GovernancePage.jsx` | License checks, stale repo detection, and risk metrics |
| `src/pages/SettingsPage.jsx` | PAT token, cache management, and application settings |
| `vite.config.js` | Vite bundler configuration with React & Tailwind plugins |
| `package.json` | Project dependencies, scripts, and package metadata |

## Rules

- Do NOT create unlisted top-level directories without maintainer approval.
- Keep components modular; place shared widgets in `src/components/` and page views in `src/pages/`.
- All API interactions MUST go through `src/services/github.js` to ensure IndexedDB caching and rate limit safety.
