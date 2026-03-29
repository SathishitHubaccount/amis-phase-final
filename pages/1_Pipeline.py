"""
AMIS — Manufacturing Intelligence Report
Runs the full 5-agent pipeline (bridge methods, no LLM) and displays
the structured health score, domain bars, cross-domain alerts, and priority actions.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import time

st.set_page_config(page_title="AMIS · Intelligence Report", page_icon="📊", layout="wide")

st.markdown("""
<style>
.domain-card { background:#1a1f2e; border-radius:8px; padding:16px 18px; margin-bottom:10px; }
.alert-card  { background:#1a1f2e; border-radius:8px; padding:12px 16px; margin-bottom:8px; border-left:4px solid; }
.action-card { background:#1a1f2e; border-radius:8px; padding:12px 16px; margin-bottom:8px; border-left:4px solid #2E74B5; }
.kv-row { display:flex; justify-content:space-between; margin:4px 0; font-size:13px; }
.kv-key { color:#888; }
.kv-val { color:#ddd; font-weight:500; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar nav ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 AMIS")
    st.divider()
    st.page_link("app.py",                       label="🏠  Plant Overview")
    st.page_link("pages/1_Pipeline.py",           label="📊  Intelligence Report")
    st.page_link("pages/2_Ask_AMIS.py",           label="🤖  Ask AMIS")
    st.page_link("pages/3_Machine_Floor.py",      label="⚙️  Machine Floor")
    st.page_link("pages/4_Validator.py",          label="🔬  Scenario Validator")

# ── Helpers ────────────────────────────────────────────────────────────────────
def health_color(score):
    if score >= 80: return "#28a745"
    if score >= 60: return "#ffc107"
    if score >= 40: return "#fd7e14"
    return "#dc3545"

def severity_color(sev):
    return {"CRITICAL": "#dc3545", "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107", "LOW": "#28a745"}.get(sev.upper(), "#888")

def priority_color(p):
    return {"P1": "#dc3545", "P2": "#fd7e14", "P3": "#ffc107"}.get(p, "#2E74B5")

DOMAIN_ICONS = {
    "demand":       "📈",
    "inventory":    "📦",
    "machine_health": "⚙️",
    "production":   "🏭",
    "supplier":     "🚚",
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Manufacturing Intelligence Report")
st.markdown("<span style='color:#666;font-size:13px;'>Full 5-agent pipeline · PLANT-01 · PROD-A · 4-week planning horizon</span>", unsafe_allow_html=True)
st.divider()

# ── Run pipeline ───────────────────────────────────────────────────────────────
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

col_run, col_info = st.columns([2, 5])
with col_run:
    run_btn = st.button("▶  Run Full Analysis", type="primary", use_container_width=True)
with col_info:
    st.markdown("<span style='color:#666;font-size:12px;'>Runs Demand → Inventory → Machine Health → Production → Supplier → Synthesize in sequence. No LLM calls — pure structured computation.</span>", unsafe_allow_html=True)

if run_btn:
    steps = [
        "Running Demand Forecasting Agent...",
        "Running Inventory Management Agent...",
        "Running Machine Health Agent...",
        "Running Production Planning Agent...",
        "Running Supplier & Procurement Agent...",
        "Synthesizing Manufacturing Intelligence Report...",
    ]
    progress = st.progress(0, text=steps[0])
    status_box = st.empty()

    import threading, queue

    result_q = queue.Queue()
    log_lines = []

    class StepCapture:
        """Capture print() calls from run_full_pipeline to update progress bar."""
        def write(self, txt):
            txt = txt.strip()
            if txt:
                log_lines.append(txt)
        def flush(self): pass

    def run_pipeline():
        from agents.orchestrator_agent import OrchestratorAgent
        agent = OrchestratorAgent()
        result = agent.run_full_pipeline(product_id="PROD-A", plant_id="PLANT-01", planning_weeks=4)
        result_q.put(result)

    t = threading.Thread(target=run_pipeline, daemon=True)
    t.start()

    step_idx = 0
    while t.is_alive():
        if len(log_lines) > step_idx and step_idx < len(steps):
            step_idx = min(len(log_lines), len(steps) - 1)
            progress.progress((step_idx) / len(steps), text=steps[min(step_idx, len(steps)-1)])
        time.sleep(0.3)

    progress.progress(1.0, text="✅ Pipeline complete!")
    t.join()
    st.session_state.pipeline_result = result_q.get()
    time.sleep(0.4)
    progress.empty()
    st.rerun()

# ── Results ────────────────────────────────────────────────────────────────────
result = st.session_state.pipeline_result

if result is None:
    st.info("Click **▶ Run Full Analysis** to execute the manufacturing intelligence pipeline.")
    with st.expander("What does this do?"):
        st.markdown("""
The pipeline runs all 5 specialist agents in sequence:

1. **Demand Forecasting** — multi-scenario forecast, anomaly detection, trend analysis
2. **Inventory Management** — stockout risk, replenishment plan, safety stock evaluation
3. **Machine Health** — fleet health assessment, failure risk, maintenance schedule
4. **Production Planning** — master production schedule, capacity gap analysis
5. **Supplier & Procurement** — supplier evaluation, purchase order generation, risk audit

Then synthesizes everything into a **unified Manufacturing Intelligence Report** with:
- Overall plant health score (0–100)
- Domain-level scores with status
- Cross-domain alerts (risks that span multiple departments)
- Prioritised action list with owners and impact
        """)
    st.stop()

report     = result["manufacturing_intelligence_report"]
health     = report["system_health"]
pipeline   = report["pipeline_summary"]
alerts     = report["cross_domain_alerts"]
actions    = report["priority_actions"]
domains    = health["domain_scores"]
raw        = result["pipeline_outputs"]

# ── Health score ───────────────────────────────────────────────────────────────
score = health["overall_score"]
status = health["overall_status"]
col_hero = health_color(score)

hero_col, gauge_col = st.columns([3, 2])

with hero_col:
    st.markdown(f"""
    <div style="background:#1a1f2e;border-radius:10px;padding:28px;border-left:6px solid {col_hero};">
      <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">Overall Plant Health Score</div>
      <div style="font-size:72px;font-weight:700;color:{col_hero};line-height:1.1;">{score}</div>
      <div style="font-size:14px;color:{col_hero};font-weight:600;">{status}</div>
      <div style="margin-top:16px;font-size:12px;color:#666;">
        {len([a for a in alerts if a.get('severity','').upper() == 'CRITICAL'])} critical ·
        {len([a for a in alerts if a.get('severity','').upper() == 'HIGH'])} high ·
        {len(actions)} priority actions
      </div>
    </div>
    """, unsafe_allow_html=True)

with gauge_col:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#444"},
            "bar": {"color": col_hero},
            "bgcolor": "#1a1f2e",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40],  "color": "#2a1215"},
                {"range": [40, 60], "color": "#2a1e0e"},
                {"range": [60, 80], "color": "#262215"},
                {"range": [80, 100],"color": "#0f2115"},
            ],
            "threshold": {"line": {"color": col_hero, "width": 3}, "thickness": 0.8, "value": score},
        },
        number={"font": {"size": 36, "color": col_hero}},
    ))
    fig_gauge.update_layout(
        height=200, margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="#1a1f2e", font={"color": "#ddd"},
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# ── Domain scores ──────────────────────────────────────────────────────────────
st.markdown("### Domain Scores")
dom_cols = st.columns(5)

for i, (domain, data) in enumerate(domains.items()):
    with dom_cols[i]:
        s = data["score"]
        c = health_color(s)
        icon = DOMAIN_ICONS.get(domain, "📋")
        label = domain.replace("_", " ").title()
        st.markdown(f"""
        <div class="domain-card" style="border-top:3px solid {c};text-align:center;">
          <div style="font-size:22px;">{icon}</div>
          <div style="font-size:11px;color:#888;margin:4px 0;">{label}</div>
          <div style="font-size:32px;font-weight:700;color:{c};">{s}</div>
          <div style="font-size:10px;color:{c};">{data['status']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(int(s) / 100)

# ── Pipeline KPIs ──────────────────────────────────────────────────────────────
st.markdown("### Pipeline Summary")
p1, p2, p3, p4, p5, p6 = st.columns(6)
kpis = [
    (p1, "Demand Target",       f"{pipeline['demand_target_weekly']:,} u/wk",    "#2E74B5"),
    (p2, "Capacity Ceiling",    f"{pipeline['capacity_ceiling_weekly']:,} u/wk",  "#ffc107"),
    (p3, "Planned Production",  f"{pipeline['planned_production_weekly']:,} u/wk","#28a745"),
    (p4, "Inventory Supply",    f"{pipeline['inventory_days_of_supply']} days",   "#17a2b8"),
    (p5, "Procurement Value",   f"${pipeline['total_procurement_value']:,.0f}",   "#6f42c1"),
    (p6, "Supply Resilience",   f"{pipeline['supply_resilience_score']}/100",     "#fd7e14"),
]
for col, label, value, color in kpis:
    with col:
        st.markdown(f"""
        <div style="background:#1a1f2e;border-radius:6px;padding:12px;text-align:center;">
          <div style="font-size:10px;color:#666;text-transform:uppercase;">{label}</div>
          <div style="font-size:20px;font-weight:700;color:{color};margin-top:4px;">{value}</div>
        </div>""", unsafe_allow_html=True)

# ── Cross-domain alerts ────────────────────────────────────────────────────────
if alerts:
    st.markdown(f"### ⚡ Cross-Domain Alerts  <span style='color:#666;font-size:14px;font-weight:normal;'>({len(alerts)} identified)</span>", unsafe_allow_html=True)
    for a in alerts:
        sev = a.get("severity", "MEDIUM")
        col = severity_color(sev)
        domains_str = " · ".join(a.get("domains", []))
        st.markdown(f"""
        <div class="alert-card" style="border-left-color:{col};">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:11px;font-weight:600;color:{col};">{sev}</span>
            <span style="font-size:10px;color:#555;">{domains_str}</span>
          </div>
          <div style="font-size:13px;color:#ddd;margin-top:4px;">{a.get('alert','')}</div>
        </div>""", unsafe_allow_html=True)

# ── Priority actions ───────────────────────────────────────────────────────────
if actions:
    st.markdown(f"### 🎯 Priority Actions  <span style='color:#666;font-size:14px;font-weight:normal;'>({len(actions)} actions)</span>", unsafe_allow_html=True)
    for act in actions:
        p = act.get("priority", "P3")
        pc = priority_color(p)
        urg = act.get("urgency", "")
        st.markdown(f"""
        <div class="action-card" style="border-left-color:{pc};">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:11px;font-weight:700;color:{pc};">{p}</span>
            <span style="font-size:10px;color:#555;">{urg} · Owner: {act.get('owner','')}</span>
          </div>
          <div style="font-size:13px;color:#ddd;">{act.get('action','')}</div>
          <div style="font-size:11px;color:#666;margin-top:4px;">Impact: {act.get('impact','')}</div>
        </div>""", unsafe_allow_html=True)

# ── Human escalation ───────────────────────────────────────────────────────────
if report.get("human_escalation_required"):
    st.error("### 🚨 Human Escalation Required\nCritical issues detected that require executive authorization before proceeding.")

# ── Raw data expander ──────────────────────────────────────────────────────────
with st.expander("🔍 View Raw Pipeline Outputs (JSON)"):
    tab_d, tab_i, tab_m, tab_p, tab_s = st.tabs(["Demand", "Inventory", "Machine Health", "Production", "Supplier"])
    import json
    tab_d.json(raw["demand"])
    tab_i.json(raw["inventory"])
    tab_m.json(raw["machine_health"])
    tab_p.json(raw["production"])
    tab_s.json(raw["supplier"])
