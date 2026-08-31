"""Data transformer - ETL, cleaning, normalization."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


class DataTransformer:
    """Transform and clean data."""

    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        strategy: str = "drop",
        value: Optional[Any] = None,
        columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Handle missing values.

        Args:
            df: Input DataFrame
            strategy: Strategy - "drop", "forward_fill", "backward_fill", "value"
            value: Value to fill if strategy is "value"
            columns: Specific columns to apply to

        Returns:
            Cleaned DataFrame
        """
        result = df.copy()
        target_cols = columns or result.columns

        if strategy == "drop":
            result = result.dropna(subset=target_cols)
        elif strategy == "forward_fill":
            result[target_cols] = result[target_cols].fillna(method="ffill")
        elif strategy == "backward_fill":
            result[target_cols] = result[target_cols].fillna(method="bfill")
        elif strategy == "value" and value is not None:
            result[target_cols] = result[target_cols].fillna(value)

        return result

    @staticmethod
    def remove_duplicates(
        df: pd.DataFrame,
        subset: Optional[List[str]] = None,
        keep: str = "first",
    ) -> pd.DataFrame:
        """
        Remove duplicate rows.

        Args:
            df: Input DataFrame
            subset: Columns to consider for duplicates
            keep: Which duplicates to keep - "first", "last", False

        Returns:
            DataFrame with duplicates removed
        """
        return df.drop_duplicates(subset=subset, keep=keep)

    @staticmethod
    def normalize_column(
        df: pd.DataFrame,
        column: str,
        method: str = "minmax",
    ) -> pd.DataFrame:
        """
        Normalize a column.

        Args:
            df: Input DataFrame
            column: Column to normalize
            method: "minmax" (0-1) or "zscore" (std normalized)

        Returns:
            DataFrame with normalized column
        """
        result = df.copy()
        
        if method == "minmax":
            min_val = result[column].min()
            max_val = result[column].max()
            result[column] = (result[column] - min_val) / (max_val - min_val)
        elif method == "zscore":
            mean_val = result[column].mean()
            std_val = result[column].std()
            result[column] = (result[column] - mean_val) / std_val
        
        return result

    @staticmethod
    def parse_dates(
        df: pd.DataFrame,
        columns: Optional[List[str]] = None,
        format: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Parse date columns.

        Args:
            df: Input DataFrame
            columns: Columns to parse
            format: Date format string

        Returns:
            DataFrame with parsed dates
        """
        result = df.copy()
        target_cols = columns or result.select_dtypes(include=["object"]).columns
        
        for col in target_cols:
            try:
                result[col] = pd.to_datetime(result[col], format=format)
            except:
                pass  # Skip if parsing fails
        
        return result

    @staticmethod
    def aggregate_by_period(
        df: pd.DataFrame,
        date_column: str,
        period: str = "M",
        agg_dict: Optional[Dict[str, str]] = None,
    ) -> pd.DataFrame:
        """
        Aggregate data by time period.

        Args:
            df: Input DataFrame
            date_column: Date column name
            period: Period string - "D" (day), "W" (week), "M" (month), "Q" (quarter), "Y" (year)
            agg_dict: Aggregation dictionary

        Returns:
            Aggregated DataFrame
        """
        result = df.copy()
        result[date_column] = pd.to_datetime(result[date_column])
        
        if agg_dict is None:
            agg_dict = {col: "sum" for col in result.select_dtypes(include=[np.number]).columns}
        
        return result.groupby(pd.Grouper(key=date_column, freq=period)).agg(agg_dict)

    @staticmethod
    def pivot_data(
        df: pd.DataFrame,
        index: str,
        columns: str,
        values: str,
        aggfunc: str = "sum",
    ) -> pd.DataFrame:
        """
        Pivot table transformation.

        Args:
            df: Input DataFrame
            index: Row index
            columns: Column headers
            values: Values to aggregate
            aggfunc: Aggregation function

        Returns:
            Pivoted DataFrame
        """
        return df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc)

    @staticmethod
    def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names (lowercase, replace spaces with underscores).

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with standardized column names
        """
        result = df.copy()
        result.columns = result.columns.str.lower().str.replace(" ", "_")
        return result
