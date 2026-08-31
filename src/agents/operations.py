"""Operations Agent - WMS/ERP data, warehouse performance, OTIF."""

from src.agents.base import BaseAgent
from src.schemas.messages import TaskRequest


class OperationsAgent(BaseAgent):
    """Agent specializing in warehouse and distribution operations."""

    def __init__(self, llm_client, tools=None):
        super().__init__(
            name="OperationsAgent",
            role="Operations Expert - WMS/ERP systems, OTIF, fill rate, labor planning, dock scheduling, pick-path optimization",
            llm_client=llm_client,
            tools=tools,
        )

    async def validate_task(self, task: TaskRequest) -> bool:
        """Validate if this agent can execute operations tasks."""
        ops_tasks = [
            "analyze_otif",
            "optimize_labor_planning",
            "schedule_dock",
            "optimize_pick_path",
            "compute_inventory_accuracy",
            "analyze_warehouse_performance",
        ]
        return task.task_type in ops_tasks
