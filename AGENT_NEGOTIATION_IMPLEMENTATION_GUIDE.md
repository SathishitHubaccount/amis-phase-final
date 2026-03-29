# 🤝 Agent Negotiation System - Complete Implementation Guide

## What is Agent Negotiation?

**Agent Negotiation** is when multiple AI agents with different goals/perspectives discuss a problem and converge on the best solution through structured debate.

Think of it like a meeting where:
- **Demand Manager** wants to accept all customer orders
- **Production Manager** is concerned about capacity limits
- **Finance Manager** wants to minimize costs
- **They debate** and find the optimal compromise

But instead of humans, it's AI agents - and it happens in seconds, not hours.

---

## Why It's Impressive for Hackathons

### Traditional Multi-Agent (Boring):
```
Agent 1 runs → produces output
Agent 2 runs → uses Agent 1's output
Agent 3 runs → uses Agent 2's output
```
This is just a **sequential pipeline**. Not very "agentic."

### Agent Negotiation (Exciting! 🔥):
```
Agent 1: "I propose solution A"
Agent 2: "I disagree because X, I propose solution B"
Agent 3: "Both have merit, what about solution C?"
Agent 1: "Ok, C works if we add constraint Y"
→ Consensus reached: Solution C with constraint Y
```

This is **true multi-agent collaboration** - agents influence each other, debate, and converge.

---

## How Agent Negotiation Works (Step-by-Step)

### Core Algorithm: 3-Round Debate

```
ROUND 1: PROPOSALS
Each agent independently proposes a solution

ROUND 2: CRITIQUES
Each agent reviews other agents' proposals and critiques them

ROUND 3: CONSENSUS
Agents synthesize all proposals + critiques into final decision
```

Let me show you with a real example:

---

## Example: Demand Spike Crisis

### Scenario Setup:
```
Situation:
- Customer wants 2,000 units in 3 days
- Normal production capacity: 1,500 units in 3 days
- Current inventory buffer: 300 units
- Overtime cost: $3,000 per 100 units
- Customer lifetime value: $500,000
- Competitor is also bidding for this contract

Question: Should we accept the order? If yes, how?
```

### ROUND 1: Each Agent Proposes Solution

#### Demand Agent Thinks:
```
Prompt to Demand Agent:
"You are a demand forecasting agent focused on customer relationships.

Scenario: Customer wants 2,000 units in 3 days.
- Production capacity: 1,500 units
- Inventory buffer: 300 units
- Customer lifetime value: $500K
- Competitor is bidding

What do you propose? Think step by step."

Demand Agent Response:
{
  "proposal": "Accept the order",
  "reasoning": [
    "Customer is high-value ($500K lifetime value)",
    "Competitor bidding means we might lose them forever if we reject",
    "We can fulfill 1,800 units (1,500 production + 300 buffer)",
    "Only need 200 more units somehow"
  ],
  "concerns": [
    "Not sure where to get the extra 200 units"
  ],
  "confidence": 0.8
}
```

#### Production Agent Thinks:
```
Prompt to Production Agent:
"You are a production planning agent focused on factory capacity and costs.

Scenario: Customer wants 2,000 units in 3 days.
- Production capacity: 1,500 units (max)
- Overtime can add 200 units for $6,000
- Using overtime strains workers

What do you propose? Think step by step."

Production Agent Response:
{
  "proposal": "Reject the order OR negotiate 5-day delivery",
  "reasoning": [
    "3-day timeline is impossible without overtime",
    "Overtime costs $6,000 for just 200 units ($30/unit premium)",
    "Workers are already fatigued from last week's overtime",
    "5-day timeline would allow normal production of 2,500 units"
  ],
  "alternative": "If customer insists on 3 days, accept but with overtime",
  "concerns": [
    "Worker burnout risk",
    "High overtime costs eat into profit"
  ],
  "confidence": 0.6
}
```

#### Inventory Agent Thinks:
```
Prompt to Inventory Agent:
"You are an inventory optimization agent focused on stock levels and costs.

Scenario: Customer wants 2,000 units in 3 days.
- Current buffer: 300 units
- Safety stock minimum: 200 units
- Using buffer depletes our cushion

What do you propose? Think step by step."

Inventory Agent Response:
{
  "proposal": "Accept order using partial buffer",
  "reasoning": [
    "We have 300 units buffer (above 200 minimum)",
    "Can safely use 100 units from buffer (keeps us at 200 minimum)",
    "Production 1,500 + Buffer 100 = 1,600 units",
    "Still need 400 more units"
  ],
  "alternative_sources": [
    "Overtime production: 200 units ($6,000)",
    "Emergency supplier: 200 units ($8,000)",
    "Both: gets us to 2,000 units"
  ],
  "recommendation": "Use 100 buffer + 1,500 production + 200 overtime + 200 emergency = 2,000 units total",
  "total_cost": "$14,000 (overtime + emergency supplier)",
  "concerns": [
    "High cost erodes profit margin"
  ],
  "confidence": 0.7
}
```

#### Cost/Finance Agent Thinks:
```
Prompt to Cost Agent:
"You are a financial analysis agent focused on profitability.

Scenario: Customer wants 2,000 units in 3 days.
- Order value: $60,000 (2,000 units × $30/unit)
- Normal production cost: $20/unit
- Overtime cost: $30/unit premium
- Emergency supplier cost: $40/unit premium

Calculate the profitability of different options."

Cost Agent Response:
{
  "analysis": {
    "reject_order": {
      "revenue": 0,
      "cost": 0,
      "profit": 0,
      "risk": "Lose $500K lifetime value customer to competitor"
    },

    "accept_with_overtime_only": {
      "revenue": "$60,000",
      "cost": "$43,000 (1,800 normal + 200 overtime)",
      "profit": "$17,000",
      "margin": "28%",
      "risk": "Still 200 units short"
    },

    "accept_with_full_solution": {
      "revenue": "$60,000",
      "cost": "$54,000 (1,600 normal + 200 overtime + 200 emergency)",
      "profit": "$6,000",
      "margin": "10%",
      "risk": "Low margin but keeps customer"
    }
  },
  "proposal": "Accept order with full solution",
  "reasoning": [
    "$6,000 profit on this order",
    "Retain $500K lifetime value customer",
    "ROI: $6K immediate + $500K retention vs $54K cost = Positive",
    "Competitor doesn't win"
  ],
  "confidence": 0.9
}
```

**END OF ROUND 1**

We now have 4 different proposals:
- Demand: Accept (somehow get 200 units)
- Production: Reject or 5-day delivery
- Inventory: Accept using buffer + overtime + emergency
- Cost: Accept with full solution (shows positive ROI)

---

### ROUND 2: Agents Critique Each Other

Now each agent sees OTHER agents' proposals and provides critiques.

#### Demand Agent Critiques Production Agent:
```
Prompt:
"You are the Demand Agent. You proposed: Accept the order.

The Production Agent proposed: Reject OR negotiate 5-day delivery.

Their reasoning:
- 3 days impossible without overtime
- Overtime strains workers
- 5 days allows normal production

Critique this proposal from your perspective (customer relationships)."

Demand Agent Critique:
{
  "critique_of": "Production Agent's rejection proposal",
  "problems": [
    "Rejecting loses a $500K lifetime value customer",
    "Competitor will win if we reject",
    "Customer explicitly needs 3-day delivery (competitive bid deadline)",
    "Negotiating 5 days means we lose the contract"
  ],
  "points_of_agreement": [
    "Overtime does strain workers (valid concern)"
  ],
  "counter_proposal": "Accept with overtime, but offer workers bonus + recovery day",
  "updated_reasoning": "After seeing Cost Agent's analysis showing $6K profit + customer retention, accepting makes business sense even with overtime"
}
```

#### Production Agent Critiques Inventory Agent:
```
Prompt:
"You are the Production Agent. You proposed: Reject or 5-day delivery.

The Inventory Agent proposed: Use buffer + overtime + emergency supplier.

Their reasoning:
- Use 100 units from buffer (safe)
- 200 units overtime
- 200 units emergency supplier
- Total cost: $14,000

Critique this proposal from your perspective (production feasibility)."

Production Agent Critique:
{
  "critique_of": "Inventory Agent's hybrid solution",
  "positives": [
    "Keeps safety stock at minimum (responsible)",
    "Combines multiple sources (reduces risk)",
    "Actually achieves 2,000 units in 3 days"
  ],
  "problems": [
    "200 units overtime in 3 days is aggressive but doable",
    "Emergency supplier reliability unknown - do they have stock?",
    "Coordination complexity (3 sources)"
  ],
  "questions": [
    "Has emergency supplier confirmed 200 units availability?",
    "What's lead time for emergency supplier?"
  ],
  "updated_position": "If emergency supplier confirmed, this works. Otherwise need backup plan."
}
```

#### Inventory Agent Critiques Cost Agent:
```
Prompt:
"You are the Inventory Agent. You proposed: Buffer + overtime + emergency.

The Cost Agent analyzed profitability and says: Accept with full solution (10% margin).

Critique this from your perspective (inventory management)."

Inventory Agent Critique:
{
  "critique_of": "Cost Agent's financial analysis",
  "agreement": [
    "Math is correct ($6K profit)",
    "Long-term customer value justifies thin margin"
  ],
  "additional_considerations": [
    "After using buffer, we need to rebuild it",
    "Next week's production should prioritize buffer replenishment",
    "Emergency supplier might become regular supplier (relationship building)"
  ],
  "risk_assessment": "Low risk if we immediately order buffer replenishment",
  "updated_recommendation": "Accept order AND place replenishment order for next week"
}
```

#### Cost Agent Critiques Demand Agent:
```
Prompt:
"You are the Cost Agent. You calculated accepting yields $6K profit + customer retention.

The Demand Agent proposed: Accept the order (strong customer focus).

Critique this from financial perspective."

Cost Agent Critique:
{
  "critique_of": "Demand Agent's acceptance proposal",
  "validation": [
    "Customer retention value is real ($500K lifetime)",
    "Losing to competitor has long-term cost",
    "Demand Agent's instinct was financially correct"
  ],
  "refinement": [
    "Should negotiate a slight premium given tight timeline",
    "Customer might accept $32/unit instead of $30/unit for 3-day rush",
    "Extra $4,000 revenue (2,000 × $2) would increase margin to 17%"
  ],
  "final_recommendation": "Accept order, but attempt to negotiate 7% rush premium"
}
```

**END OF ROUND 2**

Agents have now:
- Seen each other's perspectives
- Identified agreement points
- Raised concerns
- Suggested refinements

---

### ROUND 3: Synthesize Consensus

Now the **Orchestrator** (or a dedicated Synthesis Agent) combines all proposals + critiques into final decision.

```
Prompt to Orchestrator:
"You are coordinating 4 agents who discussed whether to accept a 2,000 unit order in 3 days.

ROUND 1 PROPOSALS:
- Demand Agent: Accept (customer focus)
- Production Agent: Reject or 5-day (capacity focus)
- Inventory Agent: Accept with buffer+overtime+emergency (hybrid)
- Cost Agent: Accept (shows $6K profit + customer retention)

ROUND 2 CRITIQUES:
- Demand critiqued Production: Rejecting loses $500K customer
- Production critiqued Inventory: Hybrid works IF emergency supplier confirmed
- Inventory critiqued Cost: Need to rebuild buffer after
- Cost critiqued Demand: Should negotiate rush premium

Synthesize these into ONE final recommendation that:
1. Addresses all valid concerns
2. Maximizes value
3. Is executable

Think step by step."

Orchestrator Synthesis:
{
  "final_decision": "ACCEPT ORDER with conditions",

  "execution_plan": {
    "step_1": "Negotiate with customer",
    "details_1": "Propose $32/unit (7% rush premium) for 3-day delivery. If customer rejects, accept at $30/unit.",

    "step_2": "Confirm emergency supplier",
    "details_2": "Call emergency supplier NOW to confirm 200 units available for pickup today. If not available, use backup: split 200 units between two suppliers.",

    "step_3": "Production allocation",
    "details_3": [
      "1,500 units from normal production (3 days)",
      "100 units from inventory buffer",
      "200 units from overtime (offer workers $500 bonus + Friday off)",
      "200 units from confirmed emergency supplier"
    ],

    "step_4": "Buffer replenishment",
    "details_4": "Place order for 300 units next week to rebuild buffer to normal levels"
  },

  "financial_summary": {
    "best_case": "$10,000 profit (if rush premium accepted)",
    "base_case": "$6,000 profit (at normal price)",
    "long_term_value": "$500,000 customer retention",
    "roi": "Excellent"
  },

  "risks_and_mitigations": {
    "risk_1": "Emergency supplier doesn't have stock",
    "mitigation_1": "Backup: split between two suppliers, confirm before committing to customer",

    "risk_2": "Worker overtime fatigue",
    "mitigation_2": "Offer bonus + recovery day, make this exception not norm",

    "risk_3": "Inventory buffer depleted",
    "mitigation_3": "Immediate replenishment order placed"
  },

  "consensus_summary": "All agents converged on ACCEPT with Inventory Agent's hybrid approach. Cost Agent's rush premium suggestion adds value. Production Agent's concerns addressed by worker bonus. Inventory Agent's buffer replenishment ensures no future risk.",

  "agent_agreement": {
    "demand_agent": "Strongly agrees (customer retained)",
    "production_agent": "Agrees with worker bonus mitigation",
    "inventory_agent": "Agrees with replenishment plan",
    "cost_agent": "Strongly agrees (positive ROI)"
  },

  "confidence": 0.95,
  "recommendation": "Execute immediately"
}
```

**END OF ROUND 3**

Final decision reached with:
- ✅ All agents in agreement
- ✅ All concerns addressed
- ✅ Clear execution plan
- ✅ Risk mitigation strategies
- ✅ Financial justification

---

## Implementation Code

### File: `backend/agent_negotiation.py`

```python
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from config import get_settings
import json

class AgentNegotiator:
    """
    Orchestrates multi-agent negotiation using 3-round debate:
    Round 1: Proposals
    Round 2: Critiques
    Round 3: Consensus
    """

    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
        self.settings = get_settings()

    def negotiate(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main negotiation workflow

        Args:
            scenario: Problem description and constraints

        Returns:
            Final consensus decision with execution plan
        """
        print(f"\n🤝 Starting negotiation with {len(self.agents)} agents...")

        # ROUND 1: Get proposals from each agent
        print("\n📋 ROUND 1: Collecting proposals...")
        proposals = self._round_1_proposals(scenario)

        # ROUND 2: Agents critique each other's proposals
        print("\n💬 ROUND 2: Agent critiques...")
        critiques = self._round_2_critiques(scenario, proposals)

        # ROUND 3: Synthesize consensus
        print("\n🎯 ROUND 3: Building consensus...")
        consensus = self._round_3_consensus(scenario, proposals, critiques)

        return {
            "scenario": scenario,
            "round_1_proposals": proposals,
            "round_2_critiques": critiques,
            "round_3_consensus": consensus,
            "negotiation_complete": True
        }

    def _round_1_proposals(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Round 1: Each agent proposes solution independently"""
        proposals = {}

        for agent in self.agents:
            print(f"  → {agent.name} proposing...")

            prompt = self._build_proposal_prompt(agent, scenario)
            proposal = agent.run(prompt)

            proposals[agent.name] = {
                "agent": agent.name,
                "proposal": proposal,
                "timestamp": self._get_timestamp()
            }

        return proposals

    def _round_2_critiques(self,
                          scenario: Dict[str, Any],
                          proposals: Dict[str, Any]) -> Dict[str, Any]:
        """Round 2: Each agent critiques others' proposals"""
        critiques = {}

        for agent in self.agents:
            print(f"  → {agent.name} critiquing...")

            # Get other agents' proposals (exclude own)
            other_proposals = {
                name: prop for name, prop in proposals.items()
                if name != agent.name
            }

            prompt = self._build_critique_prompt(
                agent,
                scenario,
                proposals[agent.name],  # Own proposal
                other_proposals         # Others' proposals
            )

            critique = agent.run(prompt)

            critiques[agent.name] = {
                "agent": agent.name,
                "critique": critique,
                "timestamp": self._get_timestamp()
            }

        return critiques

    def _round_3_consensus(self,
                          scenario: Dict[str, Any],
                          proposals: Dict[str, Any],
                          critiques: Dict[str, Any]) -> Dict[str, Any]:
        """Round 3: Synthesize all inputs into consensus"""

        print(f"  → Orchestrator synthesizing...")

        # Use first agent as synthesizer (or create dedicated orchestrator)
        synthesizer = self.agents[0]

        prompt = self._build_consensus_prompt(scenario, proposals, critiques)
        consensus = synthesizer.run(prompt)

        return {
            "final_decision": consensus,
            "all_agents_reviewed": len(self.agents),
            "timestamp": self._get_timestamp()
        }

    def _build_proposal_prompt(self, agent: BaseAgent, scenario: Dict) -> str:
        """Build prompt for Round 1: Proposal"""

        return f"""
You are {agent.name}, an expert in {agent.domain}.

SCENARIO:
{json.dumps(scenario, indent=2)}

Your task: Propose a solution to this problem from YOUR domain perspective.

Think step-by-step:
1. What is the core problem?
2. What constraints matter most to your domain?
3. What solution do you recommend?
4. What concerns do you have?
5. How confident are you? (0-1)

Return your proposal in JSON format:
{{
  "proposal": "Your recommended action",
  "reasoning": ["reason 1", "reason 2", ...],
  "concerns": ["concern 1", "concern 2", ...],
  "confidence": 0.8,
  "key_constraints": ["constraint 1", ...]
}}
"""

    def _build_critique_prompt(self,
                               agent: BaseAgent,
                               scenario: Dict,
                               own_proposal: Dict,
                               other_proposals: Dict) -> str:
        """Build prompt for Round 2: Critique"""

        return f"""
You are {agent.name}, an expert in {agent.domain}.

SCENARIO:
{json.dumps(scenario, indent=2)}

YOUR PROPOSAL (Round 1):
{json.dumps(own_proposal, indent=2)}

OTHER AGENTS' PROPOSALS:
{json.dumps(other_proposals, indent=2)}

Your task: Critique the other agents' proposals from YOUR domain perspective.

For each other agent's proposal:
1. What do you agree with?
2. What concerns you?
3. What are they missing?
4. How would you refine their proposal?

After seeing others' perspectives, update your own position if needed.

Return your critique in JSON format:
{{
  "critiques": {{
    "agent_name": {{
      "agrees_with": ["point 1", "point 2"],
      "concerns": ["concern 1", "concern 2"],
      "suggestions": ["suggestion 1", ...]
    }}
  }},
  "updated_position": "Your revised recommendation after seeing others' proposals",
  "updated_confidence": 0.85
}}
"""

    def _build_consensus_prompt(self,
                                scenario: Dict,
                                proposals: Dict,
                                critiques: Dict) -> str:
        """Build prompt for Round 3: Consensus"""

        return f"""
You are the Orchestrator synthesizing a multi-agent negotiation.

SCENARIO:
{json.dumps(scenario, indent=2)}

ROUND 1 - PROPOSALS:
{json.dumps(proposals, indent=2)}

ROUND 2 - CRITIQUES:
{json.dumps(critiques, indent=2)}

Your task: Synthesize all inputs into ONE final recommendation that:
1. Addresses all valid concerns raised by agents
2. Maximizes overall value
3. Is executable and concrete
4. Has buy-in from all agents

Think step-by-step:
1. What do all agents agree on?
2. Where do agents disagree? Why?
3. How can disagreements be resolved?
4. What's the optimal synthesis?

Return consensus in JSON format:
{{
  "final_decision": "Clear, executable recommendation",
  "execution_plan": {{
    "step_1": "First action",
    "step_2": "Second action",
    ...
  }},
  "addresses_concerns": {{
    "agent_name": "How their concern was addressed"
  }},
  "agent_agreement": {{
    "agent_name": "agree/disagree and why"
  }},
  "confidence": 0.95,
  "risks_and_mitigations": {{
    "risk_1": "Risk description",
    "mitigation_1": "How we'll handle it"
  }}
}}
"""

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Example usage
def example_negotiation():
    """Example: Demand spike scenario"""

    from agents.demand_agent import DemandAgent
    from agents.production_planning_agent import ProductionPlanningAgent
    from agents.inventory_agent import InventoryAgent

    # Create agents
    agents = [
        DemandAgent(),
        ProductionPlanningAgent(),
        InventoryAgent()
    ]

    # Define scenario
    scenario = {
        "problem": "Customer wants 2,000 units in 3 days",
        "constraints": {
            "production_capacity": 1500,
            "current_inventory": 300,
            "safety_stock_minimum": 200,
            "overtime_cost_per_100_units": 3000,
            "customer_lifetime_value": 500000,
            "competitor_bidding": True
        },
        "question": "Should we accept this order? If yes, how do we fulfill it?"
    }

    # Run negotiation
    negotiator = AgentNegotiator(agents)
    result = negotiator.negotiate(scenario)

    print("\n" + "="*60)
    print("NEGOTIATION RESULT")
    print("="*60)
    print(json.dumps(result["round_3_consensus"], indent=2))

    return result


if __name__ == "__main__":
    example_negotiation()
```

---

## API Endpoint

### File: `backend/main.py` (add this endpoint)

```python
@app.post("/api/negotiation/run")
async def run_negotiation(scenario: dict):
    """
    Run multi-agent negotiation for a given scenario

    Example request:
    {
      "scenario_type": "demand_spike",
      "product_id": "PROD-A",
      "customer_order": 2000,
      "timeline_days": 3
    }
    """

    from agent_negotiation import AgentNegotiator
    from agents.demand_agent import DemandAgent
    from agents.inventory_agent import InventoryAgent
    from agents.production_planning_agent import ProductionPlanningAgent

    # Create specialized scenario based on type
    if scenario["scenario_type"] == "demand_spike":
        negotiation_scenario = {
            "problem": f"Customer wants {scenario['customer_order']} units in {scenario['timeline_days']} days",
            "constraints": {
                "production_capacity": 1500,  # Could fetch from DB
                "current_inventory": 300,
                "safety_stock_minimum": 200,
                "overtime_available": True,
                "customer_lifetime_value": 500000
            },
            "question": "Should we accept? How to fulfill?"
        }

    # Initialize agents
    agents = [
        DemandAgent(),
        InventoryAgent(),
        ProductionPlanningAgent()
    ]

    # Run negotiation
    negotiator = AgentNegotiator(agents)
    result = negotiator.negotiate(negotiation_scenario)

    return {
        "status": "completed",
        "negotiation_id": generate_id(),
        "result": result
    }
```

---

## Frontend UI

### File: `frontend/src/pages/Negotiation.jsx`

```jsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function NegotiationDemo() {
  const [negotiating, setNegotiating] = useState(false);
  const [result, setResult] = useState(null);
  const [currentRound, setCurrentRound] = useState(0);

  const runNegotiation = async () => {
    setNegotiating(true);
    setCurrentRound(1);

    // Simulate round-by-round progression for demo effect
    const scenario = {
      scenario_type: "demand_spike",
      product_id: "PROD-A",
      customer_order: 2000,
      timeline_days: 3
    };

    setTimeout(() => setCurrentRound(2), 2000);
    setTimeout(() => setCurrentRound(3), 4000);

    const response = await fetch('/api/negotiation/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scenario)
    });

    const data = await response.json();
    setResult(data.result);
    setNegotiating(false);
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Agent Negotiation Demo</h1>

      {/* Scenario Card */}
      <Card className="mb-6 border-blue-200 bg-blue-50">
        <CardHeader>
          <h2 className="text-xl font-bold">Crisis Scenario</h2>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="font-semibold">Customer Emergency Order:</p>
            <ul className="list-disc ml-6">
              <li>Quantity: 2,000 units</li>
              <li>Timeline: 3 days</li>
              <li>Normal capacity: 1,500 units/3 days</li>
              <li>Gap: 500 units SHORT</li>
              <li>Competitor is also bidding</li>
            </ul>
          </div>

          <Button
            onClick={runNegotiation}
            disabled={negotiating}
            className="mt-4"
          >
            {negotiating ? 'Negotiating...' : 'Start Agent Negotiation'}
          </Button>
        </CardContent>
      </Card>

      {/* Negotiation Progress */}
      {negotiating && (
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="space-y-4">
              {/* Round 1 */}
              <div className={currentRound >= 1 ? 'opacity-100' : 'opacity-50'}>
                <h3 className="font-bold">Round 1: Proposals</h3>
                {currentRound >= 1 && (
                  <div className="ml-4 mt-2 space-y-1 text-sm">
                    <p>🤖 Demand Agent: "Accept order - customer is high-value"</p>
                    <p>🤖 Production Agent: "Reject - cannot meet capacity"</p>
                    <p>🤖 Inventory Agent: "Use buffer + overtime"</p>
                  </div>
                )}
              </div>

              {/* Round 2 */}
              <div className={currentRound >= 2 ? 'opacity-100' : 'opacity-50'}>
                <h3 className="font-bold">Round 2: Critiques</h3>
                {currentRound >= 2 && (
                  <div className="ml-4 mt-2 space-y-1 text-sm">
                    <p>💬 Demand critiques Production: "Rejecting loses $500K customer"</p>
                    <p>💬 Production critiques Inventory: "Overtime costs $6K"</p>
                    <p>💬 Inventory shows math: "Buffer + overtime = feasible"</p>
                  </div>
                )}
              </div>

              {/* Round 3 */}
              <div className={currentRound >= 3 ? 'opacity-100' : 'opacity-50'}>
                <h3 className="font-bold">Round 3: Consensus</h3>
                {currentRound >= 3 && (
                  <div className="ml-4 mt-2 text-sm">
                    <p>🎯 Synthesizing final recommendation...</p>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Final Result */}
      {result && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <h2 className="text-xl font-bold">✅ Consensus Reached</h2>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold">Final Decision:</h3>
                <p className="mt-1">
                  {result.round_3_consensus.final_decision.final_decision}
                </p>
              </div>

              <div>
                <h3 className="font-semibold">Execution Plan:</h3>
                <ol className="list-decimal ml-6 mt-2">
                  {Object.entries(result.round_3_consensus.final_decision.execution_plan || {}).map(([key, value]) => (
                    <li key={key}>{value}</li>
                  ))}
                </ol>
              </div>

              <div>
                <h3 className="font-semibold">Agent Agreement:</h3>
                <div className="ml-4 mt-2 space-y-1">
                  {Object.entries(result.round_3_consensus.final_decision.agent_agreement || {}).map(([agent, status]) => (
                    <p key={agent}>
                      {status.includes('agree') ? '✅' : '⚠️'} {agent}: {status}
                    </p>
                  ))}
                </div>
              </div>

              <div className="bg-white p-3 rounded">
                <p className="text-sm">
                  <strong>Confidence:</strong> {(result.round_3_consensus.final_decision.confidence * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

---

## Why This Wins Hackathons

### 1. **Visually Impressive**
Judges can SEE agents debating in real-time:
```
Round 1: Proposals appear one by one
Round 2: Critiques flow between agents
Round 3: Consensus builds
```

### 2. **Theoretically Sound**
Based on research papers:
- "Improving Factuality through Multi-Agent Debate" (Du et al., 2023)
- "Debating with More Persuasive LLMs" (Khan et al., 2024)
- Multi-agent systems literature

### 3. **Practically Valuable**
Solves real problem: Complex decisions need multiple perspectives.

### 4. **Truly Agentic**
Not just sequential calls - agents actually influence each other.

---

## Quick Implementation Checklist

- [ ] Create `backend/agent_negotiation.py` (negotiation engine)
- [ ] Add `/api/negotiation/run` endpoint to `backend/main.py`
- [ ] Create `frontend/src/pages/Negotiation.jsx` (UI)
- [ ] Add "Negotiation Demo" to sidebar navigation
- [ ] Test with demand spike scenario
- [ ] Polish UI animations
- [ ] Practice demo presentation

**Time estimate: 6-8 hours**

---

You now have everything you need to implement agent negotiation! 🚀

Want me to help you code any specific part?
