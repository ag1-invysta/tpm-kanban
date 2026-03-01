from flask import Flask, render_template, jsonify
import json
import csv
import os

app = Flask(__name__)

# ── CSV Loaders ───────────────────────────────────────────────────────────────

def load_cards():
    cards = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'cards.csv')
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cards.append({
                'id':           int(row['id']),
                'title':        row['title'],
                'column':       row['column'],
                'type':         row['type'],
                'age_days':     int(row['age_days']),
                'risk':         row['risk'],
                'owner':        row['owner'],
                'description':  row['description'],
                'dependencies': row['dependencies'],
                'assumptions':  row['assumptions'],
                'raid_flags':   row['raid_flags'],
            })
    return cards


def load_raid_log():
    """Load standalone RAID log entries from CSV."""
    entries = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'raid_log.csv')
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = dict(row)
            entry['source'] = 'log'
            entries.append(entry)
    return entries


def load_discovery_log():
    """Load per-project discovery checklist progress from CSV."""
    entries = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'discovery_log.csv')
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = dict(row)
            # Cast numeric scores to int
            for field in ('card_id', 'days_open', 'stakeholders_scope',
                          'data_readiness', 'integration', 'environment'):
                try:
                    entry[field] = int(entry[field])
                except (ValueError, KeyError):
                    pass
            entries.append(entry)
    return entries


def build_raid_log():
    """Merge card-derived RAID flags with standalone log entries."""
    card_raids = []
    for card in load_cards():
        if not card['raid_flags']:
            continue
        flags = [f.strip() for f in card['raid_flags'].split(';') if f.strip()]
        for flag in flags:
            if ':' not in flag:
                continue
            t    = flag[0]
            desc = flag[2:].strip()
            title   = card['title']
            project = 'Internal'
            for sep in [' — ', ' - ']:
                if sep in title:
                    project = title.split(sep)[-1].strip()
                    break
            card_raids.append({
                'id':                f"C-{card['id']}{t}",
                'project':           project,
                'type':              t,
                'category':          card['type'].capitalize(),
                'response_strategy': 'Mitigate',
                'status':            'Open',
                'description':       desc,
                'probability':       card['risk'].capitalize(),
                'impact':            'Medium',
                'risk_score':        card['risk'].capitalize(),
                'analysis_method':   '—',
                'rationale':         f"Flagged on card: {title}",
                'owner':             card['owner'],
                'target_date':       '—',
                'trend':             '→',
                'notes':             f"Source: Kanban card #{card['id']}",
                'source':            'card',
            })
    return card_raids + load_raid_log()


# ── Static Data ───────────────────────────────────────────────────────────────

KANBAN_COLUMNS = [
    {
        "id": "intake", "label": "Intake", "wip_limit": "∞", "wip_ratio": "No ratio",
        "purpose": "Raw requests, SOW items, uncommitted work",
        "metric": "Lead Time — Measures customer-facing responsiveness. Track rolling average; use for forecasting (not velocity).",
        "exit_criteria": ["Problem statement captured", "Business value identified", "Categorized (infra, feature, integration, …)"],
        "wip_rationale": "Inventory only; not committed work",
        "color": "#1a1a2e", "accent": "#e94560"
    },
    {
        "id": "ready_analysis", "label": "Ready for Analysis", "wip_limit": "3–5", "wip_ratio": "~0.5× execution capacity",
        "purpose": "Prioritized queue for structured discovery", "metric": "",
        "exit_criteria": ["Outcome defined", "Priority agreed", "Discovery owner assigned"],
        "wip_rationale": "Prevents overloading discovery; maintains upstream discipline",
        "color": "#16213e", "accent": "#f5a623"
    },
    {
        "id": "discovery", "label": "Discovery / Analysis", "wip_limit": "2–3", "wip_ratio": "~30–50% of execution capacity",
        "purpose": "Validate assumptions, surface unknowns, map dependencies", "metric": "",
        "exit_criteria": ["Assumptions validated", "Dependencies identified", "Feasibility reviewed", "Risks logged in RAID", "Work sized and decomposed"],
        "wip_rationale": "Keeps discovery focused; avoids analysis paralysis",
        "color": "#0f3460", "accent": "#00d4ff"
    },
    {
        "id": "ready_execution", "label": "Ready for Execution", "wip_limit": "5–8", "wip_ratio": "1.0–1.3× # engineers",
        "purpose": "Fully defined, dependency-cleared, execution-ready work", "metric": "",
        "exit_criteria": ["Clear outcome", "Assumptions validated", "Dependencies sequenced", "Acceptance criteria explicit", "Fits normal cycle time", "Owner accountable"],
        "wip_rationale": "Small buffer prevents starvation without creating excess inventory",
        "color": "#1a1a2e", "accent": "#7c3aed"
    },
    {
        "id": "in_progress", "label": "In Progress", "wip_limit": "≈ # engineers", "wip_ratio": "0.8–1.2× # engineers",
        "purpose": "Active implementation",
        "metric": "WIP Age + Cycle Time from 'In Progress' to 'Done' — measures delivery speed & predictability; track median & 85th percentile.",
        "exit_criteria": ["Actively progressing", "Blockers flagged immediately", "Scope stable", "No unresolved external dependency"],
        "wip_rationale": "Protects focus; minimizes multitasking; stabilizes cycle time",
        "color": "#16213e", "accent": "#10b981"
    },
    {
        "id": "review", "label": "Review / Validation", "wip_limit": "2–4", "wip_ratio": "~1–2 items per reviewer",
        "purpose": "QA, security, UAT, operational validation", "metric": "WIP Age",
        "exit_criteria": ["Code complete", "Peer review complete", "Tests executed", "Defects resolved", "Security validated", "Runbooks updated"],
        "wip_rationale": "Reflects system constraint; prevents QA bottleneck",
        "color": "#0f3460", "accent": "#f59e0b"
    },
    {
        "id": "done", "label": "Done", "wip_limit": "∞", "wip_ratio": "No ratio",
        "purpose": "Fully complete & operational",
        "metric": "Throughput — items that reached Done column",
        "exit_criteria": ["Meets Definition of Done", "Deployed", "Monitoring active", "Documentation complete", "Stakeholder acceptance confirmed"],
        "wip_rationale": "Exit state; no WIP control needed",
        "color": "#1a1a2e", "accent": "#06b6d4"
    }
]

RAID_CATEGORIES = {
    "R": {"label": "Risk",       "icon": "⚠",  "description": "Something that could go wrong. Score by probability × impact.",                               "example": "Customer data schema unknown — may require re-engineering pipeline", "color": "#e94560"},
    "A": {"label": "Assumption", "icon": "💡", "description": "Believed to be true but not yet validated. Must be confirmed during Discovery.",                "example": "SSO is already configured in customer environment",                  "color": "#f5a623"},
    "I": {"label": "Issue",      "icon": "🚨", "description": "A current, active blocker. Needs immediate owner and resolution date.",                        "example": "Data warehouse behind firewall — no API access available",           "color": "#ef4444"},
    "D": {"label": "Dependency", "icon": "🔗", "description": "Task B cannot start until Task A completes. Map on Kanban board.",                             "example": "Model training cannot begin until data validation completes",        "color": "#7c3aed"},
}

DISCOVERY_CHECKLIST = [
    {"category": "Data Readiness",      "icon": "🗄", "items": ["Data sources and formats confirmed", "Schema documentation available", "Data quality baseline assessed", "Access credentials / API keys provisioned", "PII / compliance constraints identified"]},
    {"category": "Integration",         "icon": "🔌", "items": ["API availability confirmed", "Authentication method documented", "Rate limits and SLAs understood", "Third-party dependencies identified", "Network / firewall constraints mapped"]},
    {"category": "Environment",         "icon": "☁",  "items": ["Dev / staging / prod environments defined", "Access provisioned for all teams", "Deployment pipeline understood", "Rollback strategy confirmed", "Monitoring / alerting baseline established"]},
    {"category": "Stakeholders & Scope","icon": "👥", "items": ["SOW deliverables mapped to tasks", "Acceptance criteria written for each deliverable", "RACI confirmed per workstream", "Change control process agreed", "Executive communication cadence set"]},
]

WORKSTREAM_RACI = {
    "workstreams": [
        {"name": "Data",             "owner": "Data Science", "description": "Ingestion, validation, schema mapping, pipeline build",          "handoff_to": "Platform/Dev"},
        {"name": "Platform / Dev",   "owner": "Engineering",  "description": "Feature configuration, API integrations, environment setup",     "handoff_to": "Launch"},
        {"name": "Launch",           "owner": "Launch Team",  "description": "UAT, acceptance testing, go-live readiness",                     "handoff_to": "Customer Success"},
        {"name": "Customer Success", "owner": "CS Team",      "description": "Onboarding, training, handoff documentation",                    "handoff_to": "—"},
    ]
}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    inline_data = json.dumps({
        "kanban":      {"columns": KANBAN_COLUMNS, "cards": load_cards()},
        "raid":        RAID_CATEGORIES,
        "discovery":   DISCOVERY_CHECKLIST,
        "workstreams": WORKSTREAM_RACI,
        "raid_log":    build_raid_log(),
        "discovery_log": load_discovery_log(),
    })
    return render_template("index.html", inline_data=inline_data)

@app.route("/api/kanban")
def get_kanban():
    return jsonify({"columns": KANBAN_COLUMNS, "cards": load_cards()})

@app.route("/api/raid")
def get_raid():
    return jsonify(RAID_CATEGORIES)

@app.route("/api/discovery")
def get_discovery():
    return jsonify(DISCOVERY_CHECKLIST)

@app.route("/api/workstreams")
def get_workstreams():
    return jsonify(WORKSTREAM_RACI)

@app.route("/api/raid_log")
def get_raid_log():
    return jsonify(build_raid_log())


@app.route("/api/discovery_log")
def get_discovery_log():
    return jsonify(load_discovery_log())


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
