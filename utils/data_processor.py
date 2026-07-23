"""
Data processing module for document tracking.
Handles date parsing, document classification, and personnel aggregation.
Uses vectorized operations for performance with 100k+ rows.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Optional, Dict, List, Tuple
import logging

from utils.date_parser import (
    parse_date_series,
    calculate_remaining_days,
    classify_document,
)
from utils.config import STATUS_MAP, KNOWN_RANKS

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Processes raw mapped data into analysis-ready format.
    Handles date parsing, classification, and aggregation.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with mapped DataFrame.

        Args:
            df: DataFrame with columns: personnel_name, rank_title,
                document_name, expiry_date_raw
        """
        self.raw_df = df.copy() if not df.empty else pd.DataFrame()
        self.processed_df: Optional[pd.DataFrame] = None
        self.personnel_summary: Optional[pd.DataFrame] = None
        self.rank_summary: Optional[pd.DataFrame] = None
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def process(self) -> pd.DataFrame:
        """
        Main processing pipeline:
        1. Parse dates
        2. Calculate remaining days
        3. Classify documents
        4. Normalize ranks

        Returns:
            pd.DataFrame: Fully processed DataFrame.
        """
        if self.raw_df.empty:
            self.errors.append("İşlenecek veri bulunamadı.")
            return pd.DataFrame()

        df = self.raw_df.copy()

        # Step 1: Parse dates
        if "expiry_date_raw" in df.columns:
            date_series = df["expiry_date_raw"].apply(
                lambda x: x if x is not None and str(x).strip() else None
            )
            df["expiry_date"] = parse_date_series(date_series.astype(str).replace('None', np.nan))
        else:
            df["expiry_date"] = None

        # Step 2: Calculate remaining days
        today = date.today()
        df["remaining_days"] = df["expiry_date"].apply(
            lambda d: calculate_remaining_days(d, today)
        )

        # Step 3: Classify documents
        df["status"] = df["remaining_days"].apply(classify_document)

        # Add status labels and colors
        df["status_emoji"] = df["status"].map(lambda s: STATUS_MAP.get(s, ("", "", ""))[0])
        df["status_label"] = df["status"].map(lambda s: STATUS_MAP.get(s, ("", "", ""))[1])
        df["status_color"] = df["status"].map(lambda s: STATUS_MAP.get(s, ("", "", ""))[2])

        # Step 4: Normalize rank titles
        df["rank_normalized"] = df["rank_title"].apply(self._normalize_rank)

        # Step 5: Flag invalid/historical dates
        df["is_invalid_date"] = False
        mask = df["expiry_date"].notna()
        df.loc[mask, "is_invalid_date"] = df.loc[mask, "expiry_date"].apply(
            lambda d: self._check_invalid_date(d, today)
        )

        self.processed_df = df
        return df

    def _normalize_rank(self, rank: Optional[str]) -> Optional[str]:
        """
        Normalize rank title to known values.

        Args:
            rank: Raw rank string.

        Returns:
            str: Normalized rank or original if no match.
        """
        if rank is None or pd.isna(rank) if isinstance(rank, float) else False:
            return "Belirtilmemiş"

        rank_str = str(rank).strip().title()

        # Direct match
        for known_rank in KNOWN_RANKS:
            if rank_str.lower() == known_rank.lower():
                return known_rank

        # Partial match
        for known_rank in KNOWN_RANKS:
            if known_rank.lower() in rank_str.lower() or rank_str.lower() in known_rank.lower():
                return known_rank

        return rank_str if rank_str else "Belirtilmemiş"

    def _check_invalid_date(self, expiry_date: date, today: date) -> bool:
        """
        Check if date seems invalid (e.g., past date older than 10 years).

        Args:
            expiry_date: The parsed expiry date.
            today: Reference date.

        Returns:
            bool: True if date is likely invalid.
        """
        if expiry_date is None:
            return False
        # Dates more than 20 years in the past might be data entry errors
        if expiry_date < today - timedelta(days=365 * 20):
            return True
        # Dates more than 50 years in the future might be errors
        if expiry_date > today + timedelta(days=365 * 50):
            return True
        return False

    def create_personnel_summary(self) -> pd.DataFrame:
        """
        Aggregate documents per personnel.
        Each row = one personnel with all their documents summarized.

        Returns:
            pd.DataFrame: Personnel summary.
        """
        if self.processed_df is None or self.processed_df.empty:
            return pd.DataFrame()

        df = self.processed_df

        # Group by personnel name and rank
        personnel_groups = df.groupby(["personnel_name", "rank_normalized"], dropna=False)

        summary_list = []
        for (name, rank), group in personnel_groups:
            total_docs = len(group)
            expired = (group["status"] == "EXPIRED").sum()
            critical = (group["status"] == "CRITICAL").sum()
            approaching = (group["status"] == "APPROACHING").sum()
            valid = (group["status"] == "VALID").sum()
            no_date = (group["status"] == "NO_DATE").sum()

            # Collect document details
            expired_docs = group[group["status"] == "EXPIRED"]["document_name"].tolist()
            critical_docs = group[group["status"] == "CRITICAL"]["document_name"].tolist()
            approaching_docs = group[group["status"] == "APPROACHING"]["document_name"].tolist()

            # Worst status
            if expired > 0:
                worst_status = "EXPIRED"
            elif critical > 0:
                worst_status = "CRITICAL"
            elif approaching > 0:
                worst_status = "APPROACHING"
            elif valid > 0:
                worst_status = "VALID"
            else:
                worst_status = "NO_DATE"

            # Max overdue days (most negative remaining_days)
            remaining_values = group["remaining_days"].dropna()
            max_overdue = abs(remaining_values.min()) if not remaining_values.empty and remaining_values.min() < 0 else 0

            summary_list.append({
                "personnel_name": name,
                "rank_title": rank,
                "total_documents": total_docs,
                "expired_count": expired,
                "critical_count": critical,
                "approaching_count": approaching,
                "valid_count": valid,
                "no_date_count": no_date,
                "worst_status": worst_status,
                "max_overdue_days": int(max_overdue),
                "expired_documents": ", ".join(expired_docs) if expired_docs else "",
                "critical_documents": ", ".join(critical_docs) if critical_docs else "",
                "approaching_documents": ", ".join(approaching_docs) if approaching_docs else "",
            })

        self.personnel_summary = pd.DataFrame(summary_list)

        # Sort by risk (worst first)
        if not self.personnel_summary.empty:
            status_order = {"EXPIRED": 0, "CRITICAL": 1, "APPROACHING": 2, "VALID": 3, "NO_DATE": 4}
            self.personnel_summary["_sort"] = self.personnel_summary["worst_status"].map(status_order)
            self.personnel_summary = self.personnel_summary.sort_values(
                ["_sort", "max_overdue_days"],
                ascending=[True, False]
            ).drop(columns=["_sort"]).reset_index(drop=True)

        return self.personnel_summary

    def create_rank_summary(self) -> pd.DataFrame:
        """
        Aggregate data by rank/title.

        Returns:
            pd.DataFrame: Rank summary with counts and risk metrics.
        """
        if self.processed_df is None or self.processed_df.empty:
            return pd.DataFrame()

        df = self.processed_df

        rank_groups = df.groupby("rank_normalized", dropna=False)

        rank_data = []
        for rank, group in rank_groups:
            unique_personnel = group["personnel_name"].nunique()
            total_docs = len(group)
            expired = (group["status"] == "EXPIRED").sum()
            critical = (group["status"] == "CRITICAL").sum()
            approaching = (group["status"] == "APPROACHING").sum()
            valid = (group["status"] == "VALID").sum()
            no_date = (group["status"] == "NO_DATE").sum()

            avg_remaining = group["remaining_days"].dropna().mean()
            risk_score = expired * 3 + critical * 2 + approaching * 1

            rank_data.append({
                "rank_title": rank if rank and str(rank) != "nan" else "Belirtilmemiş",
                "personnel_count": unique_personnel,
                "total_documents": total_docs,
                "expired_count": expired,
                "critical_count": critical,
                "approaching_count": approaching,
                "valid_count": valid,
                "no_date_count": no_date,
                "avg_remaining_days": round(avg_remaining, 1) if not pd.isna(avg_remaining) else None,
                "risk_score": risk_score,
            })

        self.rank_summary = pd.DataFrame(rank_data)
        if not self.rank_summary.empty:
            self.rank_summary = self.rank_summary.sort_values("risk_score", ascending=False).reset_index(drop=True)

        return self.rank_summary

    def get_document_type_summary(self) -> pd.DataFrame:
        """
        Summarize by document type.

        Returns:
            pd.DataFrame: Document type summary.
        """
        if self.processed_df is None or self.processed_df.empty:
            return pd.DataFrame()

        df = self.processed_df
        doc_groups = df.groupby("document_name", dropna=False)

        doc_data = []
        for doc_name, group in doc_groups:
            doc_data.append({
                "document_name": doc_name if doc_name and str(doc_name) != "nan" else "Bilinmiyor",
                "total_count": len(group),
                "expired_count": (group["status"] == "EXPIRED").sum(),
                "critical_count": (group["status"] == "CRITICAL").sum(),
                "approaching_count": (group["status"] == "APPROACHING").sum(),
                "valid_count": (group["status"] == "VALID").sum(),
            })

        doc_summary = pd.DataFrame(doc_data)
        if not doc_summary.empty:
            doc_summary = doc_summary.sort_values("total_count", ascending=False).reset_index(drop=True)

        return doc_summary

    def get_monthly_expiry_forecast(self) -> pd.DataFrame:
        """
        Forecast document expirations by month.

        Returns:
            pd.DataFrame: Monthly expiry counts.
        """
        if self.processed_df is None or self.processed_df.empty:
            return pd.DataFrame()

        df = self.processed_df[self.processed_df["expiry_date"].notna()].copy()

        if df.empty:
            return pd.DataFrame()

        today = date.today()
        df["expiry_month"] = df["expiry_date"].apply(lambda d: d.replace(day=1) if d else None)

        # Filter for next 12 months
        twelve_months = today + timedelta(days=365)
        df = df[
            (df["expiry_date"] >= today.replace(day=1)) &
            (df["expiry_date"] <= twelve_months)
        ]

        monthly = df.groupby("expiry_month").size().reset_index(name="count")
        monthly.columns = ["month", "expiring_count"]
        monthly = monthly.sort_values("month")

        monthly["month_label"] = monthly["month"].apply(
            lambda d: d.strftime("%B %Y") if d else ""
        )

        return monthly
