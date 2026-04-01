"""
Agent Negotiation System  — FAST PATH
3-round structured debate:
  Round 1: Each agent pre-fetches its live domain data (no LLM), then ONE LLM call → proposal
  Round 2: ONE LLM call per agent → critique of other proposals
  Round 3: ONE LLM call → orchestrator consensus

Total LLM calls: 7  (vs ~80 with full ReAct loop)
Expected runtime: ~35 s  (vs ~10 min with agent.run())
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime
from langchain_core.messages import HumanMessage
import json
import time


# ── Agent display metadata ────────────────────────────────────────
_AGENT_META = {
    "DemandForecasting":   {"label": "Demand Forecasting Agent",  "color": "blue",    "initials": "DA"},
    "InventoryManagement": {"label": "Inventory Management Agent","color": "purple",  "initials": "IA"},
    "ProductionPlanning":  {"label": "Production Planning Agent", "color": "emerald", "initials": "PA"},
    "MachineHealth":       {"label": "Machine Health Agent",       "color": "amber",   "initials": "MH"},
    "SupplierProcurement": {"label": "Supplier Procurement Agent", "color": "rose",    "initials": "SP"},
    "Orchestrator":        {"label": "Orchestrator",               "color": "orange",  "initials": "OR"},
}

# Tools each agent's bridge method calls (for trace display)
_AGENT_BRIDGE_TOOLS = {
    "DemandForecasting":   ["get_demand_data_summary", "analyze_demand_trends",
                            "simulate_demand_scenarios", "detect_demand_anomalies"],
    "InventoryManagement": ["get_inventory_status", "calculate_reorder_point",
                            "optimize_safety_stock", "simulate_stockout_risk"],
    "ProductionPlanning":  ["get_production_context", "build_master_production_schedule",
                            "analyze_production_bottlenecks", "evaluate_capacity_gap"],
    "MachineHealth":       ["get_machine_fleet_status", "predict_failure_risk",
                            "calculate_oee", "assess_production_capacity_impact"],
    "SupplierProcurement": ["get_procurement_context", "evaluate_supplier_options",
                            "assess_supply_chain_risk", "simulate_delivery_risk"],
}


def _agent_meta(name: str) -> dict:
    for key, meta in _AGENT_META.items():
        if key.lower() in name.lower():
            return meta
    return {"label": name + " Agent", "color": "gray", "initials": name[:2].upper()}


class AgentNegotiator:
    """
    Fast multi-agent negotiation.
    Pre-fetches live domain data once per agent (programmatic, no LLM),
    then makes exactly ONE LLM call per agent per round.
    """

    def __init__(self, agents: List[Any]):
        self.agents = agents
        self._execution_trace: List[Dict] = []
        self._seq = 0
        # Domain data pre-fetched in Round 1; reused in subsequent rounds
        self._agent_data: Dict[str, dict] = {}

    # ── Public API ────────────────────────────────────────────────

    def negotiate(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        print(f"\n🤝 Starting negotiation with {len(self.agents)} agents (fast-path)...")
        self._execution_trace = []
        self._seq = 0
        self._agent_data = {}

        print("\n📋 ROUND 1: Proposals (data fetch + 1 LLM call each)...")
        proposals = self._round_1_proposals(scenario)

        print("\n💬 ROUND 2: Critiques (1 LLM call each)...")
        critiques = self._round_2_critiques(scenario, proposals)

        print("\n🎯 ROUND 3: Consensus (1 LLM call)...")
        consensus = self._round_3_consensus(scenario, proposals, critiques)

        return {
            "scenario": scenario,
            "round_1_proposals": proposals,
            "round_2_critiques": critiques,
            "round_3_consensus": consensus,
            "execution_trace": self._execution_trace,
            "negotiation_complete": True,
            "timestamp": self._ts(),
        }

    # ── Round 1 ───────────────────────────────────────────────────

    def _round_1_proposals(self, scenario: Dict) -> Dict[str, Any]:
        proposals = {}

        for agent in self.agents:
            name = agent.__class__.__name__.replace("Agent", "")
            meta = _agent_meta(name)
            print(f"  [R1] {meta['label']}: fetching domain data + proposing...")
            t0 = time.time()

            # Step 1 — programmatic data fetch (fast, no LLM)
            domain_data, tool_calls = self._prefetch(agent, name)
            self._agent_data[name] = domain_data   # cache for later rounds

            # Step 2 — single LLM call for proposal
            data_section = (
                f"\n\nYour live domain data (already fetched):\n{json.dumps(domain_data, indent=2)}"
                if domain_data else ""
            )
            prompt = self._proposal_prompt(name, scenario) + data_section
            response, dur_ms = self._llm_call(agent, prompt, t0)

            proposals[name] = {
                "agent":      name,
                "proposal":   response,
                "tool_calls": tool_calls,
                "duration_ms": dur_ms,
                "timestamp":  self._ts(),
            }

            self._seq += 1
            self._execution_trace.append({
                "seq":            self._seq,
                "round":          1,
                "round_label":    "Initial Proposals",
                "agent":          name,
                "agent_label":    meta["label"],
                "agent_color":    meta["color"],
                "agent_initials": meta["initials"],
                "action":         "propose",
                "addressing":     [],
                "tool_calls":     tool_calls,
                "duration_ms":    dur_ms,
                "message_preview": self._preview(response),
                "timestamp":      proposals[name]["timestamp"],
            })

        return proposals

    # ── Round 2 ───────────────────────────────────────────────────

    def _round_2_critiques(self, scenario: Dict, proposals: Dict) -> Dict[str, Any]:
        critiques = {}

        for agent in self.agents:
            name = agent.__class__.__name__.replace("Agent", "")
            meta = _agent_meta(name)
            others = {k: v for k, v in proposals.items() if k != name}
            print(f"  [R2] {meta['label']}: critiquing...")
            t0 = time.time()

            # Single LLM call — no data re-fetch needed
            prompt = self._critique_prompt(name, scenario, proposals.get(name, {}), others)
            response, dur_ms = self._llm_call(agent, prompt, t0)

            critiques[name] = {
                "agent":      name,
                "critique":   response,
                "tool_calls": [],   # no tools in critique round
                "duration_ms": dur_ms,
                "timestamp":  self._ts(),
            }

            self._seq += 1
            self._execution_trace.append({
                "seq":            self._seq,
                "round":          2,
                "round_label":    "Agent Critiques",
                "agent":          name,
                "agent_label":    meta["label"],
                "agent_color":    meta["color"],
                "agent_initials": meta["initials"],
                "action":         "critique",
                "addressing":     list(others.keys()),
                "tool_calls":     [],
                "duration_ms":    dur_ms,
                "message_preview": self._preview(response),
                "timestamp":      critiques[name]["timestamp"],
            })

        return critiques

    # ── Round 3 ───────────────────────────────────────────────────

    def _round_3_consensus(self, scenario: Dict, proposals: Dict, critiques: Dict) -> Dict[str, Any]:
        synthesizer = self.agents[0]
        print(f"  [R3] Orchestrator synthesising consensus...")
        t0 = time.time()

        prompt = self._consensus_prompt(scenario, proposals, critiques)
        response, dur_ms = self._llm_call(synthesizer, prompt, t0)

        self._seq += 1
        self._execution_trace.append({
            "seq":            self._seq,
            "round":          3,
            "round_label":    "Consensus",
            "agent":          "Orchestrator",
            "agent_label":    "Orchestrator",
            "agent_color":    "orange",
            "agent_initials": "OR",
            "action":         "synthesize",
            "addressing":     list(proposals.keys()),
            "tool_calls":     [],
            "duration_ms":    dur_ms,
            "message_preview": self._preview(response),
            "timestamp":      self._ts(),
        })

        return {
            "final_decision":   response,
            "tool_calls":       [],
            "duration_ms":      dur_ms,
            "agents_involved":  len(self.agents),
            "timestamp":        self._ts(),
        }

    # ── Helpers ───────────────────────────────────────────────────

    def _llm_call(self, agent, prompt: str, t0: float) -> Tuple[str, int]:
        """Single direct LLM call — no ReAct loop, no tool binding."""
        try:
            resp = agent.llm.invoke([
                agent.system_message,
                HumanMessage(content=prompt),
            ])
            content = resp.content
            if isinstance(content, list):
                text = " ".join(
                    b.get("text", "") for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            else:
                text = str(content)
        except Exception as e:
            text = f"(LLM call failed: {e})"
        dur_ms = round((time.time() - t0) * 1000)
        return text, dur_ms

    def _prefetch(self, agent, name: str) -> Tuple[dict, List[dict]]:
        """
        Call the agent's programmatic bridge method to get live domain data.
        No LLM involved — pure tool execution.
        Returns (data_dict, tool_calls_list).
        """
        tool_names = _AGENT_BRIDGE_TOOLS.get(name, [])
        tool_calls = [{"order": i + 1, "name": t} for i, t in enumerate(tool_names)]

        try:
            if name == "DemandForecasting" and hasattr(agent, "get_forecast_output"):
                data = agent.get_forecast_output(product_id="PROD-A")
            elif name == "InventoryManagement" and hasattr(agent, "get_inventory_output"):
                data = agent.get_inventory_output(product_id="PROD-A", planning_weeks=4)
            elif name == "ProductionPlanning" and hasattr(agent, "get_production_output"):
                data = agent.get_production_output(product_id="PROD-A", planning_weeks=4)
            elif name == "MachineHealth" and hasattr(agent, "get_capacity_output"):
                data = agent.get_capacity_output(plant_id="PLANT-01")
            elif name == "SupplierProcurement" and hasattr(agent, "get_procurement_output"):
                data = agent.get_procurement_output(planning_weeks=4)
            else:
                return {}, []
            return data, tool_calls
        except Exception as e:
            print(f"  ⚠ prefetch failed for {name}: {e}")
            return {}, tool_calls   # still show tool names even if data fetch failed

    def _preview(self, text: str, max_chars: int = 220) -> str:
        if isinstance(text, list):
            text = " ".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in text)
        text = str(text).strip()
        if len(text) <= max_chars:
            return text
        for sep in [". ", ".\n", "! ", "? "]:
            idx = text.find(sep, 80)
            if 80 < idx < max_chars:
                return text[:idx + 1].strip()
        return text[:max_chars].strip() + "…"

    def _ts(self) -> str:
        return datetime.now().isoformat()

    # ── Prompts ───────────────────────────────────────────────────

    def _proposal_prompt(self, name: str, scenario: Dict) -> str:
        domain_map = {
            "DemandForecasting":   "demand forecasting and customer relationships",
            "InventoryManagement": "inventory optimisation and stock management",
            "ProductionPlanning":  "production scheduling and capacity planning",
            "MachineHealth":       "equipment reliability and predictive maintenance",
            "SupplierProcurement": "supplier relationships and procurement",
        }
        domain = domain_map.get(name, "manufacturing operations")
        return f"""You are the {name} Agent, expert in {domain}.

SCENARIO:
{json.dumps(scenario, indent=2)}

Using your live domain data provided below, propose a solution from YOUR domain perspective.

Include:
- Recommended action with specific numbers
- Key reasoning backed by your data
- Risks and concerns
- Confidence level (0–100 %)

Be concise and data-driven. 3–5 sentences max."""

    def _critique_prompt(self, name: str, scenario: Dict,
                          own: Dict, others: Dict) -> str:
        return f"""You are the {name} Agent.

SCENARIO:
{json.dumps(scenario, indent=2)}

YOUR ROUND 1 PROPOSAL:
{self._preview(own.get('proposal', '—'), 400)}

OTHER AGENTS' PROPOSALS:
{json.dumps({k: self._preview(v.get('proposal',''), 300) for k, v in others.items()}, indent=2)}

Critique the other proposals from YOUR domain perspective:
1. What do you agree with?
2. What concerns you?
3. Your updated position (has anything changed?).

Be concise — 3–4 sentences max."""

    def _consensus_prompt(self, scenario: Dict, proposals: Dict,
                           critiques: Dict) -> str:
        return f"""You are the Orchestrator synthesising a multi-agent negotiation.

SCENARIO:
{json.dumps(scenario, indent=2)}

PROPOSALS:
{json.dumps({k: self._preview(v.get('proposal',''), 250) for k, v in proposals.items()}, indent=2)}

CRITIQUES:
{json.dumps({k: self._preview(v.get('critique',''), 250) for k, v in critiques.items()}, indent=2)}

Synthesise into ONE final recommendation:
- Final decision (accept / reject / modify + specific plan)
- How each agent's key concern is addressed
- Financial summary (cost vs revenue)
- Confidence level

Be decisive. 5–7 sentences."""
