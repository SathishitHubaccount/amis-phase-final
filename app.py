"""
AMIS — Autonomous Manufacturing Intelligence System
Home Dashboard — Plant Morning Brief
Loads instantly from sample data (no LLM calls on this page).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from data.sample_data import (
    get_machine_fleet, get_current_inventory,
    get_historical_demand, get_production_lines,
    get_shift_configuration,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AMIS — Manufacturing Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Card with colored left border */
.amis-card {
    background: #1a1f2e;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 10px;
}
/* Metric big number */
.metric-big { font-size: 42px; font-weight: 700; line-height: 1.1; }
.metric-label { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.metric-sub { font-size: 13px; color: #aaa; margin-top: 4px; }
/* Machine card */
.mch-card {
    background: #1a1f2e;
    border-radius: 8px;
    padding: 14px 16px;
    border-left: 4px solid #444;
    height: 130px;
}
/* Alert row */
.alert-row {
    background: #1a1f2e;
    border-radius: 6px;
    padding: 10px 16px;
    margin-bottom: 6px;
    border-left: 4px solid;
    font-size: 13px;
}
/* Section header */
.section-hdr {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #666;
    margin: 24px 0 12px 0;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def health_color(score: int) -> str:
    if score >= 80:  return "#28a745"
    if score >= 60:  return "#ffc107"
    if score >= 40:  return "#fd7e14"
    return "#dc3545"

def health_label(score: int, status: str = "") -> str:
    if status == "down": return "DOWN"
    if score >= 80:  return "NORMAL"
    if score >= 60:  return "CAUTION"
    if score >= 40:  return "WARNING"
    return "CRITICAL"

def alert_color(level: str) -> str:
    return {"critical": "#dc3545", "warning": "#fd7e14",
            "caution": "#ffc107", "normal": "#28a745", "down": "#721c24"}.get(level, "#888")


# ── Load data ──────────────────────────────────────────────────────────────────
machines     = get_machine_fleet()
inventory    = get_current_inventory()
demand_hist  = get_historical_demand(weeks=12)
prod_lines   = get_production_lines()
shift_cfg    = get_shift_configuration()

# Derived metrics
operational  = [m for m in machines if m["status"] == "operational"]
warnings     = [m for m in machines if m["alert_level"] in ("warning", "critical", "down")]
avg_health   = int(sum(m["health_score"] for m in machines) / len(machines))
active_lines = sum(1 for l in prod_lines if l["status"] == "operational")
cap_weekly   = shift_cfg["current_base_capacity"]["effective_units_per_week"]
days_supply  = inventory["days_of_supply"]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 AMIS")
    st.markdown("**Autonomous Manufacturing**  \n**Intelligence System**")
    st.divider()
    st.markdown("### Navigation")
    st.page_link("app.py",                       label="🏠  Plant Overview",         icon=None)
    st.page_link("pages/1_Pipeline.py",           label="📊  Intelligence Report",    icon=None)
    st.page_link("pages/2_Ask_AMIS.py",           label="🤖  Ask AMIS",               icon=None)
    st.page_link("pages/3_Machine_Floor.py",      label="⚙️  Machine Floor",          icon=None)
    st.page_link("pages/4_Validator.py",          label="🔬  Scenario Validator",     icon=None)
    st.divider()
    st.caption(f"Plant: **PLANT-01**  |  Product: **PROD-A**")
    st.caption(f"Industrial Valve Assembly - Type A")
    st.caption(f"Last refreshed: {datetime.now().strftime('%H:%M, %b %d')}")

# ── Header ─────────────────────────────────────────────────────────────────────
col_title, col_date = st.columns([4, 1])
with col_title:
    st.markdown("## 🏭 Plant Morning Brief")
    st.markdown("<span style='color:#666;font-size:13px;'>PLANT-01 · Industrial Valve Assembly · Real-time snapshot</span>", unsafe_allow_html=True)
with col_date:
    st.markdown(f"<div style='text-align:right;color:#666;font-size:12px;margin-top:8px;'>{datetime.now().strftime('%A, %B %d %Y')}</div>", unsafe_allow_html=True)

st.divider()

# ── KPI Row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

with k1:
    col = health_color(avg_health)
    st.markdown(f"""
    <div class="amis-card" style="border-left:4px solid {col};">
      <div class="metric-label">Plant Health Score</div>
      <div class="metric-big" style="color:{col};">{avg_health}<span style="font-size:20px;color:#666;">/100</span></div>
      <div class="metric-sub">{len(warnings)} machine(s) need attention</div>
    </div>""", unsafe_allow_html=True)

with k2:
    line_col = "#28a745" if active_lines >= 4 else "#ffc107"
    st.markdown(f"""
    <div class="amis-card" style="border-left:4px solid {line_col};">
      <div class="metric-label">Active Production Lines</div>
      <div class="metric-big" style="color:{line_col};">{active_lines}<span style="font-size:20px;color:#666;">/ 5</span></div>
      <div class="metric-sub">Line 4 down — est. return Feb 23</div>
    </div>""", unsafe_allow_html=True)

with k3:
    inv_col = "#28a745" if days_supply > 14 else "#ffc107" if days_supply > 7 else "#dc3545"
    st.markdown(f"""
    <div class="amis-card" style="border-left:4px solid {inv_col};">
      <div class="metric-label">Inventory Days of Supply</div>
      <div class="metric-big" style="color:{inv_col};">{days_supply}<span style="font-size:20px;color:#666;"> days</span></div>
      <div class="metric-sub">{inventory['current_stock']:,} units · safety stock {inventory['safety_stock']:,}</div>
    </div>""", unsafe_allow_html=True)

with k4:
    cap_col = "#ffc107" if cap_weekly < 1000 else "#28a745"
    st.markdown(f"""
    <div class="amis-card" style="border-left:4px solid {cap_col};">
      <div class="metric-label">Weekly Capacity</div>
      <div class="metric-big" style="color:{cap_col};">{cap_weekly:,}<span style="font-size:20px;color:#666;"> u/wk</span></div>
      <div class="metric-sub">Reduced from 1,050 — Line 4 + MCH-002 degraded</div>
    </div>""", unsafe_allow_html=True)

# ── Alerts ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">⚡ Active Alerts</div>', unsafe_allow_html=True)

alerts = [
    ("critical", "🔴", "MCH-004 (Line 4) DOWN", "Bearing seizure — corrective maintenance in progress. Est. return Feb 23."),
    ("warning",  "🟠", "MCH-002 (Line 2) WARNING", "Vibration 4.2 mm/s² (baseline 1.8). Temperature 81°C. Failure risk HIGH within 48 hrs."),
    ("caution",  "🟡", "MCH-003 (Line 3) CAUTION", "Hydraulic pressure declining: 180→174 bar over 7 days. Temperature trend up."),
    ("caution",  "🟡", "Inventory reorder point breached", "13 days supply remaining. Safety stock threshold: 300 units. Incoming: +800 units in 4–7 days."),
]

for lvl, icon, title, detail in alerts:
    col = alert_color(lvl)
    st.markdown(f"""
    <div class="alert-row" style="border-left-color:{col};">
      {icon} <strong style="color:{col};">{title}</strong>
      <span style="color:#aaa;margin-left:12px;">{detail}</span>
    </div>""", unsafe_allow_html=True)

# ── Machine Fleet ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">⚙️ Machine Fleet Status</div>', unsafe_allow_html=True)

cols = st.columns(6)
for i, m in enumerate(machines):
    with cols[i]:
        col  = health_color(m["health_score"])
        lbl  = health_label(m["health_score"], m["status"])
        name_short = m["machine_name"].split(" - ")[0]
        line_short = m["production_line"]
        score_disp = str(m["health_score"]) if m["status"] != "down" else "DOWN"

        st.markdown(f"""
        <div class="mch-card" style="border-left-color:{col};">
          <div style="font-size:10px;color:#666;">{m['machine_id']} · {line_short}</div>
          <div style="font-size:12px;font-weight:600;color:#ddd;margin:4px 0;">{name_short}</div>
          <div style="font-size:30px;font-weight:700;color:{col};line-height:1;">{score_disp}</div>
          <div style="font-size:10px;color:{col};margin-top:2px;">{lbl}</div>
          <div style="font-size:10px;color:#555;margin-top:4px;">OEE · MTBF {m['mtbf_days']}d</div>
        </div>""", unsafe_allow_html=True)

# ── Charts ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-hdr">📈 12-Week Demand History</div>', unsafe_allow_html=True)

chart_c1, chart_c2 = st.columns([3, 2])

with chart_c1:
    dates   = [d["date"] for d in demand_hist]
    demands = [d["demand_units"] for d in demand_hist]
    anomaly_x = [d["date"] for d in demand_hist if d["anomaly"]]
    anomaly_y = [d["demand_units"] for d in demand_hist if d["anomaly"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=demands, mode="lines+markers",
        line=dict(color="#2E74B5", width=2),
        marker=dict(size=5, color="#2E74B5"),
        name="Weekly Demand",
        hovertemplate="%{x}<br><b>%{y:,} units</b><extra></extra>",
    ))
    if anomaly_x:
        fig.add_trace(go.Scatter(
            x=anomaly_x, y=anomaly_y, mode="markers",
            marker=dict(size=12, color="#dc3545", symbol="star"),
            name="Anomaly", hovertemplate="<b>ANOMALY: %{y:,} units</b><extra></extra>",
        ))
    fig.add_hline(y=950, line_dash="dash", line_color="#28a745",
                  annotation_text="Baseline 950", annotation_position="bottom right")
    fig.update_layout(
        template="plotly_dark", height=280, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=1.1), showlegend=True,
        xaxis_title=None, yaxis_title="Units",
        plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
    )
    st.plotly_chart(fig, use_container_width=True)

with chart_c2:
    # Production line capacity bar chart
    line_names   = [l["line_id"] for l in prod_lines]
    eff_outputs  = [l["effective_output_per_day"] for l in prod_lines]
    max_outputs  = [l["max_output_per_day"] for l in prod_lines]
    bar_colors   = [health_color(l["current_efficiency_pct"]) if l["status"] == "operational" else "#dc3545" for l in prod_lines]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=line_names, y=max_outputs, name="Max Capacity",
        marker_color="#2a2f42", hovertemplate="%{x}<br>Max: %{y} u/day<extra></extra>",
    ))
    fig2.add_trace(go.Bar(
        x=line_names, y=eff_outputs, name="Effective Output",
        marker_color=bar_colors, hovertemplate="%{x}<br>Effective: %{y} u/day<extra></extra>",
    ))
    fig2.update_layout(
        template="plotly_dark", height=280, barmode="overlay",
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=1.1),
        xaxis_title=None, yaxis_title="Units/day",
        plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
        title=dict(text="Production Line Capacity", font=dict(size=12), x=0),
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── CTA ────────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("#### Run Full Intelligence Analysis")
st.markdown("Get AI-generated cross-domain insights, risk identification, and priority actions across all 5 domains.")
col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1, 1, 3])
with col_btn1:
    if st.button("📊 Intelligence Report", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Pipeline.py")
with col_btn2:
    if st.button("🤖 Ask AMIS", use_container_width=True):
        st.switch_page("pages/2_Ask_AMIS.py")
with col_btn3:
    if st.button("⚙️ Machine Floor", use_container_width=True):
        st.switch_page("pages/3_Machine_Floor.py")
