# Code Examples & Patterns

## ✅ Approved Patterns

### 1. IndexedDB-Cached API Service Pattern (`src/services/github.js`)

```javascript
import { getFromCache, saveToCache } from "./cache.js";

export async function fetchOrgRepositories(orgName, patToken = "") {
  const cacheKey = `repos_${orgName}`;
  const cachedData = await getFromCache(cacheKey);

  if (cachedData && !isCacheExpired(cachedData.timestamp)) {
    return cachedData.data;
  }

  const headers = { Accept: "application/vnd.github.v3+json" };
  if (patToken) {
    headers["Authorization"] = `token ${patToken}`;
  }

  const response = await fetch(`https://api.github.com/orgs/${orgName}/repos?per_page=100`, { headers });
  if (!response.ok) {
    if (response.status === 403 || response.status === 429) {
      throw new Error("RATE_LIMIT_EXCEEDED");
    }
    throw new Error(`GitHub API error: ${response.statusText}`);
  }

  const data = await response.json();
  await saveToCache(cacheKey, { data, timestamp: Date.now() });
  return data;
}
```

### 2. D3 Network Graph Lifecycle in React (`src/pages/NetworkPage.jsx`)

```jsx
import { useEffect, useRef } from "react";
import * as d3 from "d3";

export function ContributorNetwork({ nodes, links }) {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!svgRef.current || !nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear prior renders

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d) => d.id))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(400, 300));

    // Draw lines and nodes...

    simulation.on("tick", () => {
      // Update SVG positions
    });

    // Cleanup function MUST stop the simulation on unmount
    return () => {
      simulation.stop();
    };
  }, [nodes, links]);

  return <svg ref={svgRef} width="800" height="600" className="w-full h-auto"></svg>;
}
```

---

## ❌ Anti-Patterns — Do NOT Use

### ❌ Uncached Direct Fetch inside Component

```jsx
// BAD: Bypasses IndexedDB cache, causes API rate limit exhaustion
useEffect(() => {
  fetch(`https://api.github.com/orgs/${orgName}/repos`)
    .then((res) => res.json())
    .then(setRepos);
}, [orgName]);

// GOOD: Use the service layer
useEffect(() => {
  fetchOrgRepositories(orgName, patToken)
    .then(setRepos)
    .catch((err) => handleApiError(err));
}, [orgName, patToken]);
```

### ❌ Missing D3 Simulation Cleanup

```javascript
// BAD: Memory leak - simulation continues running after component unmounts
useEffect(() => {
  const simulation = d3.forceSimulation(nodes)...;
  // Missing return () => simulation.stop();
}, [nodes]);
```

### ❌ Swallowing API Error Exceptions

```javascript
// BAD: Hides rate limit error from user UI
try {
  const repos = await fetchOrgRepositories(orgName);
} catch (e) {
  console.log(e); // User sees blank loading screen forever
}

// GOOD: Trigger error state so RateLimitBanner or PATModal appears
try {
  const repos = await fetchOrgRepositories(orgName);
  setRepos(repos);
} catch (err) {
  if (err.message === "RATE_LIMIT_EXCEEDED") {
    setIsRateLimited(true);
  }
}
```
