"""
AMIS — Machine Floor
Visual machine health dashboard: fleet cards, sensor trends, OEE history.
No LLM calls — all from sample data, loads instantly.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from data.sample_data import get_machine_fleet, get_sensor_readings, get_oee_history, get_maintenance_history

st.set_page_config(page_title="AMIS · Machine Floor", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
.mch-big-card {
    background:#1a1f2e; border-radius:10px; padding:18px;
    border-left:5px solid; margin-bottom:12px; cursor:pointer;
}
.sensor-row { display:flex; justify-content:space-between; align-items:center;
              background:#12151f; border-radius:6px; padding:8px 12px; margin:4px 0; }
.sensor-name { font-size:12px; color:#888; }
.sensor-val  { font-size:14px; font-weight:600; }
.sensor-bar-bg { background:#2a2f42; border-radius:4px; height:6px; margin-top:3px; }
</style>
""", unsafe_allow_html=True)

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

def sensor_color(current, baseline, high_thresh, crit_thresh):
    if crit_thresh and current >= crit_thresh: return "#dc3545"
    if high_thresh and current >= high_thresh: return "#fd7e14"
    if abs(current - baseline) / max(baseline, 0.001) > 0.10: return "#ffc107"
    return "#28a745"

# ── Data ───────────────────────────────────────────────────────────────────────
machines = get_machine_fleet()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## ⚙️ Machine Floor")
st.markdown("<span style='color:#666;font-size:13px;'>Live sensor readings · OEE trends · Maintenance history · PLANT-01</span>", unsafe_allow_html=True)
st.divider()

# ── Fleet summary KPIs ─────────────────────────────────────────────────────────
total   = len(machines)
running = sum(1 for m in machines if m["status"] == "operational")
down    = sum(1 for m in machines if m["status"] == "down")
warning = sum(1 for m in machines if m["alert_level"] in ("warning", "critical"))
caution = sum(1 for m in machines if m["alert_level"] == "caution")
avg_hs  = int(sum(m["health_score"] for m in machines) / total)

k1, k2, k3, k4, k5 = st.columns(5)
for col, label, value, color in [
    (k1, "Total Machines",    str(total),           "#2E74B5"),
    (k2, "Operational",       str(running),          "#28a745"),
    (k3, "Down",              str(down),             "#dc3545"),
    (k4, "Warning/Critical",  str(warning),          "#fd7e14"),
    (k5, "Avg Health Score",  f"{avg_hs}/100",       health_color(avg_hs)),
]:
    with col:
        st.markdown(f"""
        <div style="background:#1a1f2e;border-radius:8px;padding:14px;text-align:center;border-top:3px solid {color};">
          <div style="font-size:10px;color:#666;text-transform:uppercase;">{label}</div>
          <div style="font-size:28px;font-weight:700;color:{color};margin-top:4px;">{value}</div>
        </div>""", unsafe_allow_html=True)

# ── Machine cards row ──────────────────────────────────────────────────────────
st.markdown("<div style='font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;margin:20px 0 12px;'>Machine Fleet</div>", unsafe_allow_html=True)

card_cols = st.columns(len(machines))
for i, m in enumerate(machines):
    with card_cols[i]:
        col   = health_color(m["health_score"])
        score = "DOWN" if m["status"] == "down" else str(m["health_score"])
        lbl   = m["alert_level"].upper()
        name  = m["machine_name"].split(" - ")[0]
        line  = m["production_line"]
        st.markdown(f"""
        <div class="mch-big-card" style="border-left-color:{col};">
          <div style="font-size:10px;color:#555;">{m['machine_id']}</div>
          <div style="font-size:11px;color:#ddd;font-weight:600;margin:3px 0;">{name}</div>
          <div style="font-size:10px;color:#555;">{line}</div>
          <div style="font-size:34px;font-weight:700;color:{col};line-height:1.1;margin:6px 0;">{score}</div>
          <div style="font-size:10px;color:{col};">{lbl}</div>
          <div style="font-size:9px;color:#444;margin-top:6px;">Age: {m['age_years']}yr · MTBF {m['mtbf_days']}d</div>
        </div>""", unsafe_allow_html=True)

# ── Machine detail tabs ────────────────────────────────────────────────────────
st.divider()
st.markdown("### Machine Detail")

machine_names = [f"{m['machine_id']} — {m['machine_name'].split(' - ')[0]}" for m in machines]
selected_name = st.selectbox("Select machine for detailed view", machine_names)
selected_id   = selected_name.split(" — ")[0].strip()
machine       = next(m for m in machines if m["machine_id"] == selected_id)
sensors       = get_sensor_readings(selected_id)
oee_hist      = get_oee_history(selected_id, periods=6)

tab_sensors, tab_oee, tab_trend, tab_maint = st.tabs(["📡 Sensors", "📊 OEE History", "📈 7-Day Trends", "🔧 Maintenance"])

# ── Tab 1: Sensors ──────────────────────────────────────────────────────────────
with tab_sensors:
    if machine["status"] == "down":
        st.error(f"**{machine['machine_id']} is DOWN** — {machine.get('downtime_reason', 'Under maintenance')}")
        if "failure_event" in sensors:
            fe = sensors["failure_event"]
            st.markdown(f"**Failure date:** {fe['date']}")
            st.markdown(f"**Root cause:** {fe['root_cause']}")
            st.markdown(f"**Sensor at failure:** {fe['sensor_at_failure']}")
        st.stop() if False else None  # Don't stop, just show nothing more

    sensor_data = sensors.get("sensors", {})
    if sensor_data:
        st.markdown(f"**Last reading:** {sensors.get('timestamp', 'N/A')}")
        sens_cols = st.columns(2)
        for j, (skey, sval) in enumerate(sensor_data.items()):
            with sens_cols[j % 2]:
                baseline  = sval["baseline"]
                current   = sval["current"]
                high      = sval.get("high_threshold")
                crit      = sval.get("critical_threshold")
                unit      = sval.get("unit", "")
                scol      = sensor_color(current, baseline, high, crit)
                deviation = round(((current - baseline) / max(baseline, 0.001)) * 100, 1)
                dev_sign  = "+" if deviation >= 0 else ""

                # Progress bar ratio (capped at 1.0)
                ratio = current / (crit or high or (baseline * 2)) if (crit or high) else 0.5
                ratio = min(ratio, 1.0)

                st.markdown(f"""
                <div class="sensor-row">
                  <div>
                    <div class="sensor-name">{skey.replace('_', ' ').title()}</div>
                    <div class="sensor-val" style="color:{scol};">{current} <span style="font-size:10px;color:#555;">{unit}</span></div>
                    <div style="font-size:10px;color:#555;">Baseline: {baseline} {unit}</div>
                  </div>
                  <div style="text-align:right;">
                    <div style="font-size:13px;color:{scol};font-weight:600;">{dev_sign}{deviation}%</div>
                    {'<div style="font-size:10px;color:#dc3545;">CRITICAL</div>' if crit and current >= crit else
                     '<div style="font-size:10px;color:#fd7e14;">HIGH</div>' if high and current >= high else
                     '<div style="font-size:10px;color:#28a745;">NORMAL</div>'}
                  </div>
                </div>""", unsafe_allow_html=True)
    else:
        st.warning("No live sensor data — machine may be offline.")

# ── Tab 2: OEE History ─────────────────────────────────────────────────────────
with tab_oee:
    if oee_hist:
        periods    = [d["period"] for d in oee_hist]
        oee_vals   = [round(d["oee"] * 100, 1) for d in oee_hist]
        avail_vals = [round(d["availability"] * 100, 1) for d in oee_hist]
        perf_vals  = [round(d["performance"] * 100, 1) for d in oee_hist]
        qual_vals  = [round(d["quality"] * 100, 1) for d in oee_hist]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=periods, y=oee_vals, name="OEE %", marker_color="#2E74B5"))
        fig.add_trace(go.Scatter(x=periods, y=avail_vals, name="Availability", mode="lines+markers", line=dict(color="#28a745", width=2)))
        fig.add_trace(go.Scatter(x=periods, y=perf_vals, name="Performance", mode="lines+markers", line=dict(color="#ffc107", width=2)))
        fig.add_trace(go.Scatter(x=periods, y=qual_vals, name="Quality", mode="lines+markers", line=dict(color="#17a2b8", width=2)))
        fig.add_hline(y=85, line_dash="dash", line_color="#666", annotation_text="World-class OEE 85%")

        fig.update_layout(
            template="plotly_dark", height=320, margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(title="% Score", range=[0, 105]),
            legend=dict(orientation="h", y=1.1),
            plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
        )
        st.plotly_chart(fig, use_container_width=True)

        # OEE trend note
        if len(oee_vals) >= 2:
            trend = oee_vals[-1] - oee_vals[0]
            trend_txt = f"↓ Declining {abs(trend):.1f}% over 6 months" if trend < -2 else f"↑ Improving {trend:.1f}%" if trend > 2 else "→ Stable"
            trend_col = "#dc3545" if trend < -2 else "#28a745" if trend > 2 else "#ffc107"
            st.markdown(f"**OEE Trend:** <span style='color:{trend_col};font-weight:600;'>{trend_txt}</span>", unsafe_allow_html=True)

# ── Tab 3: 7-Day Trends ────────────────────────────────────────────────────────
with tab_trend:
    trend_data = sensors.get("trend_7_day", {})
    if trend_data:
        days = [f"Day {i+1}" for i in range(7)]
        for metric_name, values in trend_data.items():
            clean_vals = [v for v in values if v is not None]
            x_vals     = [days[i] for i, v in enumerate(values) if v is not None]

            if not clean_vals:
                continue

            # Trend direction
            delta  = clean_vals[-1] - clean_vals[0]
            pct    = round((delta / max(clean_vals[0], 0.001)) * 100, 1)
            sign   = "+" if delta >= 0 else ""
            t_col  = "#fd7e14" if delta > 0 else "#28a745"

            label = metric_name.replace("_", " ").title()
            col_chart, col_stat = st.columns([4, 1])

            with col_chart:
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=x_vals, y=clean_vals, mode="lines+markers",
                    line=dict(color=t_col, width=2), marker=dict(size=7),
                    name=label, hovertemplate=f"{label}: %{{y}}<extra></extra>",
                ))
                fig3.update_layout(
                    template="plotly_dark", height=180, margin=dict(l=5, r=5, t=5, b=5),
                    showlegend=False, title=dict(text=label, font=dict(size=12)),
                    plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e",
                )
                st.plotly_chart(fig3, use_container_width=True)

            with col_stat:
                st.markdown(f"""
                <div style="background:#1a1f2e;border-radius:6px;padding:12px;margin-top:30px;text-align:center;">
                  <div style="font-size:10px;color:#666;">7-day change</div>
                  <div style="font-size:20px;font-weight:700;color:{t_col};">{sign}{pct}%</div>
                  <div style="font-size:10px;color:#888;">{clean_vals[0]} → {clean_vals[-1]}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("No 7-day trend data available for this machine.")

# ── Tab 4: Maintenance ─────────────────────────────────────────────────────────
with tab_maint:
    history = get_maintenance_history(machine_id=selected_id)
    if history:
        st.markdown(f"**Last maintenance:** {machine['last_maintenance_date']}  |  **Next scheduled:** {machine['next_scheduled_maintenance']}")
        st.markdown(f"**Maintenance cost per event:** ${machine['maintenance_cost_per_event']:,}  |  **Unplanned failure cost/day:** ${machine['unplanned_failure_cost_per_day']:,}")
        st.divider()
        for evt in history:
            evt_col = "#dc3545" if evt["type"] == "unplanned" else "#2E74B5"
            evt_icon = "🔴" if evt["type"] == "unplanned" else "🔵"
            st.markdown(f"""
            <div style="background:#1a1f2e;border-radius:6px;padding:12px;margin-bottom:8px;border-left:3px solid {evt_col};">
              {evt_icon} <strong style="color:{evt_col};">{evt['type'].upper()}</strong>
              <span style="color:#666;font-size:11px;margin-left:12px;">{evt['date']}</span>
              <div style="font-size:13px;color:#ddd;margin-top:4px;">{evt['description']}</div>
              <div style="font-size:11px;color:#555;margin-top:4px;">
                Duration: {evt['duration_days']}d · Cost: ${evt['cost']:,} · Lost: {evt['production_lost_units']} units
                {f" · Root cause: {evt['root_cause']}" if evt.get('root_cause') else ""}
              </div>
            </div>""", unsafe_allow_html=True)

    # Cost risk card
    cost_planned   = machine["maintenance_cost_per_event"]
    cost_unplanned = machine["unplanned_failure_cost_per_day"] * machine["mttr_days"]
    st.divider()
    r1, r2 = st.columns(2)
    with r1:
        st.metric("Planned maintenance cost", f"${cost_planned:,}", delta=None)
    with r2:
        st.metric("Unplanned failure cost (avg downtime)", f"${cost_unplanned:,}",
                  delta=f"${cost_unplanned - cost_planned:,} more expensive", delta_color="inverse")
