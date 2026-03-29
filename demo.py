"""
AMIS - Demo Script
Runs pre-built scenarios to showcase all agents.

Usage: python demo.py [scenario_number]
  1 = Full Demand Analysis
  2 = Anomaly Investigation
  3 = Strategy Recommendation
  4 = Rush Order Assessment
  5 = Full Inventory Analysis
  6 = Safety Stock Optimization
  7 = Cross-Agent: Demand -> Inventory
  8 = Full Machine Health Assessment
  9 = Failure Risk Deep-Dive (MCH-002)
 10 = Cross-Agent: Machine Health -> Production Planning
 11 = Full Procurement Plan
 12 = Supply Chain Risk Audit
 13 = Cross-Agent: Production Planning -> Supplier
 14 = Full Pipeline (Orchestrator - all 5 agents)
 15 = Emergency Re-Plan (Orchestrator)
 16 = Data Flow Trace: Demand Agent  (proves LLM reasons over real tool data)
 17 = Data Flow Trace: Full Pipeline (traces all 6 agents + orchestrator LLM)
 18 = Scenario Validation: CRITICAL STATE
 19 = Scenario Validation: HEALTHY STATE
"""
import sys
import json

# Ensure Unicode characters display correctly on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from agents.demand_agent import DemandForecastingAgent
from agents.inventory_agent import InventoryManagementAgent
from agents.machine_health_agent import MachineHealthAgent
from agents.production_agent import ProductionPlanningAgent
from agents.supplier_agent import SupplierProcurementAgent
from agents.orchestrator_agent import OrchestratorAgent
from prompts.demand_prompts import EXAMPLE_PROMPTS as DEMAND_EXAMPLES, ORCHESTRATOR_TO_DEMAND
from prompts.inventory_prompts import EXAMPLE_PROMPTS as INVENTORY_EXAMPLES
from prompts.machine_health_prompts import EXAMPLE_PROMPTS as MACHINE_HEALTH_EXAMPLES
from prompts.production_prompts import EXAMPLE_PROMPTS as PRODUCTION_EXAMPLES
from prompts.supplier_prompts import EXAMPLE_PROMPTS as SUPPLIER_EXAMPLES
from prompts.orchestrator_prompts import EXAMPLE_PROMPTS as ORCHESTRATOR_EXAMPLES


def run_demand_demo(scenario_config):
    agent = DemandForecastingAgent()
    print(f"\nSENDING TO AGENT:\n{'─'*70}")
    print(scenario_config["prompt"])
    print(f"{'─'*70}")
    response = agent.run(scenario_config["prompt"])
    print(f"\n{'═'*70}\nDEMAND FORECASTING AGENT RESPONSE:\n{'═'*70}")
    print(response)
    print(f"{'═'*70}")
    return agent


def run_inventory_demo(scenario_config):
    agent = InventoryManagementAgent()
    print(f"\nSENDING TO AGENT:\n{'─'*70}")
    print(scenario_config["prompt"])
    print(f"{'─'*70}")
    response = agent.run(scenario_config["prompt"])
    print(f"\n{'═'*70}\nINVENTORY MANAGEMENT AGENT RESPONSE:\n{'═'*70}")
    print(response)
    print(f"{'═'*70}")
    return agent


def run_machine_health_demo(scenario_config):
    agent = MachineHealthAgent()
    print(f"\nSENDING TO AGENT:\n{'─'*70}")
    print(scenario_config["prompt"])
    print(f"{'─'*70}")
    response = agent.run(scenario_config["prompt"])
    print(f"\n{'═'*70}\nMACHINE HEALTH AGENT RESPONSE:\n{'═'*70}")
    print(response)
    print(f"{'═'*70}")
    return agent


def run_production_demo(scenario_config):
    agent = ProductionPlanningAgent()
    print(f"\nSENDING TO AGENT:\n{'─'*70}")
    print(scenario_config["prompt"])
    print(f"{'─'*70}")
    response = agent.run(scenario_config["prompt"])
    print(f"\n{'═'*70}\nPRODUCTION PLANNING AGENT RESPONSE:\n{'═'*70}")
    print(response)
    print(f"{'═'*70}")
    return agent


def run_cross_agent_demand_inventory():
    """Cross-agent: Demand Agent -> Inventory Agent."""
    print(f"\n{'#'*70}")
    print(f"#  CROSS-AGENT DEMO: Demand Agent -> Inventory Agent")
    print(f"#  Step 1: Demand Agent produces a forecast")
    print(f"#  Step 2: Forecast envelope is extracted (structured data)")
    print(f"#  Step 3: Inventory Agent consumes the forecast")
    print(f"{'#'*70}")

    print(f"\n{'='*70}\n  STEP 1: Running Demand Forecasting Agent...\n{'='*70}")
    demand_agent = DemandForecastingAgent()
    demand_prompt = (
        "Give me a 4-week demand forecast for Product A with scenario analysis. "
        "Include expected demand, confidence intervals, and trend direction."
    )
    demand_response = demand_agent.run(demand_prompt)
    print(f"\n{'═'*70}\nDEMAND AGENT RESPONSE:\n{'═'*70}")
    print(demand_response)

    print(f"\n{'='*70}\n  STEP 2: Extracting structured forecast envelope...\n{'='*70}")
    forecast_envelope = demand_agent.get_forecast_output("PROD-A")
    print(f"\n  FORECAST ENVELOPE (passed to Inventory Agent):\n{'─'*70}")
    print(json.dumps(forecast_envelope, indent=2))

    print(f"\n{'='*70}\n  STEP 3: Running Inventory Agent with demand forecast...\n{'='*70}")
    inventory_agent = InventoryManagementAgent()
    inventory_prompt = (
        f"[CROSS-AGENT INPUT: Demand Forecast]\n"
        f"{json.dumps(forecast_envelope, indent=2)}\n"
        f"[END CROSS-AGENT INPUT]\n\n"
        f"Based on this demand forecast from the Demand Agent, create a complete "
        f"inventory plan: assess our current stock position, check stockout risk, "
        f"evaluate if our safety stock is appropriate, and generate a 4-week "
        f"replenishment schedule."
    )
    inventory_response = inventory_agent.run(inventory_prompt)
    print(f"\n{'═'*70}\nINVENTORY AGENT RESPONSE:\n{'═'*70}")
    print(inventory_response)
    print(f"\n{'#'*70}\n#  CROSS-AGENT DEMO COMPLETE\n{'#'*70}")


def run_supplier_demo(scenario_config):
    agent = SupplierProcurementAgent()
    print(f"\nSENDING TO AGENT:\n{'─'*70}")
    print(scenario_config["prompt"])
    print(f"{'─'*70}")
    response = agent.run(scenario_config["prompt"])
    print(f"\n{'═'*70}\nSUPPLIER & PROCUREMENT AGENT RESPONSE:\n{'═'*70}")
    print(response)
    print(f"{'═'*70}")
    return agent


def run_cross_agent_production_supplier():
    """Cross-agent: Production Planning Agent -> Supplier & Procurement Agent."""
    print(f"\n{'#'*70}")
    print(f"#  CROSS-AGENT DEMO: Production Planning -> Supplier & Procurement")
    print(f"#  Step 1: Production Planning Agent builds MPS + material requirements")
    print(f"#  Step 2: Production envelope is extracted (structured data)")
    print(f"#  Step 3: Supplier Agent procures materials and assesses supply risk")
    print(f"{'#'*70}")

    print(f"\n{'='*70}\n  STEP 1: Running Production Planning Agent...\n{'='*70}")
    production_agent = ProductionPlanningAgent()
    production_prompt = (
        "Build a 4-week production plan for PROD-A with a target of 980 units/week. "
        "Line 4 is currently down and MCH-002 on Line 2 needs maintenance in Week 1. "
        "Calculate the material requirements we need to hand off to the Supplier Agent."
    )
    production_response = production_agent.run(production_prompt)
    print(f"\n{'═'*70}\nPRODUCTION PLANNING AGENT RESPONSE:\n{'═'*70}")
    print(production_response)

    print(f"\n{'='*70}\n  STEP 2: Extracting structured production envelope...\n{'='*70}")
    production_envelope = production_agent.get_production_output("PROD-A", 4)
    print(f"\n  PRODUCTION ENVELOPE (passed to Supplier Agent):\n{'─'*70}")
    print(json.dumps(production_envelope, indent=2))

    print(f"\n{'='*70}\n  STEP 3: Running Supplier Agent with production requirements...\n{'='*70}")
    supplier_agent = SupplierProcurementAgent()
    cross_agent_data = production_envelope.get("cross_agent_output_for_supplier", {})
    supplier_prompt = (
        f"[CROSS-AGENT INPUT: Production Plan]\n"
        f"{json.dumps(production_envelope, indent=2)}\n"
        f"[END CROSS-AGENT INPUT]\n\n"
        f"The Production Planning Agent has provided the 4-week material requirements above. "
        f"Our production target is {production_envelope['weekly_production_target']} units/week. "
        f"Procurement alerts flagged: {production_envelope.get('procurement_alerts', [])}.\n\n"
        f"Please: (1) Evaluate our supplier options for each key component, "
        f"(2) Assess supply chain risks — especially for flagged components, "
        f"(3) Generate a complete purchase order package, "
        f"(4) Recommend dual-sourcing for any high-risk components."
    )
    supplier_response = supplier_agent.run(supplier_prompt)
    print(f"\n{'═'*70}\nSUPPLIER & PROCUREMENT AGENT RESPONSE:\n{'═'*70}")
    print(supplier_response)

    print(f"\n{'#'*70}")
    print(f"#  CROSS-AGENT DEMO COMPLETE")
    print(f"#  Production Planning set the material requirements.")
    print(f"#  Supplier Agent evaluated suppliers, assessed risk, and generated POs.")
    print(f"{'#'*70}")


def run_cross_agent_machine_production():
    """Cross-agent: Machine Health Agent -> Production Planning Agent."""
    print(f"\n{'#'*70}")
    print(f"#  CROSS-AGENT DEMO: Machine Health -> Production Planning")
    print(f"#  Step 1: Machine Health Agent assesses capacity and maintenance needs")
    print(f"#  Step 2: Capacity envelope is extracted (structured data)")
    print(f"#  Step 3: Production Planning Agent builds MPS using capacity ceiling")
    print(f"{'#'*70}")

    print(f"\n{'='*70}\n  STEP 1: Running Machine Health Agent...\n{'='*70}")
    machine_agent = MachineHealthAgent()
    machine_prompt = (
        "Give me a complete machine health assessment. Which machines are at risk? "
        "What is our current production capacity ceiling? What maintenance do we need "
        "this week? Provide all details the Production Planning Agent will need."
    )
    machine_response = machine_agent.run(machine_prompt)
    print(f"\n{'═'*70}\nMACHINE HEALTH AGENT RESPONSE:\n{'═'*70}")
    print(machine_response)

    print(f"\n{'='*70}\n  STEP 2: Extracting structured capacity envelope...\n{'='*70}")
    capacity_envelope = machine_agent.get_capacity_output("PLANT-01")
    print(f"\n  CAPACITY ENVELOPE (passed to Production Planning Agent):\n{'─'*70}")
    print(json.dumps(capacity_envelope, indent=2))

    print(f"\n{'='*70}\n  STEP 3: Running Production Planning Agent with capacity data...\n{'='*70}")
    production_agent = ProductionPlanningAgent()
    production_prompt = (
        f"[CROSS-AGENT INPUT: Machine Health Report]\n"
        f"{json.dumps(capacity_envelope, indent=2)}\n"
        f"[END CROSS-AGENT INPUT]\n\n"
        f"The Machine Health Agent has provided our current capacity assessment above. "
        f"Our demand target is 1,050 units/week (base scenario from Demand Agent). "
        f"Build a 4-week Master Production Schedule that respects the capacity ceiling "
        f"and accounts for all maintenance windows. Include capacity gap analysis, "
        f"overtime decisions, and generate the material requirements list for the Supplier Agent."
    )
    production_response = production_agent.run(production_prompt)
    print(f"\n{'═'*70}\nPRODUCTION PLANNING AGENT RESPONSE:\n{'═'*70}")
    print(production_response)

    print(f"\n{'#'*70}")
    print(f"#  CROSS-AGENT DEMO COMPLETE")
    print(f"#  Machine Health set the capacity ceiling.")
    print(f"#  Production Planning built the MPS and generated material requirements.")
    print(f"{'#'*70}")


def run_orchestrator_demo(scenario_config):
    """Run the Orchestrator Agent with a specific prompt."""
    agent = OrchestratorAgent()
    print(f"\nSENDING TO AGENT:\n{'─'*70}")
    print(scenario_config["prompt"])
    print(f"{'─'*70}")
    response = agent.run(scenario_config["prompt"])
    print(f"\n{'═'*70}\nORCHESTRATOR AGENT RESPONSE:\n{'═'*70}")
    print(response)
    print(f"{'═'*70}")
    return agent


def run_full_pipeline_demo():
    """Full pipeline: Orchestrator runs all 5 agents programmatically, then synthesizes."""
    print(f"\n{'#'*70}")
    print(f"#  FULL PIPELINE DEMO: Orchestrator runs all 5 agents")
    print(f"#  Demand → Inventory → Machine Health → Production → Supplier → Synthesize")
    print(f"{'#'*70}")

    orchestrator = OrchestratorAgent()

    print(f"\n{'='*70}")
    print(f"  Running full AMIS pipeline programmatically...")
    print(f"  (Each agent's bridge method called in sequence — no LLM loops)")
    print(f"{'='*70}\n")

    result = orchestrator.run_full_pipeline(
        product_id="PROD-A",
        plant_id="PLANT-01",
        planning_weeks=4,
    )

    report = result["manufacturing_intelligence_report"]
    health = report["system_health"]
    pipeline = report["pipeline_summary"]
    alerts = report["cross_domain_alerts"]
    actions = report["priority_actions"]

    print(f"\n{'═'*70}")
    print(f"  MANUFACTURING INTELLIGENCE REPORT")
    print(f"{'═'*70}")
    print(f"\n  SYSTEM HEALTH: {health['overall_score']}/100  [{health['overall_status']}]")
    print(f"  {'─'*50}")
    for domain, d in health["domain_scores"].items():
        bar = "█" * (int(d["score"]) // 10) + "░" * (10 - int(d["score"]) // 10)
        print(f"  {domain:<20} [{bar}] {d['score']:>3}/100  {d['status']}")

    print(f"\n  PIPELINE SUMMARY:")
    print(f"  {'─'*50}")
    print(f"  Demand target (weekly)    : {pipeline['demand_target_weekly']} units")
    print(f"  Capacity ceiling (weekly) : {pipeline['capacity_ceiling_weekly']} units")
    print(f"  Planned production        : {pipeline['planned_production_weekly']} units")
    print(f"  Inventory days of supply  : {pipeline['inventory_days_of_supply']} days")
    print(f"  Total procurement value   : ${pipeline['total_procurement_value']:,.2f}")
    print(f"  Supply resilience score   : {pipeline['supply_resilience_score']}/100")

    if alerts:
        print(f"\n  CROSS-DOMAIN ALERTS ({len(alerts)}):")
        print(f"  {'─'*50}")
        for a in alerts:
            print(f"  [{a['severity']}] {', '.join(a['domains'])}")
            print(f"     {a['alert']}")

    if actions:
        print(f"\n  PRIORITY ACTIONS:")
        print(f"  {'─'*50}")
        for a in actions:
            print(f"  [{a['priority']}] {a['urgency']} | Owner: {a['owner']}")
            print(f"     {a['action']}")
            print(f"     Impact: {a['impact']}")

    if report.get("human_escalation_required"):
        print(f"\n  *** HUMAN ESCALATION REQUIRED ***")
        print(f"  Critical issues require executive authorization.")

    print(f"\n  Now running Orchestrator LLM for cross-domain analysis...")
    print(f"{'='*70}\n")

    orchestrator2 = OrchestratorAgent()
    llm_prompt = ORCHESTRATOR_EXAMPLES["full_pipeline_weekly_brief"]
    llm_response = orchestrator2.run(llm_prompt)
    print(f"\n{'═'*70}\nORCHESTRATOR LLM RESPONSE:\n{'═'*70}")
    print(llm_response)

    print(f"\n{'#'*70}")
    print(f"#  FULL PIPELINE DEMO COMPLETE")
    print(f"#  System health score: {health['overall_score']}/100  [{health['overall_status']}]")
    print(f"#  Cross-domain alerts: {len(alerts)}")
    print(f"#  Priority actions: {len(actions)}")
    print(f"{'#'*70}")


def run_trace_single_agent_demo():
    """
    Scenario 16 — Data Flow Trace: Demand Agent.
    Runs the Demand Agent on a full-analysis question, then renders a complete
    data flow audit showing:
      - Each iteration: LLM reasoning → tool called → tool output
      - Value Reference Audit: which specific values from tool outputs the LLM
        actually cited in its final answer
    Saves the verbose report to output_trace_demand.txt.
    """
    print(f"\n{'#'*70}")
    print(f"#  DATA FLOW TRACE: DEMAND FORECASTING AGENT")
    print(f"#  Verifying the agent reasons over real tool data")
    print(f"{'#'*70}\n")

    agent = DemandForecastingAgent()
    prompt = DEMAND_EXAMPLES["full_analysis"]

    print(f"  Question sent to agent:")
    print(f"  \"{prompt[:120]}...\"" if len(prompt) > 120 else f"  \"{prompt}\"")
    print()

    agent.run(prompt)

    print(f"\n{'═'*70}")
    print(f"  GENERATING DATA FLOW AUDIT...")
    print(f"{'═'*70}\n")

    report = agent.get_trace_report(verbose=False)
    print(report)

    output_path = "output_trace_demand.txt"
    agent.save_trace(output_path)

    print(f"\n{'#'*70}")
    print(f"#  TRACE COMPLETE")
    print(f"#  Full verbose trace saved to: {output_path}")
    print(f"{'#'*70}")


def run_trace_full_pipeline_demo():
    """
    Scenario 17 — Data Flow Trace: Full Pipeline.
    Runs the Orchestrator LLM (full 5-agent pipeline), then renders the
    complete data flow audit for the orchestrator's ReAct loop:
      - Each iteration: which agent-tool was called → what it returned
      - Value Reference Audit: which values from all 5 agent outputs
        the Orchestrator LLM cited in its final Manufacturing Intelligence Report
    Saves the verbose report to output_trace_pipeline.txt.
    """
    print(f"\n{'#'*70}")
    print(f"#  DATA FLOW TRACE: FULL 6-AGENT PIPELINE")
    print(f"#  Verifying the Orchestrator reasons over all 5 specialist agent outputs")
    print(f"{'#'*70}\n")

    orchestrator = OrchestratorAgent()
    prompt = ORCHESTRATOR_EXAMPLES["full_pipeline_weekly_brief"]

    print(f"  Question sent to Orchestrator:")
    print(f"  \"{prompt[:120]}...\"" if len(prompt) > 120 else f"  \"{prompt}\"")
    print()

    orchestrator.run(prompt)

    print(f"\n{'═'*70}")
    print(f"  GENERATING DATA FLOW AUDIT...")
    print(f"{'═'*70}\n")

    report = orchestrator.get_trace_report(verbose=False)
    print(report)

    output_path = "output_trace_pipeline.txt"
    orchestrator.save_trace(output_path)

    print(f"\n{'#'*70}")
    print(f"#  TRACE COMPLETE")
    print(f"#  Full verbose trace saved to: {output_path}")
    print(f"{'#'*70}")


def run_scenario_validation_demo(scenario_key: str):
    """
    Scenarios 18 & 19 — Controlled Injection + Validation.

    Injects a pre-defined dataset into the Demand Agent (overriding the normal
    simulated tools), runs the agent, then compares its final answer against
    the known expected conclusions.

    Outputs:
      1. Full agent run (you can watch every tool call + LLM reasoning)
      2. Data Flow Audit  (which tool values the LLM actually cited)
      3. Scenario Validation Report (PASS/FAIL for each expected conclusion)
      4. Verbose trace saved to output_validation_<scenario_key>.txt
    """
    from tools.scenario import SCENARIOS
    from tools.validator import ScenarioValidator

    scenario = SCENARIOS[scenario_key]

    print(f"\n{'#'*70}")
    print(f"#  SCENARIO VALIDATION: {scenario['name']}")
    print(f"#  Injecting controlled test data → verifying agent conclusions")
    print(f"{'#'*70}\n")

    print(f"  SCENARIO DESCRIPTION:")
    print(f"  {scenario['description']}\n")

    print(f"  INJECTED VALUES (what the agent will receive instead of real simulation):")
    for item in scenario["injected_values_summary"]:
        print(f"  ✦ {item}")
    print()

    # Build agent and inject the controlled data
    agent = DemandForecastingAgent()
    agent.set_tool_overrides(scenario["tool_overrides"])

    prompt = (
        "Run a complete demand analysis. "
        "Check for anomalies, assess inventory status, identify the demand trend, "
        "run a Monte Carlo simulation for the balanced strategy, "
        "and give me your full assessment with specific numbers and recommended actions."
    )

    print(f"  Question sent to agent:")
    print(f"  \"{prompt}\"\n")
    print(f"{'='*70}")
    print(f"  AGENT RUNNING WITH INJECTED DATA...")
    print(f"  (Watch: every *** SCENARIO OVERRIDE *** line confirms injected data was used)")
    print(f"{'='*70}\n")

    final_answer = agent.run(prompt)

    # ── Data Flow Audit ──
    print(f"\n{'='*70}")
    print(f"  DATA FLOW AUDIT")
    print(f"{'='*70}\n")
    trace_report = agent.get_trace_report(verbose=False)
    print(trace_report)

    # ── Validation Report ──
    print(f"\n{'='*70}")
    print(f"  SCENARIO VALIDATION REPORT")
    print(f"{'='*70}\n")
    validator = ScenarioValidator(scenario, final_answer)
    results = validator.validate()
    validation_report = validator.render_report(results)
    print(validation_report)

    # ── Save verbose output ──
    output_path = f"output_validation_{scenario_key}.txt"
    agent.save_trace(output_path)

    passed = sum(1 for r in results if r["passed"])
    required_checks = [r for r in results if r["required"]]
    required_passed = sum(1 for r in required_checks if r["passed"])

    print(f"\n{'#'*70}")
    print(f"#  VALIDATION COMPLETE")
    print(f"#  Total   : {passed}/{len(results)} checks passed")
    print(f"#  Required: {required_passed}/{len(required_checks)} required checks passed")
    print(f"#  Full verbose trace saved to: {output_path}")
    print(f"{'#'*70}")


def run_demo(scenario: int = 1):
    scenarios = {
        # Phase 1: Demand Agent
        1: {"name": "Full Demand Analysis", "agent": "demand",
            "prompt": DEMAND_EXAMPLES["full_analysis"],
            "description": "Complete demand analysis with forecasting, anomaly detection, strategy recommendation"},
        2: {"name": "Anomaly Investigation", "agent": "demand",
            "prompt": DEMAND_EXAMPLES["anomaly_investigation"],
            "description": "Investigating a demand spike — agent diagnoses root cause and recommends action"},
        3: {"name": "Strategy Recommendation", "agent": "demand",
            "prompt": DEMAND_EXAMPLES["strategy_recommendation"],
            "description": "Deciding between conservative/balanced/aggressive production strategies"},
        4: {"name": "Rush Order (Orchestrator Request)", "agent": "demand",
            "prompt": ORCHESTRATOR_TO_DEMAND["urgent_request"],
            "description": "Orchestrator sends an urgent multi-crisis request to the Demand Agent"},
        # Phase 2: Inventory Agent
        5: {"name": "Full Inventory Analysis", "agent": "inventory",
            "prompt": INVENTORY_EXAMPLES["full_inventory_analysis"],
            "description": "Complete inventory analysis with stockout risk and replenishment plan"},
        6: {"name": "Safety Stock Optimization", "agent": "inventory",
            "prompt": INVENTORY_EXAMPLES["safety_stock_optimization"],
            "description": "Evaluate whether current safety stock is too high or too low"},
        # Cross-agent: Demand -> Inventory
        7: {"name": "Cross-Agent: Demand -> Inventory", "agent": "cross_demand_inventory",
            "prompt": None,
            "description": "Demand Agent forecasts, Inventory Agent creates replenishment plan"},
        # Phase 3: Machine Health Agent
        8: {"name": "Full Machine Health Assessment", "agent": "machine",
            "prompt": MACHINE_HEALTH_EXAMPLES["full_fleet_health_check"],
            "description": "Complete fleet health check with failure risk and maintenance schedule"},
        9: {"name": "Failure Risk Deep-Dive (MCH-002)", "agent": "machine",
            "prompt": MACHINE_HEALTH_EXAMPLES["failure_risk_deep_dive"],
            "description": "Sensor analysis and failure probability for the CNC Machining Center"},
        # Cross-agent: Machine Health -> Production
        10: {"name": "Cross-Agent: Machine Health -> Production Planning", "agent": "cross_machine_production",
             "prompt": None,
             "description": "Machine Health sets capacity ceiling, Production Agent builds MPS + material requirements"},
        # Phase 5: Supplier & Procurement Agent
        11: {"name": "Full Procurement Plan", "agent": "supplier",
             "prompt": SUPPLIER_EXAMPLES["full_procurement_plan"],
             "description": "Complete procurement plan: supplier evaluation, PO generation, risk assessment"},
        12: {"name": "Supply Chain Risk Audit", "agent": "supplier",
             "prompt": SUPPLIER_EXAMPLES["supply_chain_risk_audit"],
             "description": "Full supply chain risk audit: single-source exposure, contract expiry, performance trends"},
        # Cross-agent: Production -> Supplier
        13: {"name": "Cross-Agent: Production Planning -> Supplier", "agent": "cross_production_supplier",
             "prompt": None,
             "description": "Production Agent generates material requirements, Supplier Agent procures and assesses risk"},
        # Phase 6: Orchestrator Agent
        14: {"name": "Full Pipeline (Orchestrator)", "agent": "full_pipeline",
             "prompt": None,
             "description": "Orchestrator runs all 5 agents, synthesizes a Manufacturing Intelligence Report"},
        15: {"name": "Emergency Re-Plan (Orchestrator)", "agent": "orchestrator",
             "prompt": ORCHESTRATOR_EXAMPLES["emergency_replan"],
             "description": "MCH-002 fails unexpectedly — Orchestrator re-plans the full pipeline in real time"},
        # Data Flow Tracer
        16: {"name": "Data Flow Trace: Demand Agent", "agent": "trace_single",
             "prompt": None,
             "description": "Runs Demand Agent and audits exactly which tool data values the LLM cited"},
        17: {"name": "Data Flow Trace: Full Pipeline", "agent": "trace_pipeline",
             "prompt": None,
             "description": "Runs full 6-agent pipeline and audits the Orchestrator's data reasoning"},
        # Scenario Validation (Option 3: controlled injection + pass/fail verdict)
        18: {"name": "Scenario Validation: CRITICAL STATE", "agent": "validate_crisis",
             "prompt": None,
             "description": "Injects crisis data (stockout in 2 days, +72% spike, 91.5% stockout risk) → validates agent conclusions"},
        19: {"name": "Scenario Validation: HEALTHY STATE", "agent": "validate_healthy",
             "prompt": None,
             "description": "Injects healthy data (57 days supply, no anomalies, 2.1% stockout risk) → validates agent conclusions"},
    }

    if scenario not in scenarios:
        print(f"  Invalid scenario. Choose 1-{len(scenarios)}")
        return

    s = scenarios[scenario]
    print(f"\n{'═'*70}\n  AMIS DEMO - Scenario {scenario}: {s['name']}\n  {s['description']}\n{'═'*70}\n")

    agent_type = s["agent"]

    if agent_type == "validate_crisis":
        run_scenario_validation_demo("crisis")
    elif agent_type == "validate_healthy":
        run_scenario_validation_demo("healthy")
    elif agent_type == "trace_single":
        run_trace_single_agent_demo()
    elif agent_type == "trace_pipeline":
        run_trace_full_pipeline_demo()
    elif agent_type == "cross_demand_inventory":
        run_cross_agent_demand_inventory()
    elif agent_type == "cross_machine_production":
        run_cross_agent_machine_production()
    elif agent_type == "cross_production_supplier":
        run_cross_agent_production_supplier()
    elif agent_type == "full_pipeline":
        run_full_pipeline_demo()
    elif agent_type == "orchestrator":
        run_orchestrator_demo(s)
    elif agent_type == "machine":
        run_machine_health_demo(s)
    elif agent_type == "inventory":
        run_inventory_demo(s)
    elif agent_type == "production":
        run_production_demo(s)
    elif agent_type == "supplier":
        run_supplier_demo(s)
    else:
        agent = run_demand_demo(s)
        if scenario == 4:
            print(f"\n\n{'═'*70}\nFOLLOW-UP QUESTION:\n{'═'*70}")
            followup = (
                "Given your assessment, what's the maximum we can safely commit to? "
                "The client is willing to accept a partial delivery. "
                "What's our best offer that balances client satisfaction with our constraints?"
            )
            print(followup)
            print(f"{'─'*70}")
            response2 = agent.run(followup)
            print(f"\n{'═'*70}\nDEMAND AGENT FOLLOW-UP:\n{'═'*70}")
            print(response2)
            print(f"{'═'*70}")


def main():
    scenario = 1
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        scenario = int(sys.argv[1])

    print("\n  Available Demo Scenarios:")
    print("  ── Phase 1: Demand Forecasting ──")
    print("   1 = Full Demand Analysis")
    print("   2 = Anomaly Investigation")
    print("   3 = Strategy Recommendation")
    print("   4 = Rush Order (Orchestrator -> Agent)")
    print("  ── Phase 2: Inventory Management ──")
    print("   5 = Full Inventory Analysis")
    print("   6 = Safety Stock Optimization")
    print("  ── Cross-Agent ──")
    print("   7 = Demand -> Inventory (cross-agent flow)")
    print("  ── Phase 3: Machine Health ──")
    print("   8 = Full Machine Health Assessment")
    print("   9 = Failure Risk Deep-Dive (MCH-002)")
    print("  ── Cross-Agent ──")
    print("  10 = Machine Health -> Production Planning (cross-agent flow)")
    print("  ── Phase 5: Supplier & Procurement ──")
    print("  11 = Full Procurement Plan")
    print("  12 = Supply Chain Risk Audit")
    print("  ── Cross-Agent ──")
    print("  13 = Production Planning -> Supplier (cross-agent flow)")
    print("  ── Phase 6: Orchestrator ──")
    print("  14 = Full Pipeline (all 5 agents + synthesis)")
    print("  15 = Emergency Re-Plan (MCH-002 failure)")
    print("  ── Data Flow Tracer ──")
    print("  16 = Data Flow Trace: Demand Agent")
    print("  17 = Data Flow Trace: Full Pipeline")
    print("  ── Scenario Validation ──")
    print("  18 = Validation: CRITICAL STATE (stockout in 2 days, +72% spike)")
    print("  19 = Validation: HEALTHY STATE  (57 days supply, no anomalies)")
    print(f"\n   Running scenario {scenario}...\n")

    run_demo(scenario)


if __name__ == "__main__":
    main()
