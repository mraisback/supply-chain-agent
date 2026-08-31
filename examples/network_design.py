"""Example 3: Network Design and Optimization."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.client import LlamaClient
from src.agents.network import NetworkAgent
from src.schemas.messages import TaskRequest
import pandas as pd


async def main():
    """
    Optimize supply chain network design and facility locations.
    """
    print("\n" + "=" * 60)
    print("NETWORK DESIGN EXAMPLE")
    print("=" * 60)

    # Initialize LLM client
    llm_client = LlamaClient(
        api_base="http://localhost:11434",
        model="llama2:7b",
    )

    print("\n[INFO] Initialized Llama LLM client")

    # Sample facility data
    facilities = pd.DataFrame({
        "facility_id": ["DC1", "DC2", "DC3"],
        "name": ["Distribution Center East", "Distribution Center Midwest", "Distribution Center West"],
        "location": ["New York", "Chicago", "Los Angeles"],
        "latitude": [40.7128, 41.8781, 34.0522],
        "longitude": [-74.0060, -87.6298, -118.2437],
        "capacity_units": [50000, 40000, 60000],
        "operating_cost_per_unit": [0.5, 0.45, 0.55],
    })

    print(f"\n[DATA] Loaded {len(facilities)} distribution centers")
    for idx, row in facilities.iterrows():
        print(f"  - {row['name']} ({row['location']}): {row['capacity_units']:,} units")

    # Sample demand points
    demand_points = pd.DataFrame({
        "location": ["Boston", "Miami", "Dallas", "Denver", "Seattle"],
        "annual_demand": [5000, 4000, 6000, 3000, 2500],
        "latitude": [42.3601, 25.7617, 32.7767, 39.7392, 47.6062],
        "longitude": [-71.0589, -80.1918, -96.7970, -104.9903, -122.3321],
    })

    print(f"\n[DATA] Loaded {len(demand_points)} demand locations")
    for idx, row in demand_points.iterrows():
        print(f"  - {row['location']}: {row['annual_demand']:,} units")

    # Initialize network agent
    print("\n[AGENT] Initializing Network Agent...")
    agent = NetworkAgent(llm_client)

    # Create network design task
    task = TaskRequest(
        task_id="network_design_v1",
        task_type="design_network",
        description="Optimize network design for distribution centers",
        parameters={
            "optimization_method": "facility_location",
            "service_level_target": 0.95,
            "max_facilities": 4,
        },
    )

    print(f"\n[TASK] Executing network design optimization...")
    try:
        result = await agent.execute(task)
        print(f"\n[RESULT] Task completed: {result.status}")
        print(f"  - Duration: {result.duration_seconds:.2f}s")
        if result.result:
            print(f"  - Optimization results: {len(result.result)} items")
    except Exception as e:
        print(f"\n[ERROR] Task failed: {e}")

    print("\n" + "=" * 60)
    print("NETWORK DESIGN EXAMPLE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
