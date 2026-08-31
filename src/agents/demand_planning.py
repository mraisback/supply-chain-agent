"""Demand Planning Agent - forecasting, demand sensing, new-product analysis."""

from src.agents.base import BaseAgent
from src.schemas.messages import TaskRequest


class DemandPlanningAgent(BaseAgent):
    """Agent specializing in demand forecasting and planning."""

    def __init__(self, llm_client, tools=None):
        super().__init__(
            name="DemandPlanningAgent",
            role="Demand Planning Expert - fluent in time series forecasting, ML models, and demand sensing",
            llm_client=llm_client,
            tools=tools,
        )

    async def validate_task(self, task: TaskRequest) -> bool:
        """Validate if this agent can execute demand planning tasks."""
        demand_tasks = [
            "forecast_demand",
            "analyze_demand_pattern",
            "detect_demand_shocks",
            "forecast_new_product_demand",
            "quantify_promotional_uplift",
        ]
        return task.task_type in demand_tasks
