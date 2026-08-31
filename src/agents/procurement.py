"""Procurement Agent - sourcing strategy, TCO, supplier risk."""

from src.agents.base import BaseAgent
from src.schemas.messages import TaskRequest


class ProcurementAgent(BaseAgent):
    """Agent specializing in procurement and sourcing."""

    def __init__(self, llm_client, tools=None):
        super().__init__(
            name="ProcurementAgent",
            role="Procurement Expert - Kraljic Matrix, TCO modeling, should-cost analysis, supplier risk, dual-sourcing strategy",
            llm_client=llm_client,
            tools=tools,
        )

    async def validate_task(self, task: TaskRequest) -> bool:
        """Validate if this agent can execute procurement tasks."""
        procurement_tasks = [
            "categorize_suppliers",
            "compute_should_cost",
            "calculate_tco",
            "score_suppliers",
            "analyze_spend",
            "evaluate_sourcing_strategy",
            "assess_supply_concentration_risk",
        ]
        return task.task_type in procurement_tasks
