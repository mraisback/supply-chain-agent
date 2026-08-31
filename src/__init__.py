"""Supply Chain Intelligence Agent - Multi-agent AI system for supply chain optimization."""

__version__ = "0.1.0"
__author__ = "Supply Chain Team"

from src.coordinator import CoordinatorAgent
from src.agents.base import BaseAgent

__all__ = [
    "CoordinatorAgent",
    "BaseAgent",
]
