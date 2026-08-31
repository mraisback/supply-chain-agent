"""Optimization models - EOQ, network MILP, resource allocation."""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List, Any
from dataclasses import dataclass


@dataclass
class EOQResult:
    """Result of EOQ optimization."""
    sku_id: str
    economic_order_quantity: float
    annual_ordering_cost: float
    annual_holding_cost: float
    total_annual_cost: float
    reorder_point: float
    orders_per_year: float


class OptimizationModels:
    """Collection of optimization models for supply chain."""

    @staticmethod
    def calculate_eoq(
        annual_demand: float,
        ordering_cost: float,
        holding_cost_per_unit: float,
    ) -> EOQResult:
        """
        Calculate Economic Order Quantity (EOQ).

        Classic inventory optimization formula:
        EOQ = sqrt((2 * D * S) / H)
        where D = annual demand, S = ordering cost, H = holding cost per unit per year

        Args:
            annual_demand: Annual demand quantity
            ordering_cost: Cost per order
            holding_cost_per_unit: Holding cost per unit per year

        Returns:
            EOQResult with optimization metrics
        """
        if holding_cost_per_unit <= 0 or ordering_cost <= 0:
            return EOQResult(
                sku_id="unknown",
                economic_order_quantity=0,
                annual_ordering_cost=0,
                annual_holding_cost=0,
                total_annual_cost=0,
                reorder_point=0,
                orders_per_year=0,
            )

        eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost_per_unit)
        orders_per_year = annual_demand / eoq if eoq > 0 else 0
        annual_ordering_cost = orders_per_year * ordering_cost
        annual_holding_cost = (eoq / 2) * holding_cost_per_unit
        total_cost = annual_ordering_cost + annual_holding_cost
        reorder_point = (annual_demand / 365) * 1  # Assumes 1-day lead time by default

        return EOQResult(
            sku_id="unknown",
            economic_order_quantity=eoq,
            annual_ordering_cost=annual_ordering_cost,
            annual_holding_cost=annual_holding_cost,
            total_annual_cost=total_cost,
            reorder_point=reorder_point,
            orders_per_year=orders_per_year,
        )

    @staticmethod
    def calculate_safety_stock(
        demand_std_dev: float,
        lead_time_std_dev: float,
        average_demand: float,
        average_lead_time: float,
        service_level: float = 0.95,
    ) -> Dict[str, float]:
        """
        Calculate safety stock using statistical method.

        Safety Stock = Z * sqrt((LT * σ_d²) + (d_avg² * σ_lt²))
        where:
        - Z = service level factor (from z-score table)
        - LT = average lead time
        - σ_d = demand standard deviation
        - d_avg = average demand
        - σ_lt = lead time standard deviation

        Args:
            demand_std_dev: Standard deviation of demand
            lead_time_std_dev: Standard deviation of lead time
            average_demand: Average daily/period demand
            average_lead_time: Average lead time in days/periods
            service_level: Service level (0-1, e.g., 0.95 = 95%)

        Returns:
            Dictionary with safety stock and reorder point
        """
        # Z-score mapping for common service levels
        z_scores = {
            0.90: 1.28,
            0.95: 1.645,
            0.99: 2.326,
            0.999: 3.09,
        }
        z = z_scores.get(service_level, 1.645)

        # Variance formula
        variance = (average_lead_time * (demand_std_dev ** 2)) + (
            (average_demand ** 2) * (lead_time_std_dev ** 2)
        )
        safety_stock = z * np.sqrt(variance)
        reorder_point = (average_demand * average_lead_time) + safety_stock

        return {
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "service_level": service_level,
            "z_score": z,
        }

    @staticmethod
    def newsvendor_optimization(
        mean_demand: float,
        std_dev_demand: float,
        unit_cost: float,
        selling_price: float,
        salvage_price: float = 0,
    ) -> Dict[str, float]:
        """
        Newsvendor model for perishable/seasonal goods.

        Optimal order quantity balances:
        - Overstocking cost: (unit_cost - salvage_price)
        - Understocking cost: (selling_price - unit_cost)

        Args:
            mean_demand: Mean demand
            std_dev_demand: Standard deviation of demand
            unit_cost: Cost per unit
            selling_price: Selling price per unit
            salvage_price: Price received for unsold inventory

        Returns:
            Dictionary with optimal order quantity and expected profit
        """
        overstocking_cost = unit_cost - salvage_price
        understocking_cost = selling_price - unit_cost
        total_cost = overstocking_cost + understocking_cost

        # Critical ratio
        critical_ratio = understocking_cost / total_cost if total_cost > 0 else 0.5

        # Z-score for critical ratio
        from scipy.stats import norm
        z = norm.ppf(critical_ratio)

        # Optimal order quantity
        optimal_order_qty = mean_demand + (z * std_dev_demand)

        # Expected profit (simplified)
        expected_profit = (
            (selling_price - unit_cost) * mean_demand
            - understocking_cost * (std_dev_demand * norm.pdf(z))
        )

        return {
            "optimal_order_quantity": optimal_order_qty,
            "critical_ratio": critical_ratio,
            "expected_profit": expected_profit,
            "safety_stock": z * std_dev_demand,
        }

    @staticmethod
    def multi_echelon_optimization(
        skus: pd.DataFrame,
        demand_forecast: pd.Series,
        lead_times: Dict[str, float],
        holding_costs: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Multi-echelon inventory optimization (simplified).

        Args:
            skus: DataFrame with SKU data
            demand_forecast: Forecasted demand
            lead_times: Lead times by echelon
            holding_costs: Holding costs by echelon

        Returns:
            Optimization results
        """
        results = {
            "echelon_1": {},
            "echelon_2": {},
            "total_inventory_cost": 0,
        }

        # Simplified: allocate inventory proportionally down the network
        total_demand = demand_forecast.sum()
        for echelon in ["echelon_1", "echelon_2"]:
            echelon_allocation = total_demand * 0.5  # Simple 50/50 split
            echelon_holding_cost = holding_costs.get(echelon, 0.5)
            cost = echelon_allocation * echelon_holding_cost
            results[echelon] = {"allocation": echelon_allocation, "cost": cost}
            results["total_inventory_cost"] += cost

        return results
