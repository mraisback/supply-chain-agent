"""Inventory Agent - EOQ, safety stock, multi-echelon optimization."""

from src.agents.base import BaseAgent
from src.schemas.messages import TaskRequest


class InventoryAgent(BaseAgent):
    """Agent specializing in inventory optimization and control."""

    def __init__(self, llm_client, tools=None):
        super().__init__(
            name="InventoryAgent",
            role="Inventory Management Expert - EOQ, reorder points, safety stock, ABC-XYZ segmentation, multi-echelon systems",
            llm_client=llm_client,
            tools=tools,
        )

    async def validate_task(self, task: TaskRequest) -> bool:
        """Validate if this agent can execute inventory tasks."""
        inventory_tasks = [
            "optimize_inventory",
            "calculate_eoq",
            "compute_safety_stock",
            "segment_skus_abc_xyz",
            "optimize_multi_echelon",
            "assess_obsolescence_risk",
        ]
        return task.task_type in inventory_tasks
