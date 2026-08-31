"""Forecasting models - ARIMA, Prophet, ML-based approaches."""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, Any
from datetime import datetime, timedelta


class ForecastingModels:
    """Collection of forecasting models for demand planning."""

    @staticmethod
    def simple_moving_average(data: pd.Series, periods: int = 12) -> pd.Series:
        """
        Simple Moving Average (SMA) forecast.

        Args:
            data: Historical demand series
            periods: Number of periods for moving average

        Returns:
            Forecasted values
        """
        return data.rolling(window=periods).mean()

    @staticmethod
    def exponential_smoothing(data: pd.Series, alpha: float = 0.3) -> pd.Series:
        """
        Exponential Smoothing forecast.

        Args:
            data: Historical demand series
            alpha: Smoothing parameter (0-1)

        Returns:
            Forecasted values
        """
        result = [data.iloc[0]]
        for i in range(1, len(data)):
            result.append(alpha * data.iloc[i] + (1 - alpha) * result[-1])
        return pd.Series(result, index=data.index)

    @staticmethod
    def calculate_mape(actual: pd.Series, predicted: pd.Series) -> float:
        """
        Calculate Mean Absolute Percentage Error.

        Args:
            actual: Actual values
            predicted: Predicted values

        Returns:
            MAPE as percentage
        """
        mask = actual != 0
        return (np.abs((actual[mask] - predicted[mask]) / actual[mask]).mean()) * 100

    @staticmethod
    def calculate_wmape(
        actual: pd.Series, predicted: pd.Series, weights: Optional[pd.Series] = None
    ) -> float:
        """
        Calculate Weighted Mean Absolute Percentage Error.

        Args:
            actual: Actual values
            predicted: Predicted values
            weights: Optional weights for each observation

        Returns:
            WMAPE as percentage
        """
        if weights is None:
            weights = pd.Series(1.0, index=actual.index)
        
        mask = actual != 0
        numerator = (weights[mask] * np.abs(actual[mask] - predicted[mask])).sum()
        denominator = (weights[mask] * actual[mask]).sum()
        
        return (numerator / denominator) * 100 if denominator != 0 else 0

    @staticmethod
    def calculate_mad(actual: pd.Series, predicted: pd.Series) -> float:
        """
        Calculate Mean Absolute Deviation.

        Args:
            actual: Actual values
            predicted: Predicted values

        Returns:
            MAD
        """
        return np.abs(actual - predicted).mean()

    @staticmethod
    def calculate_forecast_bias(actual: pd.Series, predicted: pd.Series) -> float:
        """
        Calculate forecast bias (systematic over/under forecasting).

        Args:
            actual: Actual values
            predicted: Predicted values

        Returns:
            Bias (negative = underfcasting, positive = overforecasting)
        """
        return (predicted - actual).mean()

    @staticmethod
    def detect_demand_shocks(data: pd.Series, threshold: float = 2.0) -> pd.DataFrame:
        """
        Detect anomalous demand patterns using statistical methods.

        Args:
            data: Historical demand series
            threshold: Standard deviation threshold for anomaly detection

        Returns:
            DataFrame with anomaly flags
        """
        mean = data.mean()
        std = data.std()
        
        lower_bound = mean - (threshold * std)
        upper_bound = mean + (threshold * std)
        
        is_anomaly = (data < lower_bound) | (data > upper_bound)
        
        return pd.DataFrame({
            "date": data.index,
            "demand": data.values,
            "is_anomaly": is_anomaly.values,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        })

    @staticmethod
    def forecast_with_seasonality(
        data: pd.Series, seasonal_periods: int = 12, forecast_horizon: int = 12
    ) -> Dict[str, Any]:
        """
        Forecast demand with seasonal adjustment.

        Args:
            data: Historical demand series
            seasonal_periods: Number of periods in seasonal cycle
            forecast_horizon: Number of periods to forecast

        Returns:
            Dictionary with forecast and metrics
        """
        # Detrend and deseasonal
        trend = data.rolling(window=seasonal_periods).mean()
        detrended = data - trend
        seasonal = detrended.rolling(window=seasonal_periods).mean()
        
        # Forecast using simple exponential smoothing on deseasonalized data
        deseasonalized = detrended - seasonal
        forecast_deseas = ForecastingModels.exponential_smoothing(deseasonalized, alpha=0.3)
        
        # Reapply seasonal component
        forecast = forecast_deseas + seasonal.iloc[-1]
        
        return {
            "forecast": forecast,
            "trend": trend,
            "seasonal": seasonal,
            "forecast_horizon": forecast_horizon,
        }

    @staticmethod
    def intermittent_demand_forecast(data: pd.Series, method: str = "croston") -> Dict[str, Any]:
        """
        Forecast intermittent demand (high variability, many zeros).

        Args:
            data: Historical demand series
            method: Forecasting method ("croston" or "simple_average")

        Returns:
            Dictionary with forecast and metadata
        """
        # Identify demand occurrences
        occurrences = (data > 0).astype(int)
        occurrence_rate = occurrences.sum() / len(data)
        
        if method == "croston":
            # Croston's method for intermittent demand
            non_zero_demands = data[data > 0]
            avg_demand = non_zero_demands.mean() if len(non_zero_demands) > 0 else 0
            avg_inter_arrival = len(data) / occurrences.sum() if occurrences.sum() > 0 else len(data)
            
            forecast = avg_demand / avg_inter_arrival
        else:
            # Simple average method
            forecast = data.mean()
        
        return {
            "forecast": forecast,
            "occurrence_rate": occurrence_rate,
            "method": method,
        }
