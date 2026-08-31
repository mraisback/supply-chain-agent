"""Risk models - supply chain risk mapping, resilience analysis."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta


class RiskModels:
    """Collection of risk assessment and resilience models."""

    @staticmethod
    def supplier_risk_score(
        quality_score: float,
        reliability_score: float,
        cost_competitiveness: float,
        geographic_concentration: float,
        single_source_dependency: bool = False,
    ) -> Dict[str, float]:
        """
        Calculate overall supplier risk score.

        Combines multiple risk factors:
        - Quality risk (inverse of quality score)
        - Reliability risk (inverse of reliability)
        - Cost risk (inverse of competitiveness)
        - Concentration risk (geographic)
        - Single-source risk

        Args:
            quality_score: Quality metric (0-100)
            reliability_score: Reliability metric (0-100)
            cost_competitiveness: Cost metric (0-100)
            geographic_concentration: Geographic risk (0-1)
            single_source_dependency: Whether this is a single-source supplier

        Returns:
            Dictionary with risk metrics
        """
        # Normalize scores to 0-1 range (lower is better)
        quality_risk = (100 - quality_score) / 100
        reliability_risk = (100 - reliability_score) / 100
        cost_risk = (100 - cost_competitiveness) / 100

        # Weights for risk factors
        weights = {
            "quality": 0.35,
            "reliability": 0.35,
            "cost": 0.15,
            "concentration": 0.10,
            "single_source": 0.05,
        }

        # Calculate composite risk
        base_risk = (
            weights["quality"] * quality_risk
            + weights["reliability"] * reliability_risk
            + weights["cost"] * cost_risk
            + weights["concentration"] * geographic_concentration
        )

        if single_source_dependency:
            base_risk += weights["single_source"]

        return {
            "overall_risk_score": min(base_risk, 1.0),
            "quality_risk": quality_risk,
            "reliability_risk": reliability_risk,
            "cost_risk": cost_risk,
            "concentration_risk": geographic_concentration,
            "single_source_dependency": single_source_dependency,
            "risk_level": "high" if base_risk > 0.7 else ("medium" if base_risk > 0.4 else "low"),
        }

    @staticmethod
    def bullwhip_effect_analysis(
        upstream_order_variance: float,
        downstream_demand_variance: float,
    ) -> Dict[str, float]:
        """
        Quantify the bullwhip effect (demand amplification up the supply chain).

        Bullwhip Effect = Variance of Orders / Variance of Demand
        A ratio > 1 indicates demand amplification.

        Args:
            upstream_order_variance: Variance of orders placed upstream
            downstream_demand_variance: Variance of customer demand

        Returns:
            Dictionary with bullwhip metrics
        """
        if downstream_demand_variance == 0:
            bullwhip_ratio = 0
        else:
            bullwhip_ratio = upstream_order_variance / downstream_demand_variance

        return {
            "bullwhip_ratio": bullwhip_ratio,
            "demand_amplification": (bullwhip_ratio - 1) * 100,  # % increase
            "severity": "high" if bullwhip_ratio > 2 else ("moderate" if bullwhip_ratio > 1.5 else "low"),
            "mitigation_needed": bullwhip_ratio > 1.2,
        }

    @staticmethod
    def dual_sourcing_economics(
        single_source_cost: float,
        dual_source_cost_increase_pct: float,
        disruption_probability: float,
        disruption_impact_days: float,
        daily_revenue_loss: float,
    ) -> Dict[str, float]:
        """
        Economic analysis of dual-sourcing vs. single-sourcing.

        Compares:
        - Additional cost of dual sourcing
        - Expected cost of disruption under single source

        Args:
            single_source_cost: Annual cost with single source
            dual_source_cost_increase_pct: % cost increase for dual source
            disruption_probability: Probability of disruption (0-1)
            disruption_impact_days: Days of disruption
            daily_revenue_loss: Revenue loss per day of disruption

        Returns:
            Dictionary with economic analysis
        """
        # Dual sourcing cost
        dual_source_cost = single_source_cost * (1 + dual_source_cost_increase_pct / 100)
        incremental_cost = dual_source_cost - single_source_cost

        # Expected disruption cost
        expected_disruption_cost = (
            disruption_probability * disruption_impact_days * daily_revenue_loss
        )

        # Break-even analysis
        breakeven_probability = incremental_cost / (disruption_impact_days * daily_revenue_loss) if daily_revenue_loss > 0 else 0

        return {
            "annual_dual_sourcing_cost": dual_source_cost,
            "annual_incremental_cost": incremental_cost,
            "expected_disruption_cost": expected_disruption_cost,
            "net_benefit": expected_disruption_cost - incremental_cost,
            "dual_sourcing_recommended": expected_disruption_cost > incremental_cost,
            "breakeven_disruption_probability": breakeven_probability,
        }

    @staticmethod
    def supply_chain_resilience_score(
        suppliers: pd.DataFrame,
        network_redundancy: float,
        inventory_buffer_days: float,
        supplier_diversity_index: float,
    ) -> Dict[str, Any]:
        """
        Calculate overall supply chain resilience score.

        Combines:
        - Supplier reliability scores
        - Network redundancy
        - Inventory buffers
        - Supplier diversity

        Args:
            suppliers: DataFrame with supplier risk scores
            network_redundancy: Network redundancy level (0-1)
            inventory_buffer_days: Days of inventory buffer
            supplier_diversity_index: Herfindahl-Hirschman Index (0-1, lower=more diverse)

        Returns:
            Dictionary with resilience metrics
        """
        # Supplier reliability (inverse of risk)
        avg_supplier_risk = suppliers["risk_score"].mean() if "risk_score" in suppliers.columns else 0.5
        supplier_reliability = 1 - avg_supplier_risk

        # Inventory buffer score (normalized)
        buffer_score = min(inventory_buffer_days / 30, 1.0)  # 30 days = max score

        # Network redundancy score
        redundancy_score = network_redundancy

        # Supplier diversity score
        diversity_score = 1 - supplier_diversity_index

        # Composite resilience score
        weights = {
            "supplier_reliability": 0.35,
            "buffer": 0.25,
            "redundancy": 0.25,
            "diversity": 0.15,
        }

        resilience_score = (
            weights["supplier_reliability"] * supplier_reliability
            + weights["buffer"] * buffer_score
            + weights["redundancy"] * redundancy_score
            + weights["diversity"] * diversity_score
        )

        return {
            "overall_resilience_score": resilience_score,
            "resilience_level": "high" if resilience_score > 0.7 else ("medium" if resilience_score > 0.4 else "low"),
            "supplier_reliability_score": supplier_reliability,
            "inventory_buffer_score": buffer_score,
            "network_redundancy_score": redundancy_score,
            "supplier_diversity_score": diversity_score,
        }
