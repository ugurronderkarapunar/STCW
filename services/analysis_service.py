"""
Main analysis service orchestrating file parsing, processing,
and providing data to the UI layer.
"""

import pandas as pd
import numpy as np
from datetime import date
from typing import Optional, Dict, List, Tuple, Any
import logging
import io

from utils.excel_parser import ExcelParser
from utils.data_processor import DataProcessor
from utils.config import STATUS_MAP

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Orchestrates the entire analysis pipeline.
    Acts as the main interface between UI and data processing.
    """

    def __init__(self):
        self.parser: Optional[ExcelParser] = None
        self.processor: Optional[DataProcessor] = None
        self.processed_data: Optional[pd.DataFrame] = None
        self.personnel_summary: Optional[pd.DataFrame] = None
        self.rank_summary: Optional[pd.DataFrame] = None
        self.document_summary: Optional[pd.DataFrame] = None
        self.monthly_forecast: Optional[pd.DataFrame] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.file_loaded: bool = False

    def load_file(self, file_bytes: bytes, filename: str) -> bool:
        """
        Load and process an uploaded file.

        Args:
            file_bytes: File content as bytes.
            filename: Original filename.

        Returns:
            bool: True if successful.
        """
        self.reset()
        self.parser = ExcelParser(file_bytes=file_bytes)

        # Read file
        raw_df = self.parser.read_file()
        if raw_df.empty and self.parser.errors:
            self.errors.extend(self.parser.errors)
            return False

        # Map columns
        if not self.parser.map_columns():
            self.errors.extend(self.parser.errors)
            self.warnings.extend(self.parser.warnings)
            return False

        self.warnings.extend(self.parser.warnings)

        # Get mapped data
        mapped_df = self.parser.get_mapped_dataframe()
        if mapped_df.empty:
            self.errors.append("Veri eşleştirme başarısız.")
            return False

        # Process data
        self.processor = DataProcessor(mapped_df)
        self.processed_data = self.processor.process()

        if self.processed_data.empty:
            self.errors.extend(self.processor.errors)
            return False

        self.warnings.extend(self.processor.errors)
        self.warnings.extend(self.processor.warnings)

        # Create summaries
        self.personnel_summary = self.processor.create_personnel_summary()
        self.rank_summary = self.processor.create_rank_summary()
        self.document_summary = self.processor.get_document_type_summary()
        self.monthly_forecast = self.processor.get_monthly_expiry_forecast()

        self.file_loaded = True
        return True

    def reset(self):
        """Reset all data."""
        self.parser = None
        self.processor = None
        self.processed_data = None
        self.personnel_summary = None
        self.rank_summary = None
        self.document_summary = None
        self.monthly_forecast = None
        self.errors = []
        self.warnings = []
        self.file_loaded = False

    def get_column_mapping_info(self) -> Dict[str, Optional[str]]:
        """Return the last used column mapping for UI display."""
        if self.parser and self.parser.column_map:
            return self.parser.column_map.copy()
        return {}

    def get_kpi_metrics(self) -> Dict[str, Any]:
        """
        Calculate KPI metrics for dashboard.

        Returns:
            dict: All KPI values.
        """
        if self.processed_data is None:
            return {}

        df = self.processed_data
        total_personnel = df["personnel_name"].nunique()
        total_ranks = df["rank_normalized"].nunique()
        total_documents = len(df)
        expired = (df["status"] == "EXPIRED").sum()
        critical = (df["status"] == "CRITICAL").sum()
        approaching = (df["status"] == "APPROACHING").sum()
        valid = (df["status"] == "VALID").sum()
        no_date = (df["status"] == "NO_DATE").sum()
        invalid_dates = df["is_invalid_date"].sum() if "is_invalid_date" in df.columns else 0

        return {
            "total_personnel": total_personnel,
            "total_ranks": total_ranks,
            "total_documents": total_documents,
            "expired": expired,
            "critical": critical,
            "approaching": approaching,
            "valid": valid,
            "no_date": no_date,
            "invalid_dates": invalid_dates,
        }

    def get_status_distribution(self) -> pd.DataFrame:
        """Get document count by status."""
        if self.processed_data is None:
            return pd.DataFrame()
        return self.processed_data["status_label"].value_counts().reset_index()

    def get_rank_risk(self) -> pd.DataFrame:
        """Get rank risk summary for charts."""
        if self.rank_summary is None:
            return pd.DataFrame()
        return self.rank_summary.copy()

    def get_personnel_risk(self) -> pd.DataFrame:
        """Get top risky personnel."""
        if self.personnel_summary is None:
            return pd.DataFrame()
        # Return top 20 most risky
        return self.personnel_summary.head(20).copy()

    def get_filtered_data(
        self,
        rank_filter: Optional[List[str]] = None,
        status_filter: Optional[List[str]] = None,
        document_filter: Optional[List[str]] = None,
        personnel_search: Optional[str] = None,
        month_filter: Optional[int] = None,
        year_filter: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Apply filters to processed data.
        """
        if self.processed_data is None:
            return pd.DataFrame()

        df = self.processed_data.copy()

        if rank_filter:
            df = df[df["rank_normalized"].isin(rank_filter)]

        if status_filter:
            df = df[df["status"].isin(status_filter)]

        if document_filter:
            df = df[df["document_name"].isin(document_filter)]

        if personnel_search:
            search_lower = personnel_search.lower()
            df = df[df["personnel_name"].str.lower().str.contains(search_lower, na=False)]

        if month_filter and "expiry_date" in df.columns:
            df = df[df["expiry_date"].apply(lambda d: d.month == month_filter if d else False)]

        if year_filter and "expiry_date" in df.columns:
            df = df[df["expiry_date"].apply(lambda d: d.year == year_filter if d else False)]

        return df

    def get_filter_options(self) -> Dict[str, List[Any]]:
        """
        Get available filter options from the data.
        """
        if self.processed_data is None:
            return {}

        df = self.processed_data
        return {
            "ranks": sorted(df["rank_normalized"].dropna().unique().tolist()),
            "statuses": sorted(df["status"].unique().tolist()),
            "documents": sorted(df["document_name"].dropna().unique().tolist()),
            "months": list(range(1, 13)),
            "years": sorted(
                df["expiry_date"].dropna().apply(lambda d: d.year).unique().tolist(),
                reverse=True
            ),
        }
