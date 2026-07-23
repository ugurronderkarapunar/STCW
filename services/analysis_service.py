"""
Main analysis service orchestrating file parsing, processing,
and providing data to the UI layer.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Optional, Dict, List, Tuple, Any
import logging

from utils.excel_parser import ExcelParser
from utils.data_processor import DataProcessor
from utils.config import STATUS_MAP, DOCUMENT_VALIDITY_MAP, DEFAULT_DOCUMENT_VALIDITY_DAYS

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
        self.reset()
        self.parser = ExcelParser(file_bytes=file_bytes)

        raw_df = self.parser.read_file()
        if raw_df.empty and self.parser.errors:
            self.errors.extend(self.parser.errors)
            return False

        if not self.parser.map_columns():
            self.errors.extend(self.parser.errors)
            self.warnings.extend(self.parser.warnings)
            return False

        self.warnings.extend(self.parser.warnings)

        mapped_df = self.parser.get_mapped_dataframe()
        if mapped_df.empty:
            self.errors.append("Veri eşleştirme başarısız.")
            return False

        self.processor = DataProcessor(mapped_df)
        self.processed_data = self.processor.process()

        if self.processed_data.empty:
            self.errors.extend(self.processor.errors)
            return False

        self.warnings.extend(self.processor.errors)
        self.warnings.extend(self.processor.warnings)

        self.personnel_summary = self.processor.create_personnel_summary()
        self.rank_summary = self.processor.create_rank_summary()
        self.document_summary = self.processor.get_document_type_summary()
        self.monthly_forecast = self.processor.get_monthly_expiry_forecast()

        self.file_loaded = True
        return True

    def reset(self):
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
        if self.parser and self.parser.column_map:
            return self.parser.column_map.copy()
        return {}

    def get_kpi_metrics(self) -> Dict[str, Any]:
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
        if self.processed_data is None:
            return pd.DataFrame()
        return self.processed_data["status_label"].value_counts().reset_index()

    def get_rank_risk(self) -> pd.DataFrame:
        if self.rank_summary is None:
            return pd.DataFrame()
        return self.rank_summary.copy()

    def get_personnel_risk(self) -> pd.DataFrame:
        if self.personnel_summary is None:
            return pd.DataFrame()
        return self.personnel_summary.head(20).copy()

    def get_filtered_data(
        self,
        rank_filter: Optional[List[str]] = None,
        status_filter: Optional[List[str]] = None,
        document_filter: Optional[List[str]] = None,
        personnel_search: Optional[str] = None,
        month_filter: Optional[int] = None,
        year_filter: Optional[int] = None,
        expiry_date_start: Optional[date] = None,
        expiry_date_end: Optional[date] = None,
    ) -> pd.DataFrame:
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
            df = df[df["expiry_date"].apply(lambda d: d.month == month_filter if d and pd.notna(d) else False)]
        if year_filter and "expiry_date" in df.columns:
            df = df[df["expiry_date"].apply(lambda d: d.year == year_filter if d and pd.notna(d) else False)]
        if "expiry_date" in df.columns:
            if expiry_date_start is not None:
                df = df[df["expiry_date"] >= expiry_date_start]
            if expiry_date_end is not None:
                df = df[df["expiry_date"] <= expiry_date_end]

        return df

    def get_filter_options(self) -> Dict[str, List[Any]]:
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
            ) if "expiry_date" in df.columns else [],
        }

    def update_document_dates(
        self,
        personnel_name: str,
        document_name: str,
        start_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
    ) -> bool:
        """
        Update the dates of a specific personnel document.
        Re-processes the data afterwards.
        """
        if self.processed_data is None:
            return False

        mask = (self.processed_data["personnel_name"] == personnel_name) & \
               (self.processed_data["document_name"] == document_name)

        if not mask.any():
            return False

        if expiry_date is not None:
            self.processed_data.loc[mask, "expiry_date"] = expiry_date
            self.processed_data.loc[mask, "expiry_date_raw"] = expiry_date.strftime("%d.%m.%Y")
        else:
            # If no expiry given but start_date provided, calculate it
            if start_date is not None:
                doc_lower = document_name.lower()
                validity_days = DEFAULT_DOCUMENT_VALIDITY_DAYS
                for key, days in DOCUMENT_VALIDITY_MAP.items():
                    if key in doc_lower:
                        validity_days = days
                        break
                calc_expiry = start_date + timedelta(days=validity_days)
                self.processed_data.loc[mask, "expiry_date"] = calc_expiry
                self.processed_data.loc[mask, "expiry_date_raw"] = calc_expiry.strftime("%d.%m.%Y")

        from utils.date_parser import calculate_remaining_days, classify_document
        today = date.today()
        for idx in self.processed_data[mask].index:
            new_expiry = self.processed_data.at[idx, "expiry_date"]
            rem = calculate_remaining_days(new_expiry, today)
            self.processed_data.at[idx, "remaining_days"] = rem
            new_status = classify_document(rem)
            self.processed_data.at[idx, "status"] = new_status
            self.processed_data.at[idx, "status_label"] = STATUS_MAP[new_status][1]
            self.processed_data.at[idx, "status_color"] = STATUS_MAP[new_status][2]
            self.processed_data.at[idx, "status_emoji"] = STATUS_MAP[new_status][0]

        # Re-create summaries
        self.personnel_summary = self.processor.create_personnel_summary()
        self.rank_summary = self.processor.create_rank_summary()
        self.document_summary = self.processor.get_document_type_summary()
        self.monthly_forecast = self.processor.get_monthly_expiry_forecast()

        return True
