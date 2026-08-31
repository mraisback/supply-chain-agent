"""Network Agent - facility location, transportation, cost-to-serve."""

from src.agents.base import BaseAgent
from src.schemas.messages import TaskRequest


class NetworkAgent(BaseAgent):
    """Agent specializing in supply chain network design and optimization."""

    def __init__(self, llm_client, tools=None):
        super().__init__(
            name="NetworkAgent",
            role="Network Design Expert - facility location, transportation optimization, VRP, cost-to-serve, MILP modeling",
            llm_client=llm_client,
            tools=tools,
        )

    async def validate_task(self, task: TaskRequest) -> bool:
        """Validate if this agent can execute network design tasks."""
        network_tasks = [
            "design_network",
            "optimize_facility_location",
            "calculate_cost_to_serve",
            "optimize_transportation",
            "solve_vrp",
            "evaluate_cross_docking",
            "consolidate_distribution",
        ]
        return task.task_type in network_tasks
