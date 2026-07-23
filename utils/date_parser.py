"""
Robust date parser for handling multiple date formats.
Uses vectorized operations for performance.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from dateutil import parser as dateutil_parser
from typing import Optional, Union, List, Tuple
import re
import logging

logger = logging.getLogger(__name__)

# Pre-compiled regex patterns for common date formats
DATE_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$"), "%d.%m.%Y"),
    (re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$"), "%d/%m/%Y"),
    (re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$"), "%Y-%m-%d"),
    (re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$"), "%m/%d/%Y"),
    (re.compile(r"^(\d{1,2})-(\d{1,2})-(\d{4})$"), "%d-%m-%Y"),
    (re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})$"), "%Y/%m/%d"),
    (re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{2})$"), "%d.%m.%y"),
    (re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{2})$"), "%d/%m/%y"),
]


def parse_single_date(value: any) -> Optional[date]:
    """
    Parse a single value to a date object.
    Handles strings, datetime objects, timestamps, and numeric Excel dates.

    Args:
        value: Input value to parse.

    Returns:
        Optional[date]: Parsed date or None if unparseable.
    """
    if value is None:
        return None

    if pd.isna(value) if hasattr(value, '__iter__') is False and not isinstance(value, str) else False:
        # Check for NaN more carefully
        try:
            if isinstance(value, float) and np.isnan(value):
                return None
        except (TypeError, ValueError):
            pass

    # Already a date/datetime
    if isinstance(value, (date, datetime)):
        return value.date() if isinstance(value, datetime) else value

    # Pandas Timestamp
    if isinstance(value, pd.Timestamp):
        return value.date()

    # Numeric (Excel serial date)
    if isinstance(value, (int, float)):
        if not np.isnan(value) and 1 < value < 100000:
            try:
                from datetime import timedelta
                excel_epoch = date(1899, 12, 30)
                return (excel_epoch + timedelta(days=int(value))).date()
            except (ValueError, OverflowError):
                pass

    # String parsing
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

        # Try regex-based patterns first (fast)
        for pattern, fmt in DATE_PATTERNS:
            match = pattern.match(value)
            if match:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

        # Try pandas to_datetime
        try:
            parsed = pd.to_datetime(value, errors='coerce', dayfirst=True)
            if not pd.isna(parsed):
                return parsed.date()
        except Exception:
            pass

        # Try dateutil as last resort
        try:
            return dateutil_parser.parse(value, dayfirst=True).date()
        except (ValueError, OverflowError, TypeError):
            pass

    return None


def parse_date_series(series: pd.Series) -> pd.Series:
    """
    Vectorized date parsing for an entire pandas Series.
    Falls back to element-wise parsing for mixed formats.

    Args:
        series: Pandas Series containing date values.

    Returns:
        pd.Series: Series of date objects (with NaT for unparseable values).
    """
    if series.empty:
        return pd.Series(dtype='object')

    # First attempt: direct pd.to_datetime with dayfirst
    parsed = pd.to_datetime(series, errors='coerce', dayfirst=True)

    # Check how many failed
    na_mask = parsed.isna() & series.notna()

    if na_mask.any():
        logger.info(f"Falling back to element-wise parsing for {na_mask.sum()} values")
        # Element-wise parsing for failed values
        for idx in series[na_mask].index:
            parsed_date = parse_single_date(series.loc[idx])
            if parsed_date is not None:
                parsed.loc[idx] = pd.Timestamp(parsed_date)
            else:
                parsed.loc[idx] = pd.NaT

    # Convert to date objects
    result = parsed.apply(lambda x: x.date() if pd.notna(x) else None)
    return result


def calculate_remaining_days(expiry_date: Optional[date], reference_date: Optional[date] = None) -> Optional[int]:
    """
    Calculate remaining days until expiry.

    Args:
        expiry_date: The expiry date.
        reference_date: Reference date (defaults to today).

    Returns:
        Optional[int]: Number of days remaining (negative if expired).
    """
    if expiry_date is None:
        return None

    if reference_date is None:
        reference_date = date.today()

    delta = expiry_date - reference_date
    return delta.days


def classify_document(remaining_days: Optional[int]) -> str:
    """
    Classify document based on remaining days.

    Args:
        remaining_days: Days until expiry (None if no date).

    Returns:
        str: Status key ('EXPIRED', 'CRITICAL', 'APPROACHING', 'VALID', 'NO_DATE').
    """
    if remaining_days is None:
        return "NO_DATE"
    if remaining_days < 0:
        return "EXPIRED"
    if remaining_days <= 30:
        return "CRITICAL"
    if remaining_days <= 90:
        return "APPROACHING"
    return "VALID"
