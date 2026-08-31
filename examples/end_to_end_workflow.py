"""Example 5: End-to-End Supply Chain Optimization Workflow."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.client import LlamaClient
from src.coordinator import CoordinatorAgent
from src.schemas.messages import TaskRequest
from src.tools.registry import ToolRegistry
from src.tools.code_executor import CodeExecutor
from src.tools.api_client import APIClient
from src.tools.database import DatabaseClient
from src.tools.file_system import FileSystemClient
import pandas as pd


async def main():
    """
    Execute an end-to-end supply chain optimization workflow.
    """
    print("\n" + "=" * 60)
    print("END-TO-END SUPPLY CHAIN OPTIMIZATION WORKFLOW")
    print("=" * 60)

    # Initialize LLM client
    llm_client = LlamaClient(
        api_base="http://localhost:11434",
        model="llama2:7b",
    )

    print("\n[INFO] Initialized Llama LLM client")

    # Initialize tool registry and register tools
    print("\n[TOOLS] Registering tools...")
    tools = ToolRegistry()
    
    # Register code executor
    code_executor = CodeExecutor()
    async def code_executor_wrapper(func_name, **kwargs):
        return await code_executor.execute(func_name, **kwargs)
    tools.register("code_executor", "Execute Python code for modeling")(code_executor_wrapper)
    
    # Register API client
    api_client = APIClient()
    async def api_client_wrapper(func_name, **kwargs):
        return await api_client.execute(func_name, **kwargs)
    tools.register("api_client", "Make HTTP API calls")(api_client_wrapper)
    
    # Register database client
    db_client = DatabaseClient()
    async def db_client_wrapper(func_name, **kwargs):
        return await db_client.execute(func_name, **kwargs)
    tools.register("database", "Query and manage database")(db_client_wrapper)
    
    # Register file system client
    fs_client = FileSystemClient()
    async def fs_client_wrapper(func_name, **kwargs):
        return await fs_client.execute(func_name, **kwargs)
    tools.register("file_system", "Read/write files")(fs_client_wrapper)
    
    print("  ✓ Code executor")
    print("  ✓ API client")
    print("  ✓ Database client")
    print("  ✓ File system client")

    # Initialize coordinator
    print("\n[AGENTS] Initializing multi-agent coordinator...")
    coordinator = CoordinatorAgent(llm_client, tools)
    print("  ✓ Demand Planning Agent")
    print("  ✓ Inventory Agent")
    print("  ✓ Procurement Agent")
    print("  ✓ Network Agent")
    print("  ✓ Operations Agent")
    print("  ✓ Risk Agent")

    # Define optimization scenario
    print("\n[SCENARIO] Setting up supply chain optimization scenario...")
    scenario = {
        "demand_params": {
            "forecast_method": "ensemble",
            "forecast_horizon": 12,
            "include_seasonality": True,
        },
        "inventory_params": {
            "service_level": 0.95,
            "optimization_horizon": 12,
            "segmentation_method": "abc_xyz",
        },
        "network_params": {
            "optimization_method": "facility_location",
            "service_level_target": 0.95,
            "max_facilities": 5,
        },
        "risk_params": {
            "include_geopolitical": True,
            "include_supplier_risk": True,
            "resilience_analysis": True,
        },
    }

    print("  ✓ Demand forecasting config")
    print("  ✓ Inventory optimization config")
    print("  ✓ Network design config")
    print("  ✓ Risk assessment config")

    # Execute end-to-end workflow
    print("\n[WORKFLOW] Executing end-to-end optimization...")
    print("  Processing: Demand → Inventory → Network → Risk")
    print()

    try:
        workflow_results = await coordinator.optimize_supply_chain(scenario)
        
        print(f"\n[RESULTS] Workflow completed successfully")
        print(f"  - Total tasks: {len(workflow_results)}")
        print(f"  - Successful: {sum(1 for r in workflow_results if r.status == 'success')}")
        print(f"  - Failed: {sum(1 for r in workflow_results if r.status == 'failure')}")
        
        print("\n[SUMMARY] Task Results:")
        for i, result in enumerate(workflow_results, 1):
            status_icon = "✓" if result.status == "success" else "✗"
            print(f"  {status_icon} Task {i}: {result.status}")
            print(f"    - Duration: {result.duration_seconds:.2f}s")
            if result.errors:
                print(f"    - Errors: {', '.join(result.errors[:2])}")

    except Exception as e:
        print(f"\n[ERROR] Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("END-TO-END WORKFLOW COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
