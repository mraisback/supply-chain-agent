"""Base agent class - foundation for all domain-specific agents."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from src.schemas.messages import AgentMessage, ActionType, ToolRequest, TaskRequest, TaskResult
from src.tools.registry import ToolRegistry


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, role: str, llm_client: Any, tools: Optional[ToolRegistry] = None):
        """
        Initialize a base agent.

        Args:
            name: Agent name
            role: Agent role/expertise area
            llm_client: LLM client for reasoning
            tools: Registry of available tools
        """
        self.name = name
        self.role = role
        self.llm_client = llm_client
        self.tools = tools or ToolRegistry()
        self.message_history: List[AgentMessage] = []
        self.step_counter = 0

    async def execute(self, task: TaskRequest) -> TaskResult:
        """
        Execute a task using ReAct loop: Reason -> Act -> Observe.

        Args:
            task: Task to execute

        Returns:
            Result of task execution
        """
        start_time = datetime.utcnow()
        errors: List[str] = []
        result_data: Dict[str, Any] = {}

        try:
            # 1. REASONING PHASE
            reasoning_msg = await self._reason(task)
            self.message_history.append(reasoning_msg)

            # 2. PLANNING PHASE - identify tools needed
            current_context = self._build_context()
            plan_msg = await self._plan(task, reasoning_msg, current_context)
            self.message_history.append(plan_msg)

            # 3. ACTION PHASE - execute tools
            if plan_msg.tool_requests:
                action_msg = await self._act(plan_msg.tool_requests)
                self.message_history.append(action_msg)
            else:
                action_msg = None

            # 4. OBSERVATION & REFINEMENT
            final_msg = await self._observe_and_refine(task, reasoning_msg, plan_msg, action_msg)
            self.message_history.append(final_msg)

            result_data = final_msg.tool_results
            status = "success"

        except Exception as e:
            errors.append(str(e))
            status = "failure"

        duration = (datetime.utcnow() - start_time).total_seconds()

        return TaskResult(
            task_id=task.task_id,
            status=status,
            result=result_data,
            messages=self.message_history,
            errors=errors,
            duration_seconds=duration,
        )

    async def _reason(self, task: TaskRequest) -> AgentMessage:
        """
        Reasoning phase: Analyze the task and develop approach.
        """
        self.step_counter += 1
        prompt = f"""
        You are a {self.role} expert. Analyze this task and develop an approach:
        
        Task: {task.task_type}
        Description: {task.description}
        Parameters: {json.dumps(task.parameters, indent=2)}
        
        Think through:
        1. What is being asked?
        2. What data or models do we need?
        3. What are the key steps?
        4. What assumptions should we validate?
        
        Provide a clear reasoning chain.
        """

        response = await self.llm_client.generate(prompt)

        return AgentMessage(
            agent_name=self.name,
            step=self.step_counter,
            action=ActionType.REASONING,
            content=response,
        )

    async def _plan(self, task: TaskRequest, reasoning_msg: AgentMessage, context: str) -> AgentMessage:
        """
        Planning phase: Determine which tools to use.
        """
        self.step_counter += 1
        available_tools = self.tools.list_tools()
        tools_desc = "\n".join(
            [f"- {t['name']}: {t['description']}" for t in available_tools]
        )

        prompt = f"""
        Based on your reasoning, what tools do you need to execute this task?
        
        Reasoning: {reasoning_msg.content}
        Current Context: {context}
        
        Available Tools:
        {tools_desc}
        
        Return a JSON array of tool calls in this format:
        {{
            "tools": [
                {{
                    "tool_name": "tool_name",
                    "function": "function_name",
                    "params": {{"param1": "value1"}}
                }}
            ]
        }}
        """

        response = await self.llm_client.generate(prompt)
        tool_requests = self._parse_tool_requests(response)

        return AgentMessage(
            agent_name=self.name,
            step=self.step_counter,
            action=ActionType.TOOL_USE,
            content=response,
            tool_requests=tool_requests,
        )

    async def _act(self, tool_requests: List[ToolRequest]) -> AgentMessage:
        """
        Action phase: Execute planned tools.
        """
        self.step_counter += 1
        results: Dict[str, Any] = {}

        for tool_req in tool_requests:
            try:
                result = await self.tools.execute(
                    tool_req.tool_name,
                    tool_req.function,
                    tool_req.params,
                    timeout=tool_req.timeout,
                )
                results[f"{tool_req.tool_name}:{tool_req.function}"] = result
            except Exception as e:
                results[f"{tool_req.tool_name}:{tool_req.function}"] = {"error": str(e)}

        return AgentMessage(
            agent_name=self.name,
            step=self.step_counter,
            action=ActionType.RESULT,
            content="Tools executed successfully",
            tool_results=results,
        )

    async def _observe_and_refine(self, task: TaskRequest, *messages: AgentMessage) -> AgentMessage:
        """
        Observation phase: Analyze results and refine if needed.
        """
        self.step_counter += 1
        results_summary = self._summarize_results(messages[-1] if messages else None)

        prompt = f"""
        Based on the execution results, provide a final analysis and recommendation:
        
        Task: {task.task_type}
        Results Summary: {results_summary}
        
        Provide:
        1. Key findings
        2. Recommendations
        3. Any caveats or limitations
        4. Next steps if applicable
        """

        response = await self.llm_client.generate(prompt)

        return AgentMessage(
            agent_name=self.name,
            step=self.step_counter,
            action=ActionType.COMPLETE,
            content=response,
            tool_results=messages[-1].tool_results if messages else {},
        )

    @abstractmethod
    async def validate_task(self, task: TaskRequest) -> bool:
        """Validate if this agent can execute the task."""
        pass

    def _build_context(self) -> str:
        """Build context from message history."""
        if not self.message_history:
            return "No prior context"
        return "\n".join([f"Step {m.step}: {m.content[:200]}..." for m in self.message_history[-3:]])

    def _parse_tool_requests(self, response: str) -> List[ToolRequest]:
        """Parse tool requests from LLM response."""
        try:
            data = json.loads(response)
            tool_requests = []
            for tool_data in data.get("tools", []):
                tool_requests.append(
                    ToolRequest(
                        tool_name=tool_data["tool_name"],
                        function=tool_data["function"],
                        params=tool_data.get("params", {}),
                    )
                )
            return tool_requests
        except (json.JSONDecodeError, KeyError):
            return []

    def _summarize_results(self, msg: Optional[AgentMessage]) -> str:
        """Summarize tool results for reporting."""
        if not msg or not msg.tool_results:
            return "No results"
        summary_parts = []
        for key, value in msg.tool_results.items():
            if isinstance(value, dict) and "error" in value:
                summary_parts.append(f"{key}: ERROR - {value['error']}")
            else:
                summary_parts.append(f"{key}: Success")
        return "\n".join(summary_parts)
