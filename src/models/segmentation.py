"""Segmentation models - ABC-XYZ classification, clustering."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, Any
from src.schemas.domain import ABCClassification, XYZClassification


class SegmentationModels:
    """Collection of segmentation and classification models."""

    @staticmethod
    def abc_classification(
        skus: pd.DataFrame,
        annual_spend_col: str = "annual_spend",
        a_threshold: float = 0.80,
        b_threshold: float = 0.95,
    ) -> pd.DataFrame:
        """
        ABC classification based on annual spend (Pareto analysis).

        Classic rule:
        - A items: 20% of SKUs, ~80% of value
        - B items: 30% of SKUs, ~15% of value
        - C items: 50% of SKUs, ~5% of value

        Args:
            skus: DataFrame with SKU data
            annual_spend_col: Column name for annual spend
            a_threshold: Cumulative spend threshold for A class
            b_threshold: Cumulative spend threshold for B class

        Returns:
            DataFrame with ABC classification
        """
        df = skus.copy().sort_values(annual_spend_col, ascending=False)
        df["cumulative_pct"] = (
            df[annual_spend_col].cumsum() / df[annual_spend_col].sum()
        )

        def classify_abc(pct):
            if pct <= a_threshold:
                return ABCClassification.A
            elif pct <= b_threshold:
                return ABCClassification.B
            else:
                return ABCClassification.C

        df["abc_class"] = df["cumulative_pct"].apply(classify_abc)
        return df

    @staticmethod
    def xyz_classification(
        skus: pd.DataFrame,
        cv_threshold_xy: float = 0.25,
        cv_threshold_yz: float = 1.0,
    ) -> pd.DataFrame:
        """
        XYZ classification based on demand variability (coefficient of variation).

        Coefficient of Variation (CV) = Standard Deviation / Mean
        - X (Predictable): CV < 0.25
        - Y (Moderate): 0.25 <= CV < 1.0
        - Z (Erratic): CV >= 1.0

        Args:
            skus: DataFrame with SKU data (must have demand history)
            cv_threshold_xy: CV threshold between X and Y
            cv_threshold_yz: CV threshold between Y and Z

        Returns:
            DataFrame with XYZ classification
        """
        if "demand_std_dev" not in skus.columns or "avg_demand" not in skus.columns:
            raise ValueError("DataFrame must contain 'demand_std_dev' and 'avg_demand' columns")

        df = skus.copy()
        df["cv"] = df["demand_std_dev"] / (df["avg_demand"] + 1e-6)  # Add small value to avoid division by zero

        def classify_xyz(cv):
            if cv < cv_threshold_xy:
                return XYZClassification.X
            elif cv < cv_threshold_yz:
                return XYZClassification.Y
            else:
                return XYZClassification.Z

        df["xyz_class"] = df["cv"].apply(classify_xyz)
        return df

    @staticmethod
    def abc_xyz_matrix(
        skus: pd.DataFrame,
        annual_spend_col: str = "annual_spend",
    ) -> pd.DataFrame:
        """
        Combined ABC-XYZ matrix for comprehensive SKU segmentation.

        Provides strategy recommendations:
        - AX: High value, stable -> Automated replenishment
        - AY, AZ: High value, variable -> Safety stock, close monitoring
        - BX, BZ: Medium value -> Standard controls
        - CX, CY, CZ: Low value -> Minimal controls, high safety stock

        Args:
            skus: DataFrame with SKU data
            annual_spend_col: Column name for annual spend

        Returns:
            DataFrame with ABC-XYZ classification and strategy
        """
        df = SegmentationModels.abc_classification(skus, annual_spend_col)
        df = SegmentationModels.xyz_classification(df)

        def strategy(row):
            abc = row["abc_class"]
            xyz = row["xyz_class"]
            key = f"{abc}{xyz}"

            strategies = {
                "AX": "Automated replenishment, low safety stock",
                "AY": "Regular monitoring, moderate safety stock",
                "AZ": "Close monitoring, high safety stock, dual sourcing",
                "BX": "Standard controls, low safety stock",
                "BY": "Standard controls, moderate safety stock",
                "BZ": "Periodic review, higher safety stock",
                "CX": "Minimal controls, occasional review",
                "CY": "Minimal controls, standard safety stock",
                "CZ": "Minimal controls, high safety stock, pool inventory",
            }
            return strategies.get(key, "Standard control")

        df["strategy"] = df.apply(strategy, axis=1)
        return df

    @staticmethod
    def fsn_classification(
        skus: pd.DataFrame,
        movement_col: str = "units_moved_last_year",
    ) -> pd.DataFrame:
        """
        FSN (Fast, Slow, Non-moving) classification based on movement.

        Args:
            skus: DataFrame with SKU data
            movement_col: Column name for movement metric

        Returns:
            DataFrame with FSN classification
        """
        df = skus.copy().sort_values(movement_col, ascending=False)
        df["cumulative_units"] = df[movement_col].cumsum() / df[movement_col].sum()

        def classify_fsn(cum_pct):
            if cum_pct <= 0.50:
                return "F"  # Fast
            elif cum_pct <= 0.80:
                return "S"  # Slow
            else:
                return "N"  # Non-moving

        df["fsn_class"] = df["cumulative_units"].apply(classify_fsn)
        return df
