class BaseAgent:
    def __init__(self, agent_id: str = "base"):
        self.agent_id = agent_id

    def is_active(self) -> bool:
        return True

    async def make_decision(self, context: dict) -> dict:
        # Return a placeholder decision. Implement LLM integration in specialized agents.
        return {
            "action": "noop",
            "scores": {"comfort": 0.0, "energy": 0.0, "reliability": 0.0},
            "reasoning": "BaseAgent placeholder",
        }
