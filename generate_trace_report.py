"""
AMIS Trace Report Generator
Shows exactly what the LLM is thinking at every step:
  - What was fed to the LLM (input)
  - What the LLM reasoned / decided
  - Which tool it called and with what arguments
  - What the tool returned (raw data)
  - The LLM's final answer

Output: AMIS_Trace_Report.md
"""
import json
import sys
import os
from datetime import datetime
from io import StringIO


class SuppressOutput:
    """Redirect stdout during LLM calls so only progress messages show."""
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = StringIO()
        return self

    def __exit__(self, *args):
        sys.stdout = self._original_stdout


def progress(msg):
    print(f"  {msg}", flush=True)


def run_pipeline():
    from agents.demand_agent import DemandForecastingAgent
    from agents.inventory_agent import InventoryManagementAgent

    progress("Running Demand Forecasting Agent ...")
    with SuppressOutput():
        demand_agent = DemandForecastingAgent()
        demand_agent.run(
            "Give me a complete 4-week demand forecast for Product A with scenario "
            "analysis, anomaly detection, trend direction, and confidence intervals."
        )
    progress("Demand Agent done.")

    progress("Extracting forecast envelope ...")
    with SuppressOutput():
        envelope = demand_agent.get_forecast_output("PROD-A")

    progress("Running Inventory Management Agent with demand forecast ...")
    inventory_prompt = (
        f"[CROSS-AGENT INPUT: Demand Forecast]\n"
        f"{json.dumps(envelope, indent=2)}\n"
        f"[END CROSS-AGENT INPUT]\n\n"
        f"Based on this demand forecast, provide a complete inventory plan: "
        f"assess current position, simulate stockout risk, optimize safety stock, "
        f"and generate a 4-week replenishment schedule."
    )
    with SuppressOutput():
        inventory_agent = InventoryManagementAgent()
        inventory_agent.run(inventory_prompt)
    progress("Inventory Agent done.")

    return demand_agent.trace, inventory_agent.trace, envelope


# ── Helpers ──────────────────────────────────────────────────────────────────

def _fmt_json(value):
    """Try to pretty-print a JSON string; return as-is if it fails."""
    if isinstance(value, str):
        try:
            return json.dumps(json.loads(value), indent=2)
        except Exception:
            return value
    return json.dumps(value, indent=2)


TOOL_DESCRIPTIONS = {
    # Demand tools
    "get_demand_data_summary":        "Fetches raw demand history, inventory levels, and market context",
    "simulate_demand_scenarios":      "Runs base / optimistic / pessimistic scenario simulations",
    "analyze_demand_trends":          "Calculates trend slope, growth rate, volatility, and seasonality",
    "monte_carlo_profit_simulation":  "Runs 1,000 profit simulations across production strategies",
    "compare_production_strategies":  "Compares conservative / balanced / aggressive strategies",
    "detect_demand_anomalies":        "Finds statistical spikes/dips and diagnoses root causes",
    # Inventory tools
    "get_inventory_status":           "Fetches current stock, pipeline orders, warehouse & supplier data",
    "calculate_reorder_point":        "Calculates ROP = (demand × lead time) + safety stock (Z-score)",
    "optimize_safety_stock":          "Finds optimal safety stock across 85–99% service levels",
    "simulate_stockout_risk":         "Monte Carlo: probability of stockout over N days",
    "evaluate_holding_costs":         "EOQ analysis — holding cost vs stockout cost tradeoff",
    "generate_replenishment_plan":    "Builds a 4-week week-by-week replenishment schedule",
}


# ── Report writer ─────────────────────────────────────────────────────────────

def write_trace_report(demand_trace, inventory_trace, envelope, output_path):
    now = datetime.now().strftime("%B %d, %Y  %H:%M")
    lines = []

    def L(s=""):
        lines.append(s)

    # ── HEADER ───────────────────────────────────────────────────────────────
    L("# AMIS — Full LLM Reasoning Trace")
    L("## Step-by-Step: What the LLM Is Thinking")
    L(f"> **Generated:** {now}   |   **Product:** Industrial Valve Assembly (PROD-A)")
    L()
    L("> This report traces every step of the cross-agent pipeline:")
    L("> **Input → LLM Thinks → Calls Tool → Gets Data → Thinks Again → Final Answer**")
    L()
    L("---")
    L()

    # ── HOW TO READ THIS REPORT ──────────────────────────────────────────────
    L("## How to Read This Report")
    L()
    L("| Symbol | Meaning |")
    L("|--------|---------|")
    L("| `USER INPUT` | The prompt sent to start the agent |")
    L("| `ITERATION N` | One round-trip to the LLM |")
    L("| `LLM THINKING` | The LLM's reasoning before choosing an action |")
    L("| `TOOL CALL` | The LLM decided it needs data and calls a function |")
    L("| `TOOL RESULT` | Raw data returned from the function |")
    L("| `FINAL ANSWER` | LLM has enough data — writes its response |")
    L()
    L("---")
    L()

    def write_agent_section(agent_label, trace):
        L(f"# {agent_label}")
        L()

        iter_num = 0
        step = 0
        pending_tool_calls = {}  # tool_id -> tool_name (for matching results to calls)

        for event in trace:
            etype = event["type"]

            # ── USER INPUT ───────────────────────────────────────────────────
            if etype == "user_input":
                step += 1
                L(f"## Step {step} — User Input (Prompt Sent to LLM)")
                L()
                L("> *This is the task the user (or orchestrator) gave the agent:*")
                L()

                content = event["content"]
                # Highlight cross-agent input blocks
                if "[CROSS-AGENT INPUT" in content:
                    parts = content.split("[CROSS-AGENT INPUT: Demand Forecast]")
                    L(parts[0].strip())
                    L()
                    L("**[CROSS-AGENT INPUT block — forecast data from Demand Agent:]**")
                    L()
                    inner = parts[1].split("[END CROSS-AGENT INPUT]")
                    L("```json")
                    L(inner[0].strip())
                    L("```")
                    L()
                    if len(inner) > 1 and inner[1].strip():
                        L(inner[1].strip())
                else:
                    L("```")
                    L(content)
                    L("```")
                L()
                L("---")
                L()

            # ── ITERATION START ──────────────────────────────────────────────
            elif etype == "iteration_start":
                iter_num = event["iteration"]
                step += 1
                L(f"## Step {step} — LLM Iteration {iter_num}")
                L()
                L(f"> *The LLM now has **{event['message_count']} messages** in context (system prompt + conversation so far).*")
                L()

            # ── LLM THINKING ─────────────────────────────────────────────────
            elif etype == "llm_thinking":
                L("### LLM Reasoning")
                L()
                L("> *The LLM reads all context and reasons about what to do next:*")
                L()
                for ln in event["text"].split("\n"):
                    L(ln)
                L()

            # ── TOOL CALL ────────────────────────────────────────────────────
            elif etype == "tool_call":
                tool = event["tool"]
                args = event["args"]
                tid  = event["tool_id"]
                desc = TOOL_DESCRIPTIONS.get(tool, "")
                pending_tool_calls[tid] = tool

                L(f"### LLM Decision: Call `{tool}`")
                L()
                if desc:
                    L(f"> **What this tool does:** {desc}")
                    L()
                L("**Arguments the LLM is passing:**")
                L()
                L("```json")
                L(json.dumps(args, indent=2))
                L("```")
                L()

            # ── TOOL RESULT ──────────────────────────────────────────────────
            elif etype == "tool_result":
                tool = event["tool"]
                L(f"### Tool Result from `{tool}`")
                L()
                L("> *This raw data is injected back into the LLM's context:*")
                L()
                L("```json")
                L(_fmt_json(event["result"]))
                L("```")
                L()
                L("---")
                L()

            # ── FINAL ANSWER ─────────────────────────────────────────────────
            elif etype == "final_answer":
                step += 1
                L(f"## Step {step} — LLM Final Answer")
                L()
                L("> *The LLM now has all the data it needs and writes its final response.*")
                L()
                for ln in event["content"].split("\n"):
                    L(ln)
                L()
                L("---")
                L()

    # ── DEMAND AGENT ─────────────────────────────────────────────────────────
    write_agent_section("Phase 1 — Demand Forecasting Agent", demand_trace)

    # ── CROSS-AGENT HANDOFF ──────────────────────────────────────────────────
    L("---")
    L()
    L("# Cross-Agent Handoff: Forecast Envelope")
    L()
    L("> *After the Demand Agent finishes, `get_forecast_output()` is called.*")
    L("> *It runs tools programmatically to produce a structured JSON packet.*")
    L("> *This packet is injected into the Inventory Agent's first message.*")
    L()
    L("| Field | Value |")
    L("|-------|-------|")
    L(f"| Expected Weekly Demand | **{envelope['expected_weekly_demand']:,} units / week** |")
    L(f"| Std Deviation | ±{envelope['demand_std_dev']} units |")
    L(f"| Trend | {envelope['trend_direction']} (+{envelope['growth_rate_pct_per_week']}% / week) |")
    L(f"| Anomaly Detected | {'YES — spike detected' if envelope['anomaly_detected'] else 'No'} |")
    L(f"| 95% CI | {envelope['confidence_interval_95pct']['lower']:,} – {envelope['confidence_interval_95pct']['upper']:,} units |")
    L()
    L("**Full JSON packet:**")
    L()
    L("```json")
    L(json.dumps(envelope, indent=2))
    L("```")
    L()
    L("---")
    L()

    # ── INVENTORY AGENT ──────────────────────────────────────────────────────
    write_agent_section("Phase 2 — Inventory Management Agent", inventory_trace)

    # ── FOOTER ───────────────────────────────────────────────────────────────
    L(f"*Trace report auto-generated by AMIS on {now}*")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    output_path = os.path.join(
        os.path.dirname(__file__),
        "AMIS_Trace_Report.md"
    )

    print()
    print("=" * 60)
    print("  AMIS Trace Report Generator")
    print("  Shows every LLM reasoning step in clean Markdown")
    print("=" * 60)
    print()

    demand_trace, inventory_trace, envelope = run_pipeline()

    progress(f"Writing trace report to: {output_path}")
    write_trace_report(demand_trace, inventory_trace, envelope, output_path)

    print()
    print("=" * 60)
    print("  Trace report saved to: AMIS_Trace_Report.md")
    print("  Open in VS Code → Ctrl+Shift+V for Markdown preview.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
