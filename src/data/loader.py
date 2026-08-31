"""Data loader - ingest CSV, Excel, ERP exports."""

import pandas as pd
import os
from typing import Dict, List, Optional, Union, Any
from pathlib import Path


class DataLoader:
    """Load data from various sources."""

    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    def load_csv(
        self,
        file_path: str,
        parse_dates: Optional[List[str]] = None,
        dtype: Optional[Dict[str, str]] = None,
    ) -> pd.DataFrame:
        """
        Load CSV file.

        Args:
            file_path: Path to CSV file
            parse_dates: Columns to parse as dates
            dtype: Data types for columns

        Returns:
            Loaded DataFrame
        """
        full_path = os.path.join(self.base_path, file_path)
        return pd.read_csv(full_path, parse_dates=parse_dates, dtype=dtype)

    def load_excel(
        self,
        file_path: str,
        sheet_name: Union[str, int] = 0,
        parse_dates: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Load Excel file.

        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index
            parse_dates: Columns to parse as dates

        Returns:
            Loaded DataFrame
        """
        full_path = os.path.join(self.base_path, file_path)
        return pd.read_excel(full_path, sheet_name=sheet_name, parse_dates=parse_dates)

    def load_multiple_sheets(
        self,
        file_path: str,
        sheet_names: Optional[List[str]] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple sheets from Excel file.

        Args:
            file_path: Path to Excel file
            sheet_names: List of sheet names to load

        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        full_path = os.path.join(self.base_path, file_path)
        if sheet_names:
            return pd.read_excel(full_path, sheet_name=sheet_names)
        else:
            return pd.read_excel(full_path, sheet_name=None)

    def load_directory(
        self,
        directory: str,
        pattern: str = "*.csv",
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all matching files from a directory.

        Args:
            directory: Directory path
            pattern: File pattern (e.g., '*.csv')

        Returns:
            Dictionary mapping filenames to DataFrames
        """
        full_path = os.path.join(self.base_path, directory)
        files = Path(full_path).glob(pattern)
        
        data = {}
        for file_path in files:
            if file_path.suffix == ".csv":
                data[file_path.stem] = pd.read_csv(file_path)
            elif file_path.suffix in [".xlsx", ".xls"]:
                data[file_path.stem] = pd.read_excel(file_path)
        
        return data
