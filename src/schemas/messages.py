"""Agent message protocols and types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime


class ActionType(str, Enum):
    """Types of agent actions."""
    REASONING = "reasoning"
    TOOL_USE = "tool_use"
    RESULT = "result"
    ERROR = "error"
    COMPLETE = "complete"


@dataclass
class ToolRequest:
    """Request to execute a tool."""
    tool_name: str
    function: str
    params: Dict[str, Any]
    timeout: int = 300

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "function": self.function,
            "params": self.params,
            "timeout": self.timeout,
        }


@dataclass
class AgentMessage:
    """Message from an agent."""
    agent_name: str
    step: int
    action: ActionType
    content: str
    tool_requests: List[ToolRequest] = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "step": self.step,
            "action": self.action.value,
            "content": self.content,
            "tool_requests": [t.to_dict() for t in self.tool_requests],
            "tool_results": self.tool_results,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TaskRequest:
    """Request to execute a supply chain task."""
    task_id: str
    task_type: str  # e.g., "forecast_demand", "optimize_inventory"
    description: str
    parameters: Dict[str, Any]
    priority: int = 1
    timeout: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of a completed task."""
    task_id: str
    status: str  # "success", "failure", "partial"
    result: Dict[str, Any]
    messages: List[AgentMessage] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
