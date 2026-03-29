# AMIS Phase 1: Demand Forecasting Agent

## Architecture
```
amis_phase1/
├── config.py              # Configuration & API keys
├── data/
│   └── sample_data.py     # Simulated manufacturing data
├── tools/
│   ├── __init__.py
│   ├── forecasting.py     # Demand forecasting tools
│   ├── simulation.py      # Monte Carlo simulation tools
│   └── anomaly.py         # Anomaly detection tools
├── agents/
│   ├── __init__.py
│   └── demand_agent.py    # The Demand Forecasting Agent
├── prompts/
│   ├── __init__.py
│   └── demand_prompts.py  # All prompts for the agent
├── main.py                # Entry point - interactive CLI
└── demo.py                # Pre-built demo scenarios
```

## Setup
```bash
pip install langchain langchain-anthropic langchain-core numpy --break-system-packages
export ANTHROPIC_API_KEY="your-key-here"
python main.py
```

## What This Agent Can Do
1. **Multi-Scenario Forecasting** - Generates Optimistic/Base/Pessimistic demand scenarios
2. **Monte Carlo Profit Simulation** - Simulates 1000 scenarios to calculate expected profit & risk
3. **Anomaly Detection** - Flags unusual demand patterns with root cause hypotheses
4. **Strategy Recommendation** - Recommends Aggressive/Conservative/Balanced with full reasoning
5. **Cross-Agent Alerts** - Generates alerts for other agents (production, inventory, etc.)
