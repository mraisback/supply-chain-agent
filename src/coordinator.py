"""Coordinator Agent - orchestrates multi-agent workflows."""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from src.schemas.messages import TaskRequest, TaskResult, AgentMessage, ActionType
from src.agents.base import BaseAgent
from src.agents.demand_planning import DemandPlanningAgent
from src.agents.inventory import InventoryAgent
from src.agents.procurement import ProcurementAgent
from src.agents.network import NetworkAgent
from src.agents.operations import OperationsAgent
from src.agents.risk import RiskAgent
from src.llm.client import LlamaClient
from src.tools.registry import ToolRegistry


class CoordinatorAgent(BaseAgent):
    """Coordinates and delegates tasks across domain-specific agents."""

    def __init__(self, llm_client: LlamaClient, tools: Optional[ToolRegistry] = None):
        """
        Initialize coordinator agent.

        Args:
            llm_client: LLM client for reasoning
            tools: Shared tool registry
        """
        super().__init__(
            name="CoordinatorAgent",
            role="Supply Chain Intelligence Coordinator - orchestrates specialist agents, breaks down complex goals",
            llm_client=llm_client,
            tools=tools or ToolRegistry(),
        )

        # Initialize specialist agents
        self.demand_planning_agent = DemandPlanningAgent(llm_client, self.tools)
        self.inventory_agent = InventoryAgent(llm_client, self.tools)
        self.procurement_agent = ProcurementAgent(llm_client, self.tools)
        self.network_agent = NetworkAgent(llm_client, self.tools)
        self.operations_agent = OperationsAgent(llm_client, self.tools)
        self.risk_agent = RiskAgent(llm_client, self.tools)

        self.agents = {
            "demand_planning": self.demand_planning_agent,
            "inventory": self.inventory_agent,
            "procurement": self.procurement_agent,
            "network": self.network_agent,
            "operations": self.operations_agent,
            "risk": self.risk_agent,
        }

    async def validate_task(self, task: TaskRequest) -> bool:
        """Coordinator can route any task."""
        return True

    async def route_task(self, task: TaskRequest) -> TaskResult:
        """
        Route task to appropriate agent based on task type.

        Args:
            task: Task to route

        Returns:
            Task result
        """
        # Determine which agent should handle this task
        agent = await self._select_agent(task)

        if agent is None:
            return TaskResult(
                task_id=task.task_id,
                status="failure",
                result={},
                errors=[f"No suitable agent found for task type: {task.task_type}"],
            )

        # Execute task via selected agent
        return await agent.execute(task)

    async def _select_agent(self, task: TaskRequest) -> Optional[BaseAgent]:
        """
        Select appropriate agent for task.

        Args:
            task: Task to assign

        Returns:
            Selected agent or None
        """
        # Simple routing based on task type prefix
        if task.task_type.startswith("forecast") or "demand" in task.task_type:
            return self.demand_planning_agent
        elif "inventory" in task.task_type or "eoq" in task.task_type:
            return self.inventory_agent
        elif "procurement" in task.task_type or "supplier" in task.task_type:
            return self.procurement_agent
        elif "network" in task.task_type or "facility" in task.task_type:
            return self.network_agent
        elif "operation" in task.task_type or "warehouse" in task.task_type:
            return self.operations_agent
        elif "risk" in task.task_type or "resilience" in task.task_type:
            return self.risk_agent
        else:
            # Default: try each agent
            for agent in self.agents.values():
                if await agent.validate_task(task):
                    return agent
            return None

    async def execute_workflow(
        self,
        workflow_name: str,
        tasks: List[TaskRequest],
        parallel: bool = False,
    ) -> List[TaskResult]:
        """
        Execute a sequence of tasks (workflow).

        Args:
            workflow_name: Name of workflow
            tasks: List of tasks to execute
            parallel: Execute tasks in parallel if True

        Returns:
            List of task results
        """
        start_time = datetime.utcnow()
        results = []

        try:
            if parallel:
                # Execute all tasks concurrently
                results = await asyncio.gather(
                    *[self.route_task(task) for task in tasks],
                    return_exceptions=True,
                )
                # Handle exceptions
                results = [
                    r if isinstance(r, TaskResult) else TaskResult(
                        task_id="unknown",
                        status="failure",
                        result={},
                        errors=[str(r)],
                    )
                    for r in results
                ]
            else:
                # Execute tasks sequentially
                for task in tasks:
                    result = await self.route_task(task)
                    results.append(result)
        except Exception as e:
            results.append(
                TaskResult(
                    task_id="workflow",
                    status="failure",
                    result={},
                    errors=[str(e)],
                )
            )

        duration = (datetime.utcnow() - start_time).total_seconds()

        # Log workflow execution
        workflow_result = {
            "workflow_name": workflow_name,
            "task_count": len(tasks),
            "successful_tasks": sum(1 for r in results if r.status == "success"),
            "failed_tasks": sum(1 for r in results if r.status == "failure"),
            "duration_seconds": duration,
            "results": [r.to_dict() if hasattr(r, 'to_dict') else r.__dict__ for r in results],
        }

        return results

    async def optimize_supply_chain(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        End-to-end supply chain optimization workflow.

        Args:
            scenario: Supply chain scenario with parameters

        Returns:
            Optimization results
        """
        tasks = [
            TaskRequest(
                task_id="demand-forecast",
                task_type="forecast_demand",
                description="Forecast demand for all SKUs",
                parameters=scenario.get("demand_params", {}),
            ),
            TaskRequest(
                task_id="inventory-optimization",
                task_type="optimize_inventory",
                description="Optimize inventory levels",
                parameters=scenario.get("inventory_params", {}),
            ),
            TaskRequest(
                task_id="network-optimization",
                task_type="design_network",
                description="Optimize supply chain network",
                parameters=scenario.get("network_params", {}),
            ),
            TaskRequest(
                task_id="risk-assessment",
                task_type="map_supply_chain_risks",
                description="Assess supply chain risks",
                parameters=scenario.get("risk_params", {}),
            ),
        ]

        results = await self.execute_workflow(
            workflow_name="supply_chain_optimization",
            tasks=tasks,
            parallel=False,  # Sequential execution for dependencies
        )

        return {
            "workflow": "supply_chain_optimization",
            "results": [r.to_dict() if hasattr(r, 'to_dict') else r.__dict__ for r in results],
        }
