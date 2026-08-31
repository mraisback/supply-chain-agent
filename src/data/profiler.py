"""Data profiler - data quality assessment."""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class DataProfiler:
    """Profile and assess data quality."""

    @staticmethod
    def profile(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive data profile.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with profiling results
        """
        profile = {
            "shape": df.shape,
            "columns": len(df.columns),
            "rows": len(df),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 ** 2),
            "column_details": {},
            "missing_data": {},
            "duplicates": df.duplicated().sum(),
            "data_types": df.dtypes.to_dict(),
        }

        # Column-level profiling
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_pct = (missing_count / len(df)) * 100

            col_profile = {
                "dtype": str(df[col].dtype),
                "missing_count": missing_count,
                "missing_pct": missing_pct,
                "unique_values": df[col].nunique(),
            }

            # Numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                col_profile.update({
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "mean": df[col].mean(),
                    "std": df[col].std(),
                    "median": df[col].median(),
                })

            # Categorical columns
            elif pd.api.types.is_object_dtype(df[col]):
                col_profile["top_5_values"] = df[col].value_counts().head(5).to_dict()

            profile["column_details"][col] = col_profile
            profile["missing_data"][col] = missing_pct

        return profile

    @staticmethod
    def quality_report(df: pd.DataFrame) -> str:
        """
        Generate human-readable data quality report.

        Args:
            df: Input DataFrame

        Returns:
            Report as string
        """
        profile = DataProfiler.profile(df)

        report = f"""
        DATA QUALITY REPORT
        {'=' * 50}
        
        Shape: {profile['shape'][0]} rows × {profile['shape'][1]} columns
        Memory: {profile['memory_usage_mb']:.2f} MB
        Duplicates: {profile['duplicates']} rows
        
        MISSING DATA:
        {'-' * 50}
        """

        for col, missing_pct in profile["missing_data"].items():
            if missing_pct > 0:
                report += f"  {col}: {missing_pct:.1f}%\n"

        report += f"""
        DATA TYPES:
        {'-' * 50}
        """

        for col, dtype in profile["data_types"].items():
            report += f"  {col}: {dtype}\n"

        return report

    @staticmethod
    def identify_outliers(
        df: pd.DataFrame,
        column: str,
        method: str = "iqr",
        threshold: float = 1.5,
    ) -> pd.DataFrame:
        """
        Identify outliers in a column.

        Args:
            df: Input DataFrame
            column: Column to check
            method: "iqr" (interquartile range) or "zscore"
            threshold: Threshold for outlier detection

        Returns:
            DataFrame with outlier flag
        """
        result = df.copy()

        if method == "iqr":
            Q1 = result[column].quantile(0.25)
            Q3 = result[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - (threshold * IQR)
            upper_bound = Q3 + (threshold * IQR)
            result["is_outlier"] = (
                (result[column] < lower_bound) | (result[column] > upper_bound)
            )
        elif method == "zscore":
            mean = result[column].mean()
            std = result[column].std()
            result["is_outlier"] = np.abs((result[column] - mean) / std) > threshold

        return result
