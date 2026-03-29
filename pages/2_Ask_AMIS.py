"""
AMIS — Ask AMIS
Interactive agent runner. Select an agent, pick a preset or type your own question,
watch it run, then see the full data flow trace proving the LLM used real data.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import time

st.set_page_config(page_title="AMIS · Ask AMIS", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.trace-header { font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#666; margin:12px 0 6px 0; }
.answer-box { background:#1a1f2e; border-radius:8px; padding:20px; border-left:4px solid #2E74B5; }
.audit-badge {
    display:inline-block; background:#1a2e1a; border:1px solid #28a745;
    border-radius:4px; padding:2px 8px; font-size:11px; color:#28a745; margin-right:6px;
}
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

# ── Agent & preset definitions ─────────────────────────────────────────────────
AGENTS = {
    "🤖 Orchestrator — Full Pipeline": {
        "class": "OrchestratorAgent",
        "module": "agents.orchestrator_agent",
        "presets": {
            "Weekly Manufacturing Brief": (
                "Give me a complete weekly manufacturing intelligence brief. "
                "Run all 5 agents, identify cross-domain risks, and tell me the top 3 things I need to act on today."
            ),
            "Emergency Re-Plan (MCH-002 failure)": (
                "URGENT: MCH-002 on Line 2 has just failed unexpectedly. "
                "Re-assess our full manufacturing situation. What's our revised capacity? "
                "What production do we lose this week? What should we do about inventory and suppliers immediately?"
            ),
            "Can we take a 2,000 unit rush order?": (
                "A key client wants 2,000 units delivered within 3 weeks. "
                "Given our current production capacity, inventory levels, machine health, and supplier situation, "
                "can we safely commit to this? What's our risk exposure?"
            ),
        },
    },
    "📈 Demand Forecasting Agent": {
        "class": "DemandForecastingAgent",
        "module": "agents.demand_agent",
        "presets": {
            "Full demand analysis": (
                "Run a complete demand analysis for PROD-A. "
                "Check for anomalies, give me the 4-week forecast with all three scenarios (pessimistic/base/optimistic), "
                "assess our demand trend, and recommend which production strategy to adopt."
            ),
            "Investigate the demand spike": (
                "There was a demand spike 3 weeks ago. What caused it? "
                "Is it a one-time event or the start of a new trend? "
                "Should we adjust our production target upward?"
            ),
            "Strategy: Conservative vs Aggressive": (
                "Compare the conservative and aggressive production strategies for the next 4 weeks. "
                "What are the financial implications and risks of each? Which do you recommend?"
            ),
        },
    },
    "📦 Inventory Management Agent": {
        "class": "InventoryManagementAgent",
        "module": "agents.inventory_agent",
        "presets": {
            "Full inventory analysis": (
                "Run a complete inventory analysis. Check our current stock levels, "
                "assess stockout risk for the next 4 weeks, evaluate our safety stock adequacy, "
                "and generate a replenishment schedule."
            ),
            "Are we at risk of stockout?": (
                "With our current inventory and consumption rate, when exactly will we run out? "
                "What's our stockout probability? Do we need an emergency reorder?"
            ),
            "Optimise our safety stock level": (
                "Our current safety stock is 300 units. Is this too high, too low, or correct? "
                "Calculate the optimal safety stock given our demand variability and supplier lead times."
            ),
        },
    },
    "⚙️ Machine Health Agent": {
        "class": "MachineHealthAgent",
        "module": "agents.machine_health_agent",
        "presets": {
            "Full fleet health check": (
                "Give me a complete machine health assessment for the entire fleet. "
                "Which machines are at risk? What is our production capacity ceiling this week? "
                "What maintenance do we need to schedule immediately?"
            ),
            "MCH-002 failure risk analysis": (
                "Focus on MCH-002 (CNC Machining Center on Line 2). "
                "Analyse its sensor readings, vibration trend, and OEE history. "
                "What is the failure probability in the next 48 hours? What should we do?"
            ),
            "This week's maintenance schedule": (
                "Build a maintenance schedule for this week. "
                "Which machines need immediate attention? Which can wait? "
                "What's the cost if we delay maintenance on each critical machine?"
            ),
        },
    },
    "🚚 Supplier & Procurement Agent": {
        "class": "SupplierProcurementAgent",
        "module": "agents.supplier_agent",
        "presets": {
            "Full procurement plan": (
                "Generate a complete procurement plan for the next 4 weeks. "
                "Evaluate all suppliers, generate purchase orders, and flag any supply chain risks."
            ),
            "Supply chain risk audit": (
                "Run a full supply chain risk audit. "
                "Which components are single-sourced? Where do we have geographic risk? "
                "What's our exposure if Supplier A has a disruption?"
            ),
        },
    },
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 🤖 Ask AMIS")
st.markdown("<span style='color:#666;font-size:13px;'>Select an agent, choose a question or type your own, and watch it reason with real manufacturing data.</span>", unsafe_allow_html=True)
st.divider()

# ── Controls ───────────────────────────────────────────────────────────────────
ctrl_col, result_col = st.columns([1, 2])

with ctrl_col:
    agent_name = st.selectbox("Select Agent", list(AGENTS.keys()))
    agent_cfg  = AGENTS[agent_name]

    preset_options = ["✏️ Custom question..."] + list(agent_cfg["presets"].keys())
    preset_choice  = st.selectbox("Preset question", preset_options)

    if preset_choice == "✏️ Custom question...":
        question = st.text_area("Your question", height=140,
                                placeholder="Type your manufacturing question here...")
    else:
        question = agent_cfg["presets"][preset_choice]
        st.markdown(f"""
        <div style="background:#1a1f2e;border-radius:6px;padding:12px;font-size:12px;color:#aaa;border-left:3px solid #2E74B5;">
        {question}
        </div>""", unsafe_allow_html=True)

    show_trace = st.toggle("Show Data Flow Trace (audit)", value=False)
    run_clicked = st.button("▶  Run Agent", type="primary", use_container_width=True, disabled=not question.strip())

    st.divider()
    st.caption("**Data Flow Trace** audits which specific values from tool outputs the LLM cited in its answer — proving it reasons over real data, not generated text.")

# ── Run and display ────────────────────────────────────────────────────────────
with result_col:
    if run_clicked and question.strip():
        # Instantiate agent
        module_name = agent_cfg["module"]
        class_name  = agent_cfg["class"]

        with st.spinner(f"🔄 {agent_name.split('—')[-1].strip()} is reasoning..."):
            try:
                import importlib
                mod   = importlib.import_module(module_name)
                cls   = getattr(mod, class_name)
                agent = cls()
                answer = agent.run(question)
                st.session_state[f"last_answer_{agent_name}"]  = answer
                st.session_state[f"last_agent_{agent_name}"]   = agent
                st.session_state[f"last_question_{agent_name}"] = question
            except Exception as e:
                st.error(f"Agent error: {e}")
                st.stop()

        # Show answer
        st.markdown("#### Agent Response")
        st.markdown(f"""
        <div class="answer-box">
        {answer.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        # Save to session for trace toggle
        st.session_state["_last_agent_obj"]  = agent
        st.session_state["_last_answer_txt"] = answer
        st.session_state["_show_trace"]      = show_trace

    elif f"last_answer_{agent_name}" in st.session_state:
        # Restore previous result for this agent
        answer = st.session_state[f"last_answer_{agent_name}"]
        agent  = st.session_state.get(f"last_agent_{agent_name}")
        q      = st.session_state.get(f"last_question_{agent_name}", "")

        st.markdown(f"<div style='font-size:11px;color:#555;margin-bottom:8px;'>Last question: {q[:80]}...</div>", unsafe_allow_html=True)
        st.markdown("#### Agent Response")
        st.markdown(f"""
        <div class="answer-box">
        {answer.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        st.session_state["_last_agent_obj"]  = agent
        st.session_state["_last_answer_txt"] = answer
        st.session_state["_show_trace"]      = show_trace
    else:
        st.info("Select an agent and question on the left, then click **▶ Run Agent**.")
        st.markdown("""
**How AMIS works:**

1. Your question goes to the selected agent
2. The agent uses the **ReAct loop** — it reasons, picks a tool, runs it, reads the result, reasons again
3. After using all necessary tools, it synthesises a final answer
4. The **Data Flow Trace** then shows exactly which data values the LLM cited in its answer
        """)
        st.stop()

# ── Data Flow Trace ────────────────────────────────────────────────────────────
agent_obj  = st.session_state.get("_last_agent_obj")
answer_txt = st.session_state.get("_last_answer_txt", "")

if show_trace and agent_obj and hasattr(agent_obj, "get_trace_report"):
    st.divider()
    st.markdown("### 🔍 Data Flow Trace")
    st.markdown("<span style='color:#666;font-size:12px;'>Every tool call, its output, and which values the LLM actually cited in its answer.</span>", unsafe_allow_html=True)

    with st.spinner("Building trace report..."):
        trace_report = agent_obj.get_trace_report(verbose=False)

    # Parse and display sections
    sections = trace_report.split("─" * 78)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if "VALUE REFERENCE AUDIT" in section:
            st.markdown('<div class="trace-header">Value Reference Audit</div>', unsafe_allow_html=True)
            lines = section.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("✓"):
                    st.markdown(f"<span class='audit-badge'>✓ {line[1:].strip()}</span>", unsafe_allow_html=True)
                elif "SUMMARY" in line:
                    st.success(line.replace("SUMMARY :", "").strip())
                elif "VERDICT" in line:
                    if "CONFIRMED" in line:
                        st.success(f"**Verdict:** {line.split(':', 1)[-1].strip()}")
                    elif "LIKELY" in line:
                        st.info(f"**Verdict:** {line.split(':', 1)[-1].strip()}")
                    else:
                        st.warning(f"**Verdict:** {line.split(':', 1)[-1].strip()}")
                elif "→" in line:
                    parts = line.split("→", 1)
                    st.markdown(f"`{parts[0].strip()}` → **{parts[1].strip()}**")
        elif "ITERATION" in section:
            iter_lines = section.split("\n")
            iter_title = next((l for l in iter_lines if "ITERATION" in l), "Iteration")
            with st.expander(iter_title.strip(), expanded=False):
                st.code(section, language=None)
        elif "FINAL LLM ANSWER" in section:
            pass  # Already shown above
        else:
            if len(section) > 20:
                st.code(section, language=None)

    # Save trace to file option
    col_save, _ = st.columns([1, 3])
    with col_save:
        if st.button("💾 Save full trace to file"):
            path = "output_trace_ask_amis.txt"
            agent_obj.save_trace(path)
            st.success(f"Saved to {path}")
