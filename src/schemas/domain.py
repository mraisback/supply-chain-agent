"""Supply chain domain entities and models."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ABCClassification(str, Enum):
    """ABC inventory classification."""
    A = "A"
    B = "B"
    C = "C"


class XYZClassification(str, Enum):
    """XYZ demand classification."""
    X = "X"  # Predictable, stable demand
    Y = "Y"  # Moderate variability
    Z = "Z"  # Erratic, unpredictable demand


@dataclass
class SKU:
    """Stock Keeping Unit."""
    sku_id: str
    description: str
    category: str
    unit_of_measure: str
    current_stock: float = 0.0
    abc_class: Optional[ABCClassification] = None
    xyz_class: Optional[XYZClassification] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Demand:
    """Historical or forecasted demand."""
    sku_id: str
    period: datetime
    quantity: float
    unit: str = "units"
    is_forecast: bool = False
    confidence_interval: Optional[tuple] = None  # (lower, upper)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Supplier:
    """Supplier entity."""
    supplier_id: str
    name: str
    location: str
    lead_time_days: int
    quality_score: float  # 0-100
    reliability_score: float  # 0-100
    cost_competitiveness: float  # 0-100
    is_dual_source: bool = False
    risk_level: str = "medium"  # low, medium, high
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Facility:
    """Distribution or warehouse facility."""
    facility_id: str
    name: str
    location: str
    latitude: float
    longitude: float
    capacity_units: float
    operating_cost_per_unit: float
    type: str = "warehouse"  # warehouse, distribution_center, plant
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransportationCost:
    """Transportation cost model."""
    origin_id: str
    destination_id: str
    cost_per_unit: float
    lead_time_days: int
    mode: str = "truck"  # truck, rail, ship, air
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InventoryPolicy:
    """Inventory control policy."""
    sku_id: str
    reorder_point: float
    reorder_quantity: float
    safety_stock: float
    service_level: float  # 0-1
    holding_cost_per_unit_per_year: float
    ordering_cost_per_order: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ForecastMetrics:
    """Forecast accuracy metrics."""
    sku_id: str
    period: str  # weekly, monthly, etc.
    mape: float  # Mean Absolute Percentage Error
    wmape: float  # Weighted MAPE
    mad: float  # Mean Absolute Deviation
    rmse: float  # Root Mean Squared Error
    bias: float  # Forecast bias
    fva: float  # Forecast Value Added
    metadata: Dict[str, Any] = field(default_factory=dict)
