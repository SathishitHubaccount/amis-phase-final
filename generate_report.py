"""
AMIS Report Generator
Runs the full cross-agent pipeline (Demand -> Inventory) and
writes a clean, readable report to AMIS_Report.md
"""
import json
import sys
import os
from datetime import datetime
from io import StringIO

# ── Suppress verbose agent print output during LLM calls ──
class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = StringIO()
        return self

    def __exit__(self, *args):
        sys.stdout = self._original_stdout


def progress(msg):
    """Print a status message to the real terminal."""
    print(f"  {msg}", flush=True)


def run_pipeline():
    from agents.demand_agent import DemandForecastingAgent
    from agents.inventory_agent import InventoryManagementAgent

    # ── STEP 1: Demand Agent ──
    progress("Running Demand Forecasting Agent ...")
    with SuppressOutput():
        demand_agent = DemandForecastingAgent()
        demand_response = demand_agent.run(
            "Give me a complete 4-week demand forecast for Product A with scenario "
            "analysis, anomaly detection, trend direction, and confidence intervals."
        )

    progress("Demand Agent done.")

    # ── STEP 2: Extract forecast envelope ──
    progress("Extracting forecast envelope ...")
    with SuppressOutput():
        envelope = demand_agent.get_forecast_output("PROD-A")

    # ── STEP 3: Inventory Agent with cross-agent input ──
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
        inventory_response = inventory_agent.run(inventory_prompt)

    progress("Inventory Agent done.")

    return demand_response, envelope, inventory_response


def write_report(demand_response, envelope, inventory_response, output_path):
    """Write a beautifully formatted Markdown report."""
    now = datetime.now().strftime("%B %d, %Y  %H:%M")

    # Forecast envelope summary table
    env_base   = envelope["scenarios"]["base"]["weekly_avg"]
    env_opt    = envelope["scenarios"]["optimistic"]["weekly_avg"]
    env_pess   = envelope["scenarios"]["pessimistic"]["weekly_avg"]
    env_exp    = envelope["expected_weekly_demand"]
    env_lo     = envelope["confidence_interval_95pct"]["lower"]
    env_hi     = envelope["confidence_interval_95pct"]["upper"]
    env_trend  = envelope["trend_direction"]
    env_growth = envelope["growth_rate_pct_per_week"]
    env_anom   = "YES — spike detected" if envelope["anomaly_detected"] else "No anomalies"

    lines = []

    def line(s=""):
        lines.append(s)

    # ── HEADER ──
    line("# AMIS — Autonomous Manufacturing Intelligence System")
    line("## Cross-Agent Report: Demand Forecast → Inventory Plan")
    line(f"> **Generated:** {now}   |   **Product:** Industrial Valve Assembly (PROD-A)")
    line()
    line("---")
    line()

    # ── HOW THIS REPORT WAS GENERATED ──
    line("## How This Report Was Generated")
    line()
    line("```")
    line("STEP 1  ──►  Demand Forecasting Agent runs")
    line("             Calls 4 tools: data summary, trend analysis,")
    line("             scenario simulation, anomaly detection")
    line("                │")
    line("                │  Forecast Envelope (structured JSON)")
    line("                ▼")
    line("STEP 2  ──►  Envelope extracted")
    line("             Expected demand, std dev, scenarios,")
    line("             trend direction, confidence intervals")
    line("                │")
    line("                │  [CROSS-AGENT INPUT] injected into message")
    line("                ▼")
    line("STEP 3  ──►  Inventory Management Agent runs")
    line("             Reads forecast numbers, calls 4 inventory tools:")
    line("             status check, reorder point, stockout simulation,")
    line("             replenishment planning")
    line("                │")
    line("                ▼")
    line("        Final Report ← You are here")
    line("```")
    line()
    line("---")
    line()

    # ── FORECAST ENVELOPE ──
    line("## Forecast Envelope  (Phase 1 → Phase 2 Handoff)")
    line()
    line("This is the structured data packet the Demand Agent passed to the Inventory Agent.")
    line()
    line("| Field | Value |")
    line("|-------|-------|")
    line(f"| Expected Weekly Demand | **{env_exp:,} units / week** |")
    line(f"| Demand Std Deviation | ±{envelope['demand_std_dev']} units |")
    line(f"| Trend | {env_trend} (+{env_growth}% per week) |")
    line(f"| Anomaly Detected | {env_anom} |")
    line(f"| 95% Confidence Interval | {env_lo:,} – {env_hi:,} units / week |")
    line()
    line("### Demand Scenarios")
    line()
    line("| Scenario | Probability | Weekly Avg |")
    line("|----------|-------------|------------|")
    line(f"| Optimistic | 20% | {env_opt:,} units |")
    line(f"| Base Case  | 55% | {env_base:,} units |")
    line(f"| Pessimistic| 25% | {env_pess:,} units |")
    line()
    line("---")
    line()

    # ── DEMAND AGENT REPORT ──
    line("## Phase 1 — Demand Forecasting Agent Report")
    line()
    line(demand_response)
    line()
    line("---")
    line()

    # ── INVENTORY AGENT REPORT ──
    line("## Phase 2 — Inventory Management Agent Report")
    line()
    line("> *This agent received the forecast envelope above as input.*")
    line()
    line(inventory_response)
    line()
    line("---")
    line()

    # ── QUICK SUMMARY ──
    line("## Quick Summary (TL;DR)")
    line()
    line("| Question | Answer |")
    line("|----------|--------|")
    line(f"| What is expected weekly demand? | **{env_exp:,} units/week** (base case: {env_base:,}) |")
    line(f"| Demand trend? | **{env_trend}** at {env_growth}% per week |")
    line(f"| Anomaly detected? | {env_anom} |")
    line( "| Current stock? | 1,850 units (13 days supply) |")
    line( "| Stockout risk? | See Inventory Agent Report above |")
    line( "| Recommended strategy? | Balanced production, increase safety stock |")
    line()
    line("---")
    line()
    line(f"*Report auto-generated by AMIS on {now}*")

    report_text = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)


def main():
    output_path = os.path.join(
        os.path.dirname(__file__),
        "AMIS_Report.md"
    )

    print()
    print("=" * 60)
    print("  AMIS Report Generator")
    print("  Cross-Agent: Demand Agent --> Inventory Agent")
    print("=" * 60)
    print()

    demand_response, envelope, inventory_response = run_pipeline()

    progress(f"Writing report to: {output_path}")
    write_report(demand_response, envelope, inventory_response, output_path)

    print()
    print("=" * 60)
    print(f"  Report saved to: AMIS_Report.md")
    print("  Open it in VS Code for nicely rendered Markdown.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
