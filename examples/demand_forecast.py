"""Example 1: Demand Forecasting."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.client import LlamaClient
from src.agents.demand_planning import DemandPlanningAgent
from src.schemas.messages import TaskRequest
from src.models.forecasting import ForecastingModels
from src.data.profiler import DataProfiler
import pandas as pd
import numpy as np


async def main():
    """
    Forecast demand using multiple time-series methods.
    """
    print("\n" + "=" * 60)
    print("DEMAND FORECASTING EXAMPLE")
    print("=" * 60)

    # Initialize LLM client
    llm_client = LlamaClient(
        api_base="http://localhost:11434",
        model="llama2:7b",
        temperature=0.7,
        max_tokens=2048,
    )

    print("\n[INFO] Initialized Llama LLM client")

    # Create sample demand data
    dates = pd.date_range("2023-01-01", periods=24, freq="M")
    demand_data = pd.Series(
        [
            100, 110, 115, 120, 105, 115, 130, 140, 135, 125, 120, 130,
            110, 120, 125, 130, 115, 125, 140, 150, 145, 135, 130, 140,
        ],
        index=dates,
        name="demand",
    )

    print(f"\n[DATA] Loaded {len(demand_data)} periods of demand data")
    print(f"  - Range: {demand_data.min()} to {demand_data.max()} units")
    print(f"  - Mean: {demand_data.mean():.2f}, Std Dev: {demand_data.std():.2f}")

    # Test simple moving average
    print("\n[MODEL] Calculating Simple Moving Average (12-month)...")
    sma = ForecastingModels.simple_moving_average(demand_data, periods=12)
    print(f"  - SMA Forecast: {sma.iloc[-1]:.2f} units")

    # Test exponential smoothing
    print("\n[MODEL] Calculating Exponential Smoothing (α=0.3)...")
    exp_smooth = ForecastingModels.exponential_smoothing(demand_data, alpha=0.3)
    print(f"  - Exp Smooth Forecast: {exp_smooth.iloc[-1]:.2f} units")

    # Test seasonality detection
    print("\n[MODEL] Analyzing demand seasonality...")
    seasonal_result = ForecastingModels.forecast_with_seasonality(
        demand_data, seasonal_periods=12, forecast_horizon=6
    )
    print(f"  - Seasonal pattern detected")
    print(f"  - Trend: {seasonal_result['trend'].iloc[-1]:.2f}")

    # Calculate forecast accuracy metrics
    print("\n[METRICS] Forecast Accuracy Analysis...")
    actual = demand_data.iloc[-12:]
    predicted = exp_smooth.iloc[-12:]
    
    mape = ForecastingModels.calculate_mape(actual, predicted)
    wmape = ForecastingModels.calculate_wmape(actual, predicted)
    mad = ForecastingModels.calculate_mad(actual, predicted)
    bias = ForecastingModels.calculate_forecast_bias(actual, predicted)
    
    print(f"  - MAPE: {mape:.2f}%")
    print(f"  - WMAPE: {wmape:.2f}%")
    print(f"  - MAD: {mad:.2f} units")
    print(f"  - Bias: {bias:.2f} units")

    # Initialize demand planning agent
    print("\n[AGENT] Initializing Demand Planning Agent...")
    agent = DemandPlanningAgent(llm_client)

    # Create task
    task = TaskRequest(
        task_id="forecast_sku001",
        task_type="forecast_demand",
        description="Forecast demand for SKU001 for next 6 months",
        parameters={
            "sku": "SKU001",
            "forecast_horizon": 6,
            "method": "ensemble",
        },
    )

    print("\n[TASK] Executing demand forecast task...")
    print(f"  - Task ID: {task.task_id}")
    print(f"  - Type: {task.task_type}")
    print(f"  - Horizon: {task.parameters['forecast_horizon']} months")

    # Execute task
    try:
        result = await agent.execute(task)
        print(f"\n[RESULT] Task completed with status: {result.status}")
        print(f"  - Duration: {result.duration_seconds:.2f}s")
        print(f"  - Messages: {len(result.messages)}")
        if result.errors:
            print(f"  - Errors: {result.errors}")
    except Exception as e:
        print(f"\n[ERROR] Task execution failed: {e}")

    print("\n" + "=" * 60)
    print("DEMAND FORECASTING EXAMPLE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
