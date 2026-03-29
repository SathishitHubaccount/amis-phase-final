"""
AMIS — Scenario Validator
Injects controlled test data (Crisis or Healthy) into the Demand Agent,
runs it, then shows a PASS/FAIL report proving the agent reasons correctly.
This is the "proof of intelligence" page.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st

st.set_page_config(page_title="AMIS · Scenario Validator", page_icon="🔬", layout="wide")

st.markdown("""
<style>
.check-pass { background:#0f2115; border-left:4px solid #28a745; border-radius:6px; padding:10px 14px; margin:4px 0; }
.check-fail { background:#2a1215; border-left:4px solid #dc3545; border-radius:6px; padding:10px 14px; margin:4px 0; }
.check-opt  { background:#1a1f2e; border-left:4px solid #555; border-radius:6px; padding:10px 14px; margin:4px 0; }
.injected   { background:#12151f; border-radius:6px; padding:10px 14px; margin:4px 0;
              border-left:3px solid #2E74B5; font-size:12px; color:#aaa; }
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

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 🔬 Scenario Validator")
st.markdown("<span style='color:#666;font-size:13px;'>Controlled data injection → PASS/FAIL verdict — proving the AI reasons correctly, not hallucinating.</span>", unsafe_allow_html=True)
st.divider()

# ── Explain ─────────────────────────────────────────────────────────────────────
with st.expander("What is this? Why does it matter?", expanded=False):
    st.markdown("""
**The problem with AI systems:** How do you know the LLM is actually reasoning over your data — and not just generating plausible-sounding text?

**AMIS Scenario Validator solves this:**
1. We **inject known, controlled values** into the agent's tools (overriding the normal simulated data)
2. We know exactly what the agent *should* conclude from that data
3. We run the agent and check if it actually reached those conclusions
4. PASS/FAIL for every expected signal

**Crisis Scenario** injects extreme values:
- Stock: only 284 units remaining (stockout in **2.0 days**)
- Demand spike: **+72%** above baseline (1,634 units/week)
- Stockout risk: **91.5%** within 4 weeks
- Monte Carlo: only **8.5%** of simulations avoid stockout

**Healthy Scenario** injects stable values:
- Stock: 8,050 units (**57 days** of supply)
- Demand: stable at baseline, **no anomalies**
- Stockout risk: only **2.1%**
    """)

# ── Scenario selector ──────────────────────────────────────────────────────────
col_select, col_info = st.columns([1, 2])

with col_select:
    scenario_choice = st.radio(
        "Select Scenario",
        ["🔴 CRISIS STATE", "🟢 HEALTHY STATE"],
        index=0,
    )
    scenario_key = "crisis" if "CRISIS" in scenario_choice else "healthy"

from tools.scenario import SCENARIOS
scenario = SCENARIOS[scenario_key]

with col_info:
    scen_color = "#dc3545" if scenario_key == "crisis" else "#28a745"
    st.markdown(f"""
    <div style="background:#1a1f2e;border-radius:8px;padding:16px;border-left:5px solid {scen_color};">
      <div style="font-size:14px;font-weight:600;color:{scen_color};">{scenario['name']}</div>
      <div style="font-size:12px;color:#aaa;margin-top:6px;">{scenario['description']}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Show injected values ────────────────────────────────────────────────────────
st.markdown("#### 💉 Data to be Injected")
st.markdown("<span style='color:#666;font-size:12px;'>These exact values will replace the normal simulated data — the agent will receive ONLY these values.</span>", unsafe_allow_html=True)

inj_cols = st.columns(2)
for i, item in enumerate(scenario["injected_values_summary"]):
    with inj_cols[i % 2]:
        st.markdown(f'<div class="injected">✦ {item}</div>', unsafe_allow_html=True)

# ── Run ────────────────────────────────────────────────────────────────────────
st.divider()

run_prompt = (
    "Run a complete demand analysis. "
    "Check for anomalies, assess inventory status, identify the demand trend, "
    "run a Monte Carlo simulation for the balanced strategy, "
    "and give me your full assessment with specific numbers and recommended actions."
)

col_run, col_note = st.columns([1, 3])
with col_run:
    run_btn = st.button("▶  Run Validation", type="primary", use_container_width=True)
with col_note:
    st.markdown("<span style='color:#666;font-size:12px;'>Runs the Demand Forecasting Agent with injected data, then validates every expected conclusion with PASS/FAIL.</span>", unsafe_allow_html=True)

cache_key = f"validator_result_{scenario_key}"

if run_btn:
    with st.spinner(f"Running {scenario['name']} — agent reasoning with injected data..."):
        from agents.demand_agent import DemandForecastingAgent
        from tools.validator import ScenarioValidator

        agent = DemandForecastingAgent()
        agent.set_tool_overrides(scenario["tool_overrides"])
        final_answer = agent.run(run_prompt)

        validator = ScenarioValidator(scenario, final_answer)
        results   = validator.validate()

        st.session_state[cache_key] = {
            "results":      results,
            "final_answer": final_answer,
            "agent":        agent,
            "scenario":     scenario,
        }

# ── Display results ─────────────────────────────────────────────────────────────
if cache_key in st.session_state:
    data      = st.session_state[cache_key]
    results   = data["results"]
    answer    = data["final_answer"]
    agent_obj = data["agent"]

    required = [r for r in results if r["required"]]
    optional = [r for r in results if not r["required"]]
    req_pass = sum(1 for r in required if r["passed"])
    opt_pass = sum(1 for r in optional if r["passed"])
    total_pass = sum(1 for r in results if r["passed"])

    all_req_pass = req_pass == len(required)

    st.divider()

    # ── Verdict banner ──────────────────────────────────────────────────────────
    if all_req_pass and opt_pass == len(optional):
        verdict, vcol, vicon = "PASS — PERFECT", "#28a745", "✅"
        detail = "Agent correctly identified ALL injected signals (required + optional)."
    elif all_req_pass:
        verdict, vcol, vicon = "PASS", "#28a745", "✅"
        detail = f"Agent correctly identified all {len(required)} required signals."
    elif req_pass >= len(required) // 2:
        verdict, vcol, vicon = "PARTIAL PASS", "#ffc107", "⚠️"
        detail = f"Agent missed {len(required) - req_pass} required signal(s)."
    else:
        verdict, vcol, vicon = "FAIL", "#dc3545", "❌"
        detail = f"Agent failed {len(required) - req_pass} required checks."

    st.markdown(f"""
    <div style="background:#1a1f2e;border-radius:10px;padding:24px;border:2px solid {vcol};text-align:center;margin-bottom:20px;">
      <div style="font-size:40px;margin-bottom:8px;">{vicon}</div>
      <div style="font-size:28px;font-weight:700;color:{vcol};">{verdict}</div>
      <div style="font-size:14px;color:#aaa;margin-top:6px;">{detail}</div>
      <div style="font-size:13px;color:#666;margin-top:10px;">
        Required: {req_pass}/{len(required)} passed ·
        Optional: {opt_pass}/{len(optional)} passed ·
        Total: {total_pass}/{len(results)}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score bar ───────────────────────────────────────────────────────────────
    left_col, right_col = st.columns([3, 2])

    with left_col:
        # Required checks
        st.markdown(f"#### Required Checks  ({req_pass}/{len(required)} passed)")
        for r in required:
            cls   = "check-pass" if r["passed"] else "check-fail"
            icon  = "✓" if r["passed"] else "✗"
            icolor = "#28a745" if r["passed"] else "#dc3545"
            cat   = r.get("category", "")
            desc  = r["description"]
            match = r.get("matched_term", "")
            detail_txt = f'Matched: "{match}"' if r["passed"] and match else \
                         f'Searched: {r.get("search_terms", [])[:3]}' if not r["passed"] else \
                         "No forbidden terms found — correct."
            st.markdown(f"""
            <div class="{cls}">
              <span style="color:{icolor};font-weight:700;">{icon}</span>
              <strong style="color:#ccc;margin-left:8px;">{cat}</strong>
              <div style="font-size:12px;color:#aaa;margin-top:4px;margin-left:18px;">{desc}</div>
              <div style="font-size:11px;color:#555;margin-left:18px;">{detail_txt}</div>
            </div>""", unsafe_allow_html=True)

        if optional:
            st.markdown(f"#### Optional Checks  ({opt_pass}/{len(optional)} passed)")
            for r in optional:
                cls   = "check-pass" if r["passed"] else "check-opt"
                icon  = "✓" if r["passed"] else "○"
                icolor = "#28a745" if r["passed"] else "#555"
                st.markdown(f"""
                <div class="{cls}">
                  <span style="color:{icolor};font-weight:700;">{icon}</span>
                  <strong style="color:#999;margin-left:8px;">{r.get('category','')}</strong>
                  <div style="font-size:12px;color:#777;margin-top:4px;margin-left:18px;">{r['description']}</div>
                </div>""", unsafe_allow_html=True)

    with right_col:
        # Score donut
        import plotly.graph_objects as go
        labels = ["Passed", "Failed"]
        values = [total_pass, len(results) - total_pass]
        colors = [vcol, "#2a1215" if verdict == "FAIL" else "#1a1f2e"]

        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.65,
            marker=dict(colors=colors, line=dict(color="#0e1117", width=2)),
            textinfo="none",
            hovertemplate="%{label}: %{value}<extra></extra>",
        ))
        fig.add_annotation(
            text=f"<b>{total_pass}/{len(results)}</b>",
            x=0.5, y=0.5, font_size=24, showarrow=False,
            font=dict(color=vcol),
        )
        fig.update_layout(
            template="plotly_dark", height=220, margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False, paper_bgcolor="#1a1f2e",
        )
        st.plotly_chart(fig, use_container_width=True)

        # What this proves
        st.markdown(f"""
        <div style="background:#1a1f2e;border-radius:8px;padding:14px;border-left:4px solid {vcol};">
          <div style="font-size:12px;font-weight:600;color:{vcol};margin-bottom:8px;">What this proves</div>
          <div style="font-size:12px;color:#aaa;line-height:1.6;">
            The agent received <strong>known, controlled values</strong>.
            We checked if it reached the <strong>correct conclusions</strong> from that data.
            A PASS verdict means the LLM <strong>actually reasoned</strong> over the injected data —
            not generated canned text.
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Agent's answer ──────────────────────────────────────────────────────────
    with st.expander("📝 View Agent's Full Answer"):
        st.markdown(f"""
        <div style="background:#1a1f2e;border-radius:8px;padding:18px;border-left:4px solid #2E74B5;font-size:13px;color:#ddd;white-space:pre-wrap;">
{answer}
        </div>""", unsafe_allow_html=True)

    # ── Data Flow Trace ─────────────────────────────────────────────────────────
    with st.expander("🔍 Data Flow Trace (Value Reference Audit)"):
        with st.spinner("Building audit..."):
            trace_rpt = agent_obj.get_trace_report(verbose=False)
        st.code(trace_rpt, language=None)
        if st.button("💾 Save trace to file"):
            agent_obj.save_trace(f"output_validation_{scenario_key}.txt")
            st.success(f"Saved to output_validation_{scenario_key}.txt")

else:
    if not run_btn:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
**Crisis State injects:**
- 🔴 Stock: 284 units (2 days supply)
- 🔴 Daily demand: 142 units (+72% spike)
- 🔴 Stockout risk: 91.5%
- 🔴 Monte Carlo: 8.5% safe scenarios

**Expected conclusions the agent must reach:**
- Stockout in 2 days
- Demand spike of ~72%
- Emergency reorder recommended
- Crisis / critical status flagged
            """)
        with col2:
            st.markdown("""
**Healthy State injects:**
- 🟢 Stock: 8,050 units (57 days supply)
- 🟢 Demand: stable, no anomalies
- 🟢 Stockout risk: 2.1%
- 🟢 Monte Carlo: 97.9% safe scenarios

**Expected conclusions the agent must reach:**
- No immediate action needed
- Stock is healthy / well-stocked
- Demand is normal / stable
- Should NOT flag as crisis or emergency
            """)
