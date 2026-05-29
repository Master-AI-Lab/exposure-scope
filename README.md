# exposure-scope 🛡️🔍

**HUNTER OSINT Engine** — Reverse search engine that maps your digital exposure.

Find where your personal data lives across the internet. Ethical OSINT for understanding your digital footprint.

## Architecture

```
Frontend (Vercel)          Backend (VPS)
┌─────────────────┐       ┌──────────────────────┐
│  Landing Page    │  ←→  │  HUNTER Orchestrator  │
│  Search Input    │  API │  SpiderFoot           │
│  Results Display │       │  Sherlock             │
│  Exposure Score  │       │  holehe               │
└─────────────────┘       │  theHarvester         │
                          │  TruffleHog            │
                          │  AI Synthesis Layer    │
                          └──────────────────────┘
```

## Tools

| Tool | What It Finds |
|------|---------------|
| **SpiderFoot** | Automated OSINT — IPs, domains, emails, social media |
| **Sherlock** | Username presence on 400+ platforms |
| **holehe** | Email accounts on online services |
| **theHarvester** | Email, subdomain, and port enumeration |
| **TruffleHog** | Exposed secrets in public code |

## Quick Start

### Backend (VPS)

```bash
pip install -r backend/requirements.txt
python3 backend/orchestrator.py --email user@example.com
```

### Frontend (Vercel)

Deploy the `frontend/` directory to Vercel.

## API

```
POST /api/scan
{
  "target": "user@example.com",
  "type": "email"
}

Response: {
  "exposure_summary": { "score": 12.5, "level": "MODERATE" },
  "categories": { ... },
  "raw_results": { ... }
}
```

## Security

- **No secrets in code** — Use environment variables or config file
- **Passive scanning only** — No direct interaction with target systems
- **Results stored locally** — Never shared or sold
