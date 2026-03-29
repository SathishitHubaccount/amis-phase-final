"""
AMIS - Autonomous Manufacturing Intelligence System
Interactive CLI for testing agents.
Supports: Demand Forecasting Agent (Phase 1) + Inventory Management Agent (Phase 2)
        + Machine Health Agent (Phase 3) + Production Planning Agent (Phase 4)
        + Supplier & Procurement Agent (Phase 5) + Orchestrator Agent (Phase 6)
"""
import sys

# Ensure Unicode characters display correctly on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from agents.demand_agent import DemandForecastingAgent
from agents.inventory_agent import InventoryManagementAgent
from agents.machine_health_agent import MachineHealthAgent
from agents.production_agent import ProductionPlanningAgent
from agents.supplier_agent import SupplierProcurementAgent
from agents.orchestrator_agent import OrchestratorAgent
from prompts.demand_prompts import EXAMPLE_PROMPTS as DEMAND_EXAMPLES
from prompts.inventory_prompts import EXAMPLE_PROMPTS as INVENTORY_EXAMPLES
from prompts.machine_health_prompts import EXAMPLE_PROMPTS as MACHINE_HEALTH_EXAMPLES
from prompts.production_prompts import EXAMPLE_PROMPTS as PRODUCTION_EXAMPLES
from prompts.supplier_prompts import EXAMPLE_PROMPTS as SUPPLIER_EXAMPLES
from prompts.orchestrator_prompts import EXAMPLE_PROMPTS as ORCHESTRATOR_EXAMPLES


AGENTS = {
    "demand": {
        "class": DemandForecastingAgent,
        "examples": DEMAND_EXAMPLES,
        "icon": "📈",
        "label": "DEMAND FORECASTING AGENT",
    },
    "inventory": {
        "class": InventoryManagementAgent,
        "examples": INVENTORY_EXAMPLES,
        "icon": "📦",
        "label": "INVENTORY MANAGEMENT AGENT",
    },
    "machine": {
        "class": MachineHealthAgent,
        "examples": MACHINE_HEALTH_EXAMPLES,
        "icon": "🔧",
        "label": "MACHINE HEALTH AGENT",
    },
    "production": {
        "class": ProductionPlanningAgent,
        "examples": PRODUCTION_EXAMPLES,
        "icon": "🏭",
        "label": "PRODUCTION PLANNING AGENT",
    },
    "supplier": {
        "class": SupplierProcurementAgent,
        "examples": SUPPLIER_EXAMPLES,
        "icon": "🚚",
        "label": "SUPPLIER & PROCUREMENT AGENT",
    },
    "orchestrator": {
        "class": OrchestratorAgent,
        "examples": ORCHESTRATOR_EXAMPLES,
        "icon": "🎯",
        "label": "ORCHESTRATOR AGENT",
    },
}

AGENT_KEYS = list(AGENTS.keys())


def print_banner():
    print("""
╔═════════════════════════════════════════════════════════════════╗
║           AMIS - Autonomous Manufacturing Intelligence          ║
║        Multi-Agent System (Phase 1 + 2 + 3 + 4 + 5 + 6)        ║
╠═════════════════════════════════════════════════════════════════╣
║  Agents Available:                                              ║
║    [1] Demand Forecasting Agent                                 ║
║        - Multi-scenario forecasting, anomaly detection          ║
║        - Monte Carlo simulation, strategy recommendation        ║
║                                                                 ║
║    [2] Inventory Management Agent                               ║
║        - Reorder point calculation, safety stock optimization   ║
║        - Stockout risk simulation, replenishment planning       ║
║                                                                 ║
║    [3] Machine Health Agent                                     ║
║        - Fleet health monitoring, sensor anomaly detection      ║
║        - Failure prediction, OEE analysis, maintenance planning ║
║                                                                 ║
║    [4] Production Planning Agent                                ║
║        - Master Production Schedule (MPS), bottleneck analysis  ║
║        - Capacity gap, overtime/contract decisions, BOM/MRP     ║
║                                                                 ║
║    [5] Supplier & Procurement Agent                             ║
║        - Supplier evaluation, PO generation, risk assessment    ║
║        - Delivery simulation, dual-source optimization          ║
║                                                                 ║
║    [6] Orchestrator Agent                                       ║
║        - Runs full 5-agent pipeline, cross-domain synthesis     ║
║        - System health score, priority actions, escalation      ║
╠═════════════════════════════════════════════════════════════════╣
║  Commands:                                                      ║
║    Type any question in natural language                        ║
║    'examples'  - Show example prompts for current agent         ║
║    'demo <n>'  - Run example prompt n                           ║
║    'switch'    - Cycle to the next agent                        ║
║    'agent'     - Show which agent is active                     ║
║    'reset'     - Clear conversation memory                      ║
║    'quit'      - Exit                                           ║
╚═════════════════════════════════════════════════════════════════╝
    """)


def select_agent():
    """Let user choose which agent to activate."""
    print("\n  Select an agent:")
    print("    [1] Demand Forecasting Agent")
    print("    [2] Inventory Management Agent")
    print("    [3] Machine Health Agent")
    print("    [4] Production Planning Agent")
    print("    [5] Supplier & Procurement Agent")
    print("    [6] Orchestrator Agent  ← runs all 5 agents")
    choice = input("\n  > ").strip()
    if choice == "2":
        return "inventory"
    if choice == "3":
        return "machine"
    if choice == "4":
        return "production"
    if choice == "5":
        return "supplier"
    if choice == "6":
        return "orchestrator"
    return "demand"


def show_examples(examples):
    print("\n  Example Prompts You Can Try:\n")
    for i, (key, prompt) in enumerate(examples.items(), 1):
        print(f"  [{i}] ({key})")
        print(f"      \"{prompt}\"\n")
    print("  Tip: Type 'demo 1' to run example 1, or type your own question.\n")


def main():
    print_banner()

    agent_key = select_agent()
    agent_config = AGENTS[agent_key]

    try:
        agent = agent_config["class"]()
    except Exception as e:
        print(f"\n  Failed to initialize agent: {e}")
        print("  Make sure ANTHROPIC_API_KEY is set as environment variable.")
        sys.exit(1)

    examples = agent_config["examples"]
    icon = agent_config["icon"]
    label = agent_config["label"]

    while True:
        try:
            user_input = input(f"\n{icon} You > ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("\n  Shutting down AMIS. Goodbye!")
                break

            if user_input.lower() == "agent":
                print(f"\n  Active agent: {icon} {label}")
                continue

            if user_input.lower() == "switch":
                # Cycle through agents in order
                current_idx = AGENT_KEYS.index(agent_key)
                agent_key = AGENT_KEYS[(current_idx + 1) % len(AGENT_KEYS)]
                agent_config = AGENTS[agent_key]
                try:
                    agent = agent_config["class"]()
                except Exception as e:
                    print(f"\n  Failed to initialize agent: {e}")
                    continue
                examples = agent_config["examples"]
                icon = agent_config["icon"]
                label = agent_config["label"]
                print(f"\n  Switched to: {icon} {label}")
                continue

            if user_input.lower() == "examples":
                show_examples(examples)
                continue

            if user_input.lower() == "reset":
                agent.reset_memory()
                continue

            if user_input.lower().startswith("demo"):
                example_list = list(examples.values())
                parts = user_input.split()
                if len(parts) == 2 and parts[1].isdigit():
                    idx = int(parts[1]) - 1
                    if 0 <= idx < len(example_list):
                        user_input = example_list[idx]
                        print(f"\n  Running: \"{user_input}\"\n")
                    else:
                        print(f"  Invalid demo number. Use 1-{len(example_list)}")
                        continue
                else:
                    print("  Usage: demo <number> (e.g., 'demo 1')")
                    continue

            # Run the agent
            response = agent.run(user_input)

            print(f"\n{'─'*70}")
            print(f"{icon} {label}:")
            print(f"{'─'*70}")
            print(response)
            print(f"{'─'*70}")

        except KeyboardInterrupt:
            print("\n\n  Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n  Error: {e}")
            print("  Try again or type 'reset' to clear memory.")


if __name__ == "__main__":
    main()
