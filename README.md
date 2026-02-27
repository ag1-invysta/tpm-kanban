# TPM Ops Dashboard

An interactive Flask web application for Senior Technical Project Managers, visualizing the full implementation delivery lifecycle — from SOW intake through to done — across a structured Kanban board, RAID log, discovery checklist, and workstream RACI.

Built as an interview preparation and reference tool for TPM roles in SaaS/data platform environments.

---

## Overview

The dashboard surfaces four interconnected concepts that drive delivery predictability:

| View | Purpose |
|---|---|
| **Kanban Board** | 7-column flow from Intake → Done, with WIP limits, exit criteria, and per-card RAID flags |
| **RAID Log** | Risks, Assumptions, Issues, Dependencies — mapped to the Kanban flow |
| **Discovery** | Interactive pre-execution checklist across 4 categories, with assumption tracking and SLA rules |
| **Workstreams** | Cross-functional ownership map (Data → Engineering → Launch → CS) with RACI-lite matrix |

---

## Project Structure

```
tpm_app/
├── app.py                  # Flask app — routes, column config, RAID/discovery/workstream data
├── data/
│   └── cards.csv           # Kanban card data — add/edit cards here, no code changes needed
├── templates/
│   └── index.html          # Single-page frontend — HTML, CSS, and JS in one file
└── README.md
```

---

## Quick Start

**Requirements:** Python 3.8+

```bash
# 1. Install dependency
pip install flask

# 2. Run the app
python app.py

# 3. Open in browser
http://localhost:5000
```

---

## Kanban Board

The board implements a 7-stage flow derived from real SaaS implementation practice. Each column has defined WIP limits, a purpose, exit criteria, and a key metric.

| Column | WIP Limit | Key Metric |
|---|---|---|
| Intake | ∞ | Lead Time |
| Ready for Analysis | 3–5 | — |
| Discovery / Analysis | 2–3 | — |
| Ready for Execution | 5–8 | — |
| In Progress | ≈ # engineers | Cycle Time (median + 85th pct) |
| Review / Validation | 2–4 | WIP Age |
| Done | ∞ | Throughput |

**Interactions:**
- Click a **column header** to expand its purpose, WIP rationale, exit criteria, and key metric inline
- Click a **card** to open its detail panel — appears below the column detail if open, or directly below the header if not
- Click the same card or column again to collapse

**Age indicators** on cards (In Progress and earlier only):
- `2d` and under — neutral
- `3–5d` — amber warning
- `6d+` — red alert
- Done column cards never show age as a warning color

---

## Adding and Editing Cards

All card data lives in `data/cards.csv`. Edit it directly — the app reads it fresh on every API call, so changes appear immediately on reload without restarting Flask.

### CSV Schema

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier |
| `title` | string | Card title displayed on board |
| `column` | string | Must match a column `id` (see valid values below) |
| `type` | string | Card category — `feature`, `infra`, `integration`, `compliance`, `process` |
| `age_days` | integer | Days in current column |
| `risk` | string | `low`, `medium`, or `high` |
| `owner` | string | Accountable team or individual |
| `description` | string | Full card description shown in detail panel |
| `dependencies` | string | Upstream blockers or required inputs. Use `None` if none. |
| `assumptions` | string | Key assumption underpinning the card. Use `None` if none. |
| `raid_flags` | string | Semicolon-delimited RAID entries (see format below) |

### Valid Column IDs

```
intake
ready_analysis
discovery
ready_execution
in_progress
review
done
```

### RAID Flag Format

Each flag is prefixed with its type letter followed by a colon:

```
R:Risk description
A:Assumption description
I:Issue description
D:Dependency description
```

Multiple flags on one card are separated by semicolons:

```
R:Legal review delayed — may impact go-live;A:PII field list complete (unverified)
```

Cards with any RAID flag display an amber `⚑ RAID` badge on the board. The full flag breakdown appears in the card detail panel.

---

## RAID Log View

Explains each of the four RAID categories with descriptions and BlastPoint-specific examples, plus a flow diagram showing where each type enters the Kanban pipeline:

- **Risks** → logged during Discovery / Analysis
- **Assumptions** → captured before Ready for Analysis
- **Issues** → surfaced immediately in In Progress
- **Dependencies** → sequenced before Ready for Execution
- All items → resolved before Done

---

## Discovery View

An interactive checklist across four pre-execution categories:

- **Data Readiness** — schema, access, quality, PII
- **Integration** — API availability, auth, rate limits, firewall
- **Environment** — dev/staging/prod, deployment pipeline, rollback
- **Stakeholders & Scope** — SOW mapping, acceptance criteria, RACI, change control

Check items off to track validation progress. The sidebar shows:
- A live progress ring (checked / total)
- An assumption log with `validated`, `unvalidated`, and `false` statuses — a `false` assumption triggers a scope review and RAID entry
- The open question SLA rule: 3+ days unresolved = escalate to TPM as a Risk; 7+ days = executive visibility required

---

## Workstreams View

Shows the four delivery workstreams in sequence with clear ownership:

```
Data (Data Science) → Platform/Dev (Engineering) → Launch (Launch Team) → Customer Success (CS)
```

The RACI-lite matrix covers 8 key activities and handoffs across all four teams. RACI codes:

| Code | Meaning |
|---|---|
| **A** | Accountable — single owner, cannot be shared |
| **R** | Responsible — doing the work |
| **C** | Consulted — input required before proceeding |
| **I** | Informed — kept in the loop |

A boundary risk callout explains why tasks at workstream edges (e.g., Data → Engineering handoff) are the most common source of dropped work — and why explicit ownership at those interfaces is non-negotiable.

---

## API Endpoints

The frontend is fully API-driven. All endpoints return JSON.

| Endpoint | Returns |
|---|---|
| `GET /` | Renders the dashboard HTML |
| `GET /api/kanban` | Column definitions + all cards from CSV |
| `GET /api/raid` | RAID category definitions |
| `GET /api/discovery` | Discovery checklist categories and items |
| `GET /api/workstreams` | Workstream definitions |

---

## Design Notes

- Dark theme with a CSS grid background and accent color system — each Kanban column has its own accent color carried through headers, card borders, and detail panels
- Typography: Space Mono (monospace labels/codes) + DM Sans (body)
- No external JS frameworks — vanilla JS with fetch API
- Single `index.html` — all CSS and JS inline for portability
- Flask development server only — not configured for production deployment

---

## Extending the App

**To add a new Kanban column:** Add an entry to the `KANBAN_COLUMNS` list in `app.py` following the existing schema, then use its `id` value in `cards.csv`.

**To update discovery checklist items:** Edit the `DISCOVERY_CHECKLIST` list in `app.py`.

**To change RACI matrix rows:** Edit the `RACI_MATRIX` array in the JavaScript section of `templates/index.html`.

**To add workstreams:** Update `WORKSTREAM_RACI` in `app.py` and `WS_COLORS` in `index.html` (one hex color per workstream).
