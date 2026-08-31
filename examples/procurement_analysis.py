"""Example 4: Procurement and Sourcing Analysis."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.client import LlamaClient
from src.agents.procurement import ProcurementAgent
from src.schemas.messages import TaskRequest
from src.models.risk import RiskModels
import pandas as pd


async def main():
    """
    Analyze sourcing strategy using Kraljic Matrix and supplier scoring.
    """
    print("\n" + "=" * 60)
    print("PROCUREMENT & SOURCING ANALYSIS EXAMPLE")
    print("=" * 60)

    # Initialize LLM client
    llm_client = LlamaClient(
        api_base="http://localhost:11434",
        model="llama2:7b",
    )

    print("\n[INFO] Initialized Llama LLM client")

    # Sample supplier data
    suppliers = pd.DataFrame({
        "supplier_id": ["SUPP001", "SUPP002", "SUPP003", "SUPP004"],
        "name": ["Supplier A", "Supplier B", "Supplier C", "Supplier D"],
        "location": ["USA", "Mexico", "China", "India"],
        "quality_score": [95, 85, 75, 90],
        "reliability_score": [90, 80, 70, 88],
        "cost_competitiveness": [80, 95, 90, 75],
        "geographic_concentration": [0.1, 0.3, 0.5, 0.2],
        "single_source_dependency": [False, True, False, False],
    })

    print(f"\n[DATA] Loaded {len(suppliers)} suppliers for analysis")

    # Calculate supplier risk scores
    print("\n[MODEL] Calculating Supplier Risk Scores...")
    suppliers["risk_score"] = 0.0
    for idx, row in suppliers.iterrows():
        risk_data = RiskModels.supplier_risk_score(
            quality_score=row["quality_score"],
            reliability_score=row["reliability_score"],
            cost_competitiveness=row["cost_competitiveness"],
            geographic_concentration=row["geographic_concentration"],
            single_source_dependency=row["single_source_dependency"],
        )
        suppliers.loc[idx, "risk_score"] = risk_data["overall_risk_score"]
        print(f"  {row['name']}: {risk_data['risk_level'].upper()} risk")
        print(f"    - Risk Score: {risk_data['overall_risk_score']:.3f}")
        print(f"    - Quality: {risk_data['quality_risk']:.3f}, Reliability: {risk_data['reliability_risk']:.3f}")

    # Dual sourcing analysis
    print("\n[MODEL] Dual-Sourcing Economics Analysis...")
    dual_source = RiskModels.dual_sourcing_economics(
        single_source_cost=100000,
        dual_source_cost_increase_pct=15,
        disruption_probability=0.05,
        disruption_impact_days=14,
        daily_revenue_loss=5000,
    )
    print(f"  - Single Source Annual Cost: ${100000:,.0f}")
    print(f"  - Dual Source Annual Cost: ${dual_source['annual_dual_sourcing_cost']:,.0f}")
    print(f"  - Expected Disruption Cost: ${dual_source['expected_disruption_cost']:,.0f}")
    print(f"  - Recommendation: {'Dual source' if dual_source['dual_sourcing_recommended'] else 'Single source'}")

    # Initialize procurement agent
    print("\n[AGENT] Initializing Procurement Agent...")
    agent = ProcurementAgent(llm_client)

    # Create sourcing strategy task
    task = TaskRequest(
        task_id="procurement_analysis_v1",
        task_type="evaluate_sourcing_strategy",
        description="Evaluate optimal sourcing strategy for critical components",
        parameters={
            "analysis_type": "kraljic_matrix",
            "risk_tolerance": "medium",
            "cost_optimization_target": 0.95,
        },
    )

    print(f"\n[TASK] Executing sourcing strategy analysis...")
    try:
        result = await agent.execute(task)
        print(f"\n[RESULT] Task completed: {result.status}")
        print(f"  - Duration: {result.duration_seconds:.2f}s")
    except Exception as e:
        print(f"\n[ERROR] Task failed: {e}")

    print("\n" + "=" * 60)
    print("PROCUREMENT ANALYSIS EXAMPLE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
