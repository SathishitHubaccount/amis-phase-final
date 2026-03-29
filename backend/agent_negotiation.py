"""
Agent Negotiation System
Orchestrates multi-agent debate with 3-round structure:
- Round 1: Each agent proposes solution
- Round 2: Agents critique each other's proposals
- Round 3: Synthesize consensus
"""

from typing import List, Dict, Any
from datetime import datetime
import json


class AgentNegotiator:
    """
    Orchestrates multi-agent negotiation for complex decision-making
    """

    def __init__(self, agents: List[Any]):
        """
        Initialize negotiator with list of agents

        Args:
            agents: List of agent instances (DemandAgent, InventoryAgent, etc.)
        """
        self.agents = agents

    def negotiate(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main negotiation workflow - 3 rounds of structured debate

        Args:
            scenario: Problem description with constraints and question

        Returns:
            Complete negotiation result with all rounds and final consensus
        """
        print(f"\n🤝 Starting negotiation with {len(self.agents)} agents...")

        # ROUND 1: Each agent proposes solution independently
        print("\n📋 ROUND 1: Collecting proposals...")
        proposals = self._round_1_proposals(scenario)

        # ROUND 2: Agents critique each other's proposals
        print("\n💬 ROUND 2: Agent critiques...")
        critiques = self._round_2_critiques(scenario, proposals)

        # ROUND 3: Synthesize consensus from all inputs
        print("\n🎯 ROUND 3: Building consensus...")
        consensus = self._round_3_consensus(scenario, proposals, critiques)

        return {
            "scenario": scenario,
            "round_1_proposals": proposals,
            "round_2_critiques": critiques,
            "round_3_consensus": consensus,
            "negotiation_complete": True,
            "timestamp": self._get_timestamp()
        }

    def _round_1_proposals(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Round 1: Each agent independently proposes a solution

        Args:
            scenario: Problem description

        Returns:
            Dictionary of agent proposals
        """
        proposals = {}

        for agent in self.agents:
            agent_name = agent.__class__.__name__.replace('Agent', '')
            print(f"  → {agent_name} Agent proposing...")

            # Build prompt for this agent to propose solution
            prompt = self._build_proposal_prompt(agent_name, scenario)

            # Get agent's proposal
            try:
                proposal_response = agent.run(prompt)
                proposals[agent_name] = {
                    "agent": agent_name,
                    "proposal": proposal_response,
                    "timestamp": self._get_timestamp()
                }
            except Exception as e:
                print(f"  ⚠️ Error from {agent_name} Agent: {e}")
                proposals[agent_name] = {
                    "agent": agent_name,
                    "proposal": f"Error generating proposal: {str(e)}",
                    "timestamp": self._get_timestamp()
                }

        return proposals

    def _round_2_critiques(self,
                          scenario: Dict[str, Any],
                          proposals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Round 2: Each agent critiques other agents' proposals

        Args:
            scenario: Original problem
            proposals: Round 1 proposals from all agents

        Returns:
            Dictionary of agent critiques
        """
        critiques = {}

        for agent in self.agents:
            agent_name = agent.__class__.__name__.replace('Agent', '')
            print(f"  → {agent_name} Agent critiquing...")

            # Get this agent's own proposal
            own_proposal = proposals.get(agent_name, {})

            # Get other agents' proposals
            other_proposals = {
                name: prop for name, prop in proposals.items()
                if name != agent_name
            }

            # Build critique prompt
            prompt = self._build_critique_prompt(
                agent_name,
                scenario,
                own_proposal,
                other_proposals
            )

            # Get agent's critique
            try:
                critique_response = agent.run(prompt)
                critiques[agent_name] = {
                    "agent": agent_name,
                    "critique": critique_response,
                    "timestamp": self._get_timestamp()
                }
            except Exception as e:
                print(f"  ⚠️ Error from {agent_name} Agent: {e}")
                critiques[agent_name] = {
                    "agent": agent_name,
                    "critique": f"Error generating critique: {str(e)}",
                    "timestamp": self._get_timestamp()
                }

        return critiques

    def _round_3_consensus(self,
                          scenario: Dict[str, Any],
                          proposals: Dict[str, Any],
                          critiques: Dict[str, Any]) -> Dict[str, Any]:
        """
        Round 3: Synthesize all proposals and critiques into consensus

        Args:
            scenario: Original problem
            proposals: Round 1 proposals
            critiques: Round 2 critiques

        Returns:
            Final consensus decision
        """
        print(f"  → Orchestrator synthesizing consensus...")

        # Use first agent as synthesizer (orchestrator role)
        synthesizer = self.agents[0]

        # Build consensus prompt with all information
        prompt = self._build_consensus_prompt(scenario, proposals, critiques)

        # Get final consensus
        try:
            consensus_response = synthesizer.run(prompt)
            return {
                "final_decision": consensus_response,
                "agents_involved": len(self.agents),
                "timestamp": self._get_timestamp()
            }
        except Exception as e:
            print(f"  ⚠️ Error generating consensus: {e}")
            return {
                "final_decision": f"Error generating consensus: {str(e)}",
                "agents_involved": len(self.agents),
                "timestamp": self._get_timestamp()
            }

    def _build_proposal_prompt(self, agent_name: str, scenario: Dict) -> str:
        """
        Build prompt for Round 1: Agent proposes solution

        Args:
            agent_name: Name of the agent
            scenario: Problem scenario

        Returns:
            Formatted prompt string
        """
        # Map agent names to domain expertise
        domain_map = {
            "Demand": "demand forecasting and customer relationships",
            "Inventory": "inventory optimization and stock management",
            "ProductionPlanning": "production scheduling and capacity planning",
            "MachineHealth": "equipment reliability and predictive maintenance",
            "Supplier": "supplier relationships and procurement"
        }

        domain = domain_map.get(agent_name, "manufacturing operations")

        return f"""You are the {agent_name} Agent, an expert in {domain}.

SCENARIO:
{json.dumps(scenario, indent=2)}

Your task: Propose a solution to this problem from YOUR domain perspective.

Think step-by-step:
1. What is the core problem from your perspective?
2. What constraints in your domain matter most?
3. What solution do you recommend?
4. What concerns or risks do you see?
5. How confident are you in this recommendation?

Provide your proposal in a clear, structured format with:
- Your recommended action
- Key reasoning points
- Concerns or risks
- Confidence level (0-100%)

Be specific and actionable. Focus on what YOU can control in your domain.
"""

    def _build_critique_prompt(self,
                               agent_name: str,
                               scenario: Dict,
                               own_proposal: Dict,
                               other_proposals: Dict) -> str:
        """
        Build prompt for Round 2: Agent critiques others

        Args:
            agent_name: Name of the agent
            scenario: Problem scenario
            own_proposal: This agent's Round 1 proposal
            other_proposals: Other agents' Round 1 proposals

        Returns:
            Formatted prompt string
        """
        return f"""You are the {agent_name} Agent.

SCENARIO:
{json.dumps(scenario, indent=2)}

YOUR PROPOSAL (Round 1):
{json.dumps(own_proposal.get('proposal', 'No proposal'), indent=2)}

OTHER AGENTS' PROPOSALS:
{json.dumps(other_proposals, indent=2)}

Your task: Analyze the other agents' proposals from YOUR domain perspective.

For each other agent's proposal, consider:
1. What do you agree with?
2. What concerns you from your domain perspective?
3. What are they missing or overlooking?
4. How could their proposal impact your domain?

After seeing others' perspectives, reflect:
- Does this change your original recommendation?
- What hybrid solution might work best?
- Where can you compromise, and where must you hold firm?

Provide structured critique covering:
- Points of agreement with each agent
- Concerns from your domain perspective
- Suggestions for improvement
- Your updated position after seeing all proposals
"""

    def _build_consensus_prompt(self,
                                scenario: Dict,
                                proposals: Dict,
                                critiques: Dict) -> str:
        """
        Build prompt for Round 3: Synthesize consensus

        Args:
            scenario: Problem scenario
            proposals: All Round 1 proposals
            critiques: All Round 2 critiques

        Returns:
            Formatted prompt string
        """
        return f"""You are the Orchestrator synthesizing a multi-agent negotiation.

SCENARIO:
{json.dumps(scenario, indent=2)}

ROUND 1 - AGENT PROPOSALS:
{json.dumps(proposals, indent=2)}

ROUND 2 - AGENT CRITIQUES:
{json.dumps(critiques, indent=2)}

Your task: Synthesize all inputs into ONE final recommendation.

The final decision must:
1. Address all valid concerns raised by agents
2. Maximize overall value across all domains
3. Be concrete and executable
4. Have buy-in from all agents (or document disagreements)

Think step-by-step:
1. What do all agents agree on? (Common ground)
2. Where do agents disagree? What are the root causes?
3. How can disagreements be resolved or balanced?
4. What's the optimal synthesis that serves all domains?
5. What execution steps are needed?
6. What risks remain and how to mitigate them?

Provide a clear final recommendation with:
- Final decision (accept/reject/modify)
- Concrete execution plan (step-by-step)
- How each agent's concerns are addressed
- Financial summary (if applicable)
- Risk assessment and mitigation strategies
- Overall confidence level (0-100%)

Be decisive but thorough. This decision will be executed.
"""

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp"""
        return datetime.now().isoformat()


# Example usage and testing
def test_negotiation():
    """
    Test function - demonstrates negotiation with mock agents
    """
    print("="*60)
    print("AGENT NEGOTIATION TEST")
    print("="*60)

    # Create mock agents (in real use, import actual agents)
    class MockAgent:
        def __init__(self, name):
            self.name = name

        def run(self, prompt):
            return f"{self.name} response to: {prompt[:100]}..."

    agents = [
        MockAgent("DemandAgent"),
        MockAgent("InventoryAgent"),
        MockAgent("ProductionPlanningAgent")
    ]

    # Create scenario
    scenario = {
        "problem": "Customer wants 2,000 units in 3 days",
        "constraints": {
            "production_capacity": 1500,
            "current_inventory": 300,
            "safety_stock_minimum": 200,
            "overtime_cost_per_100_units": 3000,
            "customer_lifetime_value": 500000
        },
        "question": "Should we accept this order? If yes, how do we fulfill it?"
    }

    # Run negotiation
    negotiator = AgentNegotiator(agents)
    result = negotiator.negotiate(scenario)

    print("\n" + "="*60)
    print("NEGOTIATION COMPLETE")
    print("="*60)
    print(f"\nAgents involved: {len(result['round_1_proposals'])}")
    print(f"Consensus reached: {result['negotiation_complete']}")

    return result


if __name__ == "__main__":
    test_negotiation()
