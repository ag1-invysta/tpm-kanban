# TPM Ops Dashboard

An interactive Flask web application for Senior Technical Project Managers, visualizing the full implementation delivery lifecycle — from SOW intake through structured decomposition, WSJF prioritization, and RAID management, to done — across five interconnected views.

Built as an interview preparation and reference tool for TPM roles in SaaS/data platform environments.

---

## Overview

The dashboard surfaces five interconnected views that drive delivery predictability:

| View | Purpose |
|---|---|
| **Kanban Board** | 7-column flow from Intake → Done, with WIP limits, WSJF-ordered Intake, exit criteria, and per-card RAID flags |
| **RAID Log** | Filterable, sortable register of all Risks, Assumptions, Issues, and Dependencies — synchronized across projects and Kanban cards, with type-aware trend tooltips |
| **Discovery** | Collapsible reference checklist across 4 categories, plus a per-project register with score bars, SLA indicators, and DoR-linked detail panels |
| **Workstreams** | Cross-functional ownership map with corrected RACI-lite matrix and cell-level definition tooltips |
| **SOW Translation** | 7-step pipeline from SOW Intake to Kanban, with per-deliverable decomposition, WSJF scoring, DoR gate tracking, fast-path routing, and task-level serialization |

---

## Project Structure

```
tpm_app/
├── app.py                      # Flask app — loaders, static data, routes
├── data/
│   ├── cards.csv               # Kanban card data — edit directly, no restart needed
│   ├── raid_log.csv            # Standalone RAID log entries
│   ├── discovery_log.csv       # Per-project discovery checklist progress
│   ├── sow_deliverables.csv    # SOW deliverable register with WSJF fields
│   └── sow_tasks.csv           # Decomposed task breakdown per deliverable
├── templates/
│   └── index.html              # Single-page frontend — all HTML, CSS, and JS inline
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

The board implements a 7-stage flow derived from real SaaS implementation practice.

| Column | WIP Limit | Key Metric |
|---|---|---|
| Intake | ∞ | Lead Time |
| Ready for Analysis | 3–5 | — |
| Discovery / Analysis | 2–3 | — |
| Ready for Execution | 5–8 | — |
| In Progress | ≈ # engineers | Cycle Time (median + 85th pct) |
| Review / Validation | 2–4 | WIP Age |
| Done | ∞ | Throughput |

**WSJF ordering in Intake:** Cards in Intake are automatically sorted top-to-bottom by WSJF score. Each card shows a rank badge (`#1 · 8.00`) and a proportional gradient bar. Cards with unresolved dependencies show a 🔒 lock indicator. The team always pulls the highest-value, most time-critical unblocked item first.

**Interactions:**
- Click a **column header** to expand its purpose, WIP rationale, exit criteria, and key metric
- Click a **card** to open its detail panel — includes a full WSJF breakdown (Business Value, Time Criticality ×2, Risk Reduction, ROM Days) with the formula rendered
- Cards with RAID entries show an amber `⚑ RAID` badge and a **View N RAID entries →** link

**Age indicators** on cards (all columns except Done):
- `2d` and under — neutral
- `3–5d` — amber warning
- `6d+` — red alert

---

## WSJF Scoring

All cards and SOW deliverables carry a WSJF (Weighted Shortest Job First) score:

```
WSJF Score = (Business Value + 2 × Time Criticality + Risk Reduction) ÷ ROM Days
```

Time Criticality is doubled relative to standard SAFe. In SaaS implementation work, committed-date pressure is the dominant prioritization factor — a deliverable on the critical path to a go-live date should always float above equally valuable but less urgent work.

| Component | Description | Range |
|---|---|---|
| `business_value` | How much this moves the customer's stated goal | 1–10 |
| `time_criticality` | How fast value decays if delayed; contractual dates score high | 1–10 |
| `risk_reduction` | Does completing this unblock other work or resolve RAID items? | 1–10 |
| `rom_days` | ROM estimate in days — normalizes for job size | integer |

Score color: green ≥ 6.0 · blue ≥ 3.0 · dim < 3.0

---

## Adding and Editing Cards

All card data lives in `data/cards.csv`. Edit directly — changes appear on browser reload, no restart needed.

### CSV Schema

| Field | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier |
| `title` | string | Card title — project name extracted from suffix after ` — ` or ` - ` |
| `column` | string | Must match a valid column ID |
| `type` | string | `feature`, `infra`, `integration`, `compliance`, `process` |
| `age_days` | integer | Days the card has been in its current column |
| `risk` | string | `low`, `medium`, or `high` |
| `owner` | string | Accountable team or individual |
| `description` | string | Full description shown in the detail panel |
| `dependencies` | string | Upstream blockers. Use `None` if none. |
| `assumptions` | string | Key assumption. Use `None` if none. |
| `raid_flags` | string | Semicolon-delimited inline RAID signals |
| `business_value` | integer | WSJF component — 1 to 10 |
| `time_criticality` | integer | WSJF component — 1 to 10 |
| `risk_reduction` | integer | WSJF component — 1 to 10 |
| `rom_days` | integer | ROM estimate in days |

### Valid Column IDs

```
intake  |  ready_analysis  |  discovery  |  ready_execution  |  in_progress  |  review  |  done
```

### RAID Flag Format

```
R:Risk description;A:Assumption description;I:Issue description;D:Dependency description
```

---

## RAID Log

### Two-source data model

**Inline card flags** (`raid_flags` in `cards.csv`) are lightweight operational signals visible on the board. One line — type and description only.

**Standalone log entries** (`data/raid_log.csv`) are fully managed items carrying probability, impact, score, response strategy, analysis method, owner, target date, and trend. These are the primary artifact for stakeholder reporting.

Intended flow: `Card flag (signal) → RAID log entry (managed item)`. A flag should become a standalone entry once it needs active management — an owner, response strategy, and target date.

### Trend column

Each entry shows `↑ Worsening`, `→ Stable`, or `↓ Improving` with type-aware hover tooltips. Directionality is consistent: ↑ always means harder, ↓ always means better, across all four RAID types.

### raid_log.csv Schema

| Field | Values / Format | Description |
|---|---|---|
| `id` | `R-01`, `A-02`, etc. | Unique ID, prefixed by type |
| `project` | String | Must match project name derived from card titles |
| `type` | `R`, `A`, `I`, `D` | Risk, Assumption, Issue, Dependency |
| `category` | `Data`, `Security`, `Scope`, `Schedule`, `Integration`, `Compliance`, `Operations`, `Resources`, `External` | Area of concern |
| `response_strategy` | `Mitigate`, `Avoid`, `Accept`, `Defer`, `Resolve`, `Validate` | Management approach |
| `status` | `Open`, `Accepted`, `Resolved`, `Validated`, `Closed` | Current state |
| `description` | String | Clear statement of the item |
| `probability` | `High`, `Medium`, `Low`, `—` | Use `—` for Issues (already occurring) |
| `impact` | `High`, `Medium`, `Low` | Business or delivery impact |
| `risk_score` | `High`, `Medium`, `Low` | Composite score |
| `analysis_method` | String | e.g. `P×I Matrix`, `FMEA`, `Spike / Feasibility Test` |
| `rationale` | String | Decision or reasoning summary |
| `owner` | String | Accountable person or team |
| `target_date` | `YYYY-MM-DD` or `—` | Resolution target |
| `trend` | `↑`, `→`, `↓` | Direction of risk |
| `notes` | String | Current status, actions, escalation context |

### Project Name Matching

Project names are derived from card titles by splitting on ` — ` or ` - ` and taking the last segment:

- `SSO Integration — BankFirst` → `BankFirst`
- `Data Schema Mapping - LogiTrack` → `LogiTrack`
- `SOC 2 Evidence Collection` → `Internal`

The `project` field in `raid_log.csv` must match this derived value exactly (case-sensitive).

---

## Discovery View

### Reference checklist (collapsible)

A global reference panel showing all 20 checklist items across four categories. **Stakeholders & Scope appears first** — scoping and RACI clarity is a prerequisite for validating data, integration, and environment assumptions.

| Category | Focus |
|---|---|
| **Stakeholders & Scope** | SOW mapping, RACI, change control, acceptance criteria |
| **Data Readiness** | Schema, access, quality, PII classification |
| **Integration** | API availability, auth, rate limits, firewall |
| **Environment** | Dev/staging/prod, deployment pipeline, rollback |

Items are independently checkable with a live running count. Click the panel header to collapse once internalized. These checkboxes are a global reference — per-project completion is tracked in the register below.

### Per-project register

One row per eligible Kanban card. Columns include score bars for each category (1–5 scale, color-coded), an overall completion badge, days open with SLA thresholds, and blocker context.

**SLA rules:** 3+ days open (non-complete) → amber, escalate to TPM. 7+ days → red, exec visibility required.

Clicking a row expands a detail panel with the full checklist, a progress ring, RAID assumptions from the log, and SLA warnings.

---

## Workstreams View

```
Data (Data Science) → Platform/Dev (Engineering) → Launch (Launch Team) → Customer Success (CS)
```

The RACI-lite matrix covers 8 key activities. Notable corrected assignments:

- **Data Schema Discovery:** Data Science is R (executes), TPM is A (owns outcome)
- **API Integration Design:** Engineering is A+R; TPM is C — consulted, not responsible
- **Acceptance Criteria Sign-off:** CS is C (input before lock), not R
- **Go-Live Readiness Gate:** Launch is A (owns ship decision), TPM is C

All cells have hover tooltips showing the full RACI definition. Rows with zero or multiple A assignments are flagged with a red outline and ⚠ symbol.

---

## SOW Translation View

Models the process of converting a Statement of Work into a trustworthy Kanban delivery plan. A SOW describes *outcomes*; this view builds the *delivery model* from it.

### 7-step pipeline

Click any step tile to open a popover showing the activities at that step and its output artifact. Step 06 (DoR Gate) includes the full 5-gate checklist with sub-items defining exactly what "done" means for each gate.

| Step | Title | Output |
|---|---|---|
| 01 | SOW Intake | Deliverable inventory + initial RAID entries |
| 02 | Decomposition | Task list per deliverable; spike cards created |
| 03 | Owner Sizing | ROM estimates with confidence tiers |
| 04 | Sizing Review | Agreed ROM; critical path; RAID additions |
| 05 | Serialization | Dependency graph; sequenced task list |
| 06 | DoR Gate | DoR scorecard — all 5 gates must be green |
| 07 | → Kanban | Cards in Intake/Backlog, WSJF-ordered |

**Why decomposition before sizing:** The team decomposes without estimating in the same session. Simultaneous decomposition and estimation inflates ROM because people anchor on complexity while decomposing. Separation surfaces hidden disagreements and produces more reliable estimates.

**Why sizing is async and owner-driven:** Each owner sizes only their own tasks independently, without cross-team anchoring. Group review follows — disagreements surface after estimates are committed, not during.

### Definition of Ready — 5 gates

All five gates must be green before a deliverable's cards enter the Kanban board:

| Gate | What "done" means |
|---|---|
| **AC Written** | Outcome clearly stated; happy path and edge cases covered; success metric measurable and agreed with the customer |
| **Dependencies Mapped** | All predecessor tasks sequenced; cross-workstream handoffs explicit; external dependencies in RAID |
| **Owner Confirmed** | Named individual confirmed (not a team); has capacity in the delivery window; has reviewed AC |
| **Sized by Owner** | ROM provided by the person doing the work; confidence tier assigned; Low confidence → Assumption in RAID |
| **RAID Populated** | All risks from decomposition logged; assumptions requiring validation have entries; cross-workstream deps tracked as D entries |

### Kanban landing zone and fast-path routing

DoR-cleared cards land in **Intake/Backlog** by default, ranked by WSJF score. The team *pulls* from Intake into Ready for Analysis as capacity opens — cards are never pushed directly into the execution queue.

**Fast-path exception:** If all 5 DoR gates are cleared AND the target date is within 14 days, the deliverable is eligible to land directly in **Ready for Analysis**, bypassing Intake. Fast-path eligible deliverables show an `⚡ Fast-path → Ready for Analysis` badge in the register and detail panel.

```
Fast-path = dorComplete AND daysToTarget ≤ 14 AND status != 'Ready for Execution'
```

### Spike cards

When a task cannot be sized due to an unvalidated assumption or unknown technical path, do not assign a placeholder estimate. Create a **spike card** with a fixed timebox (1–3 days). The spike validates the assumption and produces a ROM. Spike-required deliverables show `⚡ spike` in the ROM column.

### sow_deliverables.csv Schema

| Field | Type | Description |
|---|---|---|
| `id` | string | `D-01`, `D-02`, etc. |
| `project` | string | Client or project name |
| `section` | string | SOW section reference (e.g., `3.1`) |
| `deliverable` | string | Deliverable name from SOW |
| `owner` | string | Accountable team |
| `workstream` | string | `Data`, `Platform/Dev`, `Launch`, `Customer Success`, `Stakeholders` |
| `rom_days` | integer | ROM estimate in days |
| `confidence` | string | `High`, `Medium`, `Low` |
| `status` | string | `In Decomposition`, `Spike In Progress`, `In Progress`, `Blocked`, `Ready for Execution` |
| `dor_ac` | boolean | AC written gate cleared (`true`/`false`) |
| `dor_deps` | boolean | Dependencies mapped gate cleared |
| `dor_owner` | boolean | Owner confirmed gate cleared |
| `dor_sized` | boolean | Sized by owner gate cleared |
| `dor_raid` | boolean | RAID populated gate cleared |
| `spike_needed` | boolean | Spike required before final sizing |
| `committed_date` | `YYYY-MM-DD` | Contract delivery date from the SOW |
| `target_date` | `YYYY-MM-DD` | Internal projected completion date |
| `notes` | string | Current status or blocking context |
| `business_value` | integer | WSJF component — 1 to 10 |
| `time_criticality` | integer | WSJF component — 1 to 10 |
| `risk_reduction` | integer | WSJF component — 1 to 10 |

### sow_tasks.csv Schema

| Field | Type | Description |
|---|---|---|
| `id` | string | `T-01`, `T-02`, etc. |
| `deliverable_id` | string | Parent deliverable ID |
| `title` | string | Task name |
| `owner` | string | Named individual or team |
| `workstream` | string | Workstream assignment |
| `rom_days` | integer | ROM in days |
| `confidence` | string | `High`, `Medium`, `Low` |
| `status` | string | `Not Started`, `In Progress`, `Complete`, `Blocked` |
| `predecessors` | space-delimited | Task IDs that must complete before this task can start |
| `successors` | space-delimited | Task IDs gated by this task |
| `raid_ref` | string | RAID log entry this task relates to |
| `notes` | string | Context, blockers, spike status |

---

## API Endpoints

| Endpoint | Returns |
|---|---|
| `GET /` | Renders the dashboard with all data embedded inline |
| `GET /api/kanban` | Column definitions + all cards |
| `GET /api/raid` | RAID category reference definitions |
| `GET /api/discovery` | Discovery checklist categories and items |
| `GET /api/workstreams` | Workstream definitions |
| `GET /api/raid_log` | Merged RAID register (card flags + standalone entries) |
| `GET /api/discovery_log` | Per-project discovery checklist progress |
| `GET /api/sow` | SOW deliverables and task breakdown |

---

## Data Architecture

All data is serialized to JSON and injected into the page as `INLINE_DATA` at render time via Jinja2. The JavaScript `loadAll()` function reads from this inline object — the page works whether served by Flask or opened as a static file.

Flask reads all CSV files on every request. No restart needed after editing any CSV — reload the browser and changes appear immediately.

WSJF scores are computed in two places: server-side in Python at load time, and client-side via `computeWsjf()` at render time. The client-side computation is the authoritative display value, ensuring accuracy regardless of serialization edge cases.

Pipeline step popovers use `position: fixed` with `getBoundingClientRect()` positioning — this avoids the overflow clipping that would occur if the popover were positioned absolutely inside the pipeline's scrollable container.

---

## Design Notes

- Dark theme with CSS grid background and per-column/workstream accent color system
- Typography: Space Mono (labels, codes, IDs) + DM Sans (body text)
- No external JS frameworks — vanilla JS only
- Single `index.html` — all CSS and JS inline for portability
- Flask development server only — not configured for production deployment

---

## Extending the App

**Add Kanban cards:** Append to `data/cards.csv`. Set all four WSJF fields (`business_value`, `time_criticality`, `risk_reduction`, `rom_days`) for scoring. Reload browser.

**Add RAID entries:** Append to `data/raid_log.csv`. `project` must match the name derived from card titles. Reload browser.

**Add SOW deliverables:** Append to `data/sow_deliverables.csv`; add corresponding tasks to `data/sow_tasks.csv`. Reload browser.

**Update discovery checklist:** Edit `DISCOVERY_CHECKLIST` in `app.py`.

**Change RACI matrix:** Edit `RACI_MATRIX` in the JavaScript section of `templates/index.html`.

**Add Kanban column:** Add entry to `KANBAN_COLUMNS` in `app.py`, then use its `id` in `cards.csv`.

**Add workstreams:** Update `WORKSTREAM_RACI` in `app.py` and `WS_COLORS` in `index.html`.
