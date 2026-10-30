# Bharat Career Twin · AgentFeed demo

This folder contains the working browser demo for the Bharat Career Twin plan.

## Run locally

From the `website` folder:

```bash
python3 -m http.server 4173
```

Then open `http://127.0.0.1:4173`.

The demo intentionally keeps the front end dependency-free so the prototype can be reviewed without a build step. The experience mirrors the planned React component boundaries:

- perspective-grid landing hero
- expandable sidebar and responsive mobile navigation
- steer box, focus modes, MMR-style mixed feed and diversity guard
- explainable ranking sheet with a Docker counterfactual
- QR share sheet with WhatsApp, LinkedIn, post, copy and download actions
- animated team reveal grid and masked mutual avatars
- command search with live filtering and keyboard navigation
- multi-step resume twin loader with editable JSON and cover letter
- nearby tribe graph, referral pathfinder and bilingual referral copy
- government scheme eligibility, startup bazaar, recent pulse and simulation lab

The seeded job cards use the same normalized source shape expected from the freehire sync described in the project plan. The browser now prefers the local FastAPI feed and retains the arrays in `app.js` as an offline fallback.

## Local API connection

When the FastAPI service is running on `http://127.0.0.1:8000`, the feed
automatically requests `/api/feed` with the local `demo_fresher` identity and
renders the six-agent trace returned by the backend. Feed interactions,
resume parsing, referral-path drafts, and new startup ideas also use the API
where a matching endpoint exists. If the API is unavailable, the browser
keeps the seeded deterministic demo feed and local interactions usable.

Override the defaults before loading the page when needed:

```html
<script>
  window.BCT_API_BASE = 'http://127.0.0.1:8000/api';
  window.BCT_DEMO_USER = 'demo_govt';
</script>
```
