"""Example 2: Inventory Optimization."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.client import LlamaClient
from src.agents.inventory import InventoryAgent
from src.schemas.messages import TaskRequest
from src.models.optimization import OptimizationModels
from src.models.segmentation import SegmentationModels
import pandas as pd


async def main():
    """
    Optimize inventory levels using EOQ, safety stock, and segmentation.
    """
    print("\n" + "=" * 60)
    print("INVENTORY OPTIMIZATION EXAMPLE")
    print("=" * 60)

    # Initialize LLM client
    llm_client = LlamaClient(
        api_base="http://localhost:11434",
        model="llama2:7b",
    )

    print("\n[INFO] Initialized Llama LLM client")

    # Sample SKU data
    skus = pd.DataFrame({
        "sku_id": ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"],
        "description": ["Widget A", "Widget B", "Component C", "Assembly D", "Part E"],
        "annual_demand": [1000, 2000, 500, 5000, 300],
        "annual_spend": [10000, 15000, 5000, 25000, 2000],
        "ordering_cost": [50, 50, 50, 50, 50],
        "holding_cost_per_unit": [1.0, 1.5, 2.0, 0.5, 3.0],
        "avg_demand": [83.3, 166.7, 41.7, 416.7, 25.0],
        "demand_std_dev": [20, 40, 10, 100, 5],
    })

    print(f"\n[DATA] Loaded {len(skus)} SKUs for analysis")

    # EOQ Calculation
    print("\n[MODEL] Calculating Economic Order Quantity (EOQ)...")
    for idx, row in skus.iterrows():
        eoq_result = OptimizationModels.calculate_eoq(
            annual_demand=row["annual_demand"],
            ordering_cost=row["ordering_cost"],
            holding_cost_per_unit=row["holding_cost_per_unit"],
        )
        eoq_result.sku_id = row["sku_id"]
        print(f"  {row['sku_id']}: EOQ = {eoq_result.economic_order_quantity:.0f} units")
        print(f"    - Total Annual Cost: ${eoq_result.total_annual_cost:.2f}")
        print(f"    - Orders/Year: {eoq_result.orders_per_year:.1f}")

    # Safety Stock Calculation
    print("\n[MODEL] Calculating Safety Stock (95% Service Level)...")
    safety_stocks = {}
    for idx, row in skus.iterrows():
        ss = OptimizationModels.calculate_safety_stock(
            demand_std_dev=row["demand_std_dev"],
            lead_time_std_dev=0.5,  # Assume 0.5 day lead time std dev
            average_demand=row["avg_demand"],
            average_lead_time=7,  # 7-day lead time
            service_level=0.95,
        )
        safety_stocks[row["sku_id"]] = ss["safety_stock"]
        print(f"  {row['sku_id']}: Safety Stock = {ss['safety_stock']:.0f} units")
        print(f"    - Reorder Point: {ss['reorder_point']:.0f} units")

    # ABC-XYZ Segmentation
    print("\n[MODEL] ABC-XYZ Segmentation Analysis...")
    abc_xyz_analysis = SegmentationModels.abc_xyz_matrix(
        skus, annual_spend_col="annual_spend"
    )
    print("\n  Segmentation Results:")
    for idx, row in abc_xyz_analysis.iterrows():
        print(f"  {row['sku_id']}: {row['abc_class']}{row['xyz_class']}")
        print(f"    - Strategy: {row['strategy']}")

    # Initialize inventory agent
    print("\n[AGENT] Initializing Inventory Agent...")
    agent = InventoryAgent(llm_client)

    # Create optimization task
    task = TaskRequest(
        task_id="inventory_optimization_v1",
        task_type="optimize_inventory",
        description="Optimize inventory levels across all SKUs",
        parameters={
            "service_level": 0.95,
            "lead_time_days": 7,
            "optimization_horizon_months": 12,
        },
    )

    print(f"\n[TASK] Executing inventory optimization task...")
    try:
        result = await agent.execute(task)
        print(f"\n[RESULT] Task completed: {result.status}")
        print(f"  - Duration: {result.duration_seconds:.2f}s")
    except Exception as e:
        print(f"\n[ERROR] Task failed: {e}")

    print("\n" + "=" * 60)
    print("INVENTORY OPTIMIZATION EXAMPLE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
