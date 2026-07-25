# Project Setup & Local Development

## Prerequisites

Verify local development tools before starting setup:

```bash
# Check Node.js version (must be >= 18.0.0)
node --version

# Check npm & git
npm --version
git --version
```

## Local Development Setup

### 1. Install Project Dependencies

Run from the root of the `OrgExplorer` repository:

```bash
npm install
```

### 2. Start Vite Development Server

Spin up the local development server:

```bash
npm run dev
```

Open the printed local URL (typically `http://localhost:5173`) in your web browser.

### 3. Verify Production Build

Test building the application locally before creating a pull request:

```bash
npm run build
npm run preview
```

## Issue Assignment Check Before Coding

Before writing code or opening PRs:
1. Confirm your assigned GitHub issue number.
2. If unassigned, post in the project Discord channel ([`.agent/info/operational-data.md`](../info/operational-data.md)) to discuss and get assigned before starting work.
