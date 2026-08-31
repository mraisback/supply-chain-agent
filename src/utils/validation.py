"""Input validation utilities."""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re


class ValidationError(Exception):
    """Validation error."""
    pass


class Validator:
    """Data and parameter validation."""

    @staticmethod
    def validate_sku_id(sku_id: str) -> bool:
        """
        Validate SKU ID format.

        Args:
            sku_id: SKU identifier

        Returns:
            True if valid
        """
        if not isinstance(sku_id, str) or len(sku_id) == 0:
            raise ValidationError("SKU ID must be a non-empty string")
        return True

    @staticmethod
    def validate_positive_number(value: Union[int, float], name: str = "value") -> bool:
        """
        Validate positive number.

        Args:
            value: Number to validate
            name: Field name for error message

        Returns:
            True if valid
        """
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValidationError(f"{name} must be a positive number, got {value}")
        return True

    @staticmethod
    def validate_percentage(value: float, name: str = "percentage") -> bool:
        """
        Validate percentage (0-1 or 0-100).

        Args:
            value: Percentage value
            name: Field name for error message

        Returns:
            True if valid
        """
        if not isinstance(value, (int, float)) or value < 0:
            raise ValidationError(f"{name} must be non-negative, got {value}")
        # Normalize to 0-1 if > 1
        if value > 1:
            value = value / 100
        if value > 1:
            raise ValidationError(f"{name} must be between 0 and 1, got {value}")
        return True

    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """
        Validate date string.

        Args:
            date_str: Date string
            format: Expected date format

        Returns:
            True if valid
        """
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError as e:
            raise ValidationError(f"Invalid date format: {date_str} (expected {format})")

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address.

        Args:
            email: Email address

        Returns:
            True if valid
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ValidationError(f"Invalid email address: {email}")
        return True

    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required: List[str]) -> bool:
        """
        Validate that required fields are present.

        Args:
            data: Data dictionary
            required: List of required field names

        Returns:
            True if all required fields present
        """
        missing = [field for field in required if field not in data or data[field] is None]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")
        return True
