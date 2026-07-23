"""
Table rendering components for the dashboard.
"""

import pandas as pd
import streamlit as st
from datetime import date
from typing import Optional, List


def render_expired_table(data: pd.DataFrame, max_rows: int = 50) -> None:
    """
    Render table of expired documents.

    Args:
        data: Filtered DataFrame with expired documents.
        max_rows: Maximum rows to display.
    """
    if data.empty:
        st.info("✅ Süresi geçmiş belge bulunmamaktadır.")
        return

    display_df = data[data["status"] == "EXPIRED"].copy()

    if display_df.empty:
        st.info("✅ Süresi geçmiş belge bulunmamaktadır.")
        return

    # Select and rename columns
    display_df = display_df[[
        "personnel_name", "rank_normalized", "document_name",
        "expiry_date", "remaining_days", "status"
    ]].copy()

    display_df.columns = [
        "Ad Soyad", "Ünvan", "Belge",
        "Bitiş Tarihi", "Kaç Gün Geçmiş", "Durum"
    ]

    # Format
    display_df["Kaç Gün Geçmiş"] = display_df["Kaç Gün Geçmiş"].apply(
        lambda x: f"{abs(int(x))} gün" if pd.notna(x) else "-"
    )
    display_df["Bitiş Tarihi"] = display_df["Bitiş Tarihi"].apply(
        lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) and x is not None else "-"
    )

    st.dataframe(
        display_df.head(max_rows),
        use_container_width=True,
        hide_index=True,
        height=min(400, 35 * len(display_df) + 38),
        column_config={
            "Ad Soyad": st.column_config.TextColumn(width="medium"),
            "Ünvan": st.column_config.TextColumn(width="medium"),
            "Belge": st.column_config.TextColumn(width="medium"),
            "Bitiş Tarihi": st.column_config.TextColumn(width="small"),
            "Kaç Gün Geçmiş": st.column_config.TextColumn(width="small"),
            "Durum": st.column_config.TextColumn(width="small"),
        },
    )

    if len(display_df) > max_rows:
        st.caption(f"Toplam {len(display_df)} kayıttan ilk {max_rows} tanesi gösteriliyor.")


def render_critical_table(data: pd.DataFrame, max_rows: int = 50) -> None:
    """
    Render table of critical documents (0-30 days).

    Args:
        data: Filtered DataFrame.
        max_rows: Maximum rows to display.
    """
    display_df = data[data["status"] == "CRITICAL"].copy()

    if display_df.empty:
        st.info("✅ 30 gün içinde bitecek belge bulunmamaktadır.")
        return

    display_df = display_df[[
        "personnel_name", "rank_normalized", "document_name",
        "expiry_date", "remaining_days"
    ]].copy()

    display_df.columns = [
        "Ad Soyad", "Ünvan", "Belge", "Bitiş Tarihi", "Kalan Gün"
    ]

    display_df["Kalan Gün"] = display_df["Kalan Gün"].apply(
        lambda x: f"{int(x)} gün" if pd.notna(x) else "-"
    )
    display_df["Bitiş Tarihi"] = display_df["Bitiş Tarihi"].apply(
        lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) and x is not None else "-"
    )

    st.dataframe(
        display_df.head(max_rows),
        use_container_width=True,
        hide_index=True,
        height=min(400, 35 * len(display_df) + 38),
    )

    if len(display_df) > max_rows:
        st.caption(f"Toplam {len(display_df)} kayıttan ilk {max_rows} tanesi gösteriliyor.")


def render_approaching_table(data: pd.DataFrame, max_rows: int = 50) -> None:
    """
    Render table of approaching documents (31-90 days).

    Args:
        data: Filtered DataFrame.
        max_rows: Maximum rows to display.
    """
    display_df = data[data["status"] == "APPROACHING"].copy()

    if display_df.empty:
        st.info("✅ 90 gün içinde bitecek belge bulunmamaktadır.")
        return

    display_df = display_df[[
        "personnel_name", "rank_normalized", "document_name",
        "expiry_date", "remaining_days"
    ]].copy()

    display_df.columns = [
        "Ad Soyad", "Ünvan", "Belge", "Bitiş Tarihi", "Kalan Gün"
    ]

    display_df["Kalan Gün"] = display_df["Kalan Gün"].apply(
        lambda x: f"{int(x)} gün" if pd.notna(x) else "-"
    )
    display_df["Bitiş Tarihi"] = display_df["Bitiş Tarihi"].apply(
        lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) and x is not None else "-"
    )

    st.dataframe(
        display_df.head(max_rows),
        use_container_width=True,
        hide_index=True,
        height=min(400, 35 * len(display_df) + 38),
    )

    if len(display_df) > max_rows:
        st.caption(f"Toplam {len(display_df)} kayıttan ilk {max_rows} tanesi gösteriliyor.")


def render_missing_date_table(data: pd.DataFrame, max_rows: int = 50) -> None:
    """
    Render table of documents with missing dates.

    Args:
        data: Filtered DataFrame.
        max_rows: Maximum rows to display.
    """
    display_df = data[data["status"] == "NO_DATE"].copy()

    if display_df.empty:
        st.info("✅ Tarih bilgisi eksik belge bulunmamaktadır.")
        return

    display_df = display_df[[
        "personnel_name", "rank_normalized", "document_name"
    ]].copy()

    display_df.columns = ["Ad Soyad", "Ünvan", "Belge"]

    st.dataframe(
        display_df.head(max_rows),
        use_container_width=True,
        hide_index=True,
        height=min(400, 35 * len(display_df) + 38),
    )

    if len(display_df) > max_rows:
        st.caption(f"Toplam {len(display_df)} kayıttan ilk {max_rows} tanesi gösteriliyor.")


def render_invalid_date_table(data: pd.DataFrame, max_rows: int = 50) -> None:
    """
    Render table of documents with invalid dates.

    Args:
        data: Filtered DataFrame.
        max_rows: Maximum rows to display.
    """
    if "is_invalid_date" not in data.columns:
        st.info("✅ Hatalı tarih bulunmamaktadır.")
        return

    display_df = data[data["is_invalid_date"] == True].copy()

    if display_df.empty:
        st.info("✅ Hatalı tarih bulunmamaktadır.")
        return

    display_df = display_df[[
        "personnel_name", "rank_normalized", "document_name", "expiry_date_raw"
    ]].copy()

    display_df.columns = ["Ad Soyad", "Ünvan", "Belge", "Ham Tarih Verisi"]

    st.dataframe(
        display_df.head(max_rows),
        use_container_width=True,
        hide_index=True,
        height=min(400, 35 * len(display_df) + 38),
    )

    if len(display_df) > max_rows:
        st.caption(f"Toplam {len(display_df)} kayıttan ilk {max_rows} tanesi gösteriliyor.")
