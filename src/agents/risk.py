"""Risk Agent - supply chain resilience, risk mapping, dual-sourcing."""

from src.agents.base import BaseAgent
from src.schemas.messages import TaskRequest


class RiskAgent(BaseAgent):
    """Agent specializing in supply chain risk and resilience."""

    def __init__(self, llm_client, tools=None):
        super().__init__(
            name="RiskAgent",
            role="Risk & Resilience Expert - supply chain risk mapping, geopolitical analysis, bullwhip effect, business continuity, dual-sourcing economics",
            llm_client=llm_client,
            tools=tools,
        )

    async def validate_task(self, task: TaskRequest) -> bool:
        """Validate if this agent can execute risk tasks."""
        risk_tasks = [
            "map_supply_chain_risks",
            "assess_geopolitical_risk",
            "evaluate_single_source_risk",
            "simulate_disruption",
            "quantify_bullwhip_effect",
            "design_business_continuity_plan",
        ]
        return task.task_type in risk_tasks
