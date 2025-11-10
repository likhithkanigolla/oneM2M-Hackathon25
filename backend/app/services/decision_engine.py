from typing import Dict
from app.agents.base_agent import BaseAgent

class DecisionEngine:
    def __init__(self):
        # placeholder agents map
        self.agents = {
            "base": BaseAgent("base"),
        }

    async def get_agent_decisions(self, room, slos, active_scenarios) -> Dict:
        context = self._build_context(room, slos, active_scenarios)
        decisions = {}
        for agent_id, agent in self.agents.items():
            if agent.is_active():
                decision = await agent.make_decision(context)
                decisions[agent_id] = decision
        return decisions

    def _build_context(self, room, slos, scenarios):
        return {
            "room_state": getattr(room, "to_dict", lambda: room)(),
            "slos": slos,
            "active_scenarios": [s for s in (scenarios or [])],
        }

    async def aggregate_decision(self, decisions: Dict, agent_weights: Dict) -> str:
        # implement weighted voting / aggregation
        return "aggregate_placeholder"
