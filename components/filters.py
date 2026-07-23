"""
Filter components for the Streamlit sidebar.
"""

import streamlit as st
from typing import Dict, List, Optional, Any


def render_sidebar_filters(filter_options: Dict[str, List[Any]]) -> Dict[str, Any]:
    """
    Render all sidebar filters and return selected values.

    Args:
        filter_options: Dictionary of available filter values.

    Returns:
        Dict with selected filter values.
    """
    st.sidebar.markdown("### 🔍 Filtreler")

    filters = {}

    # Personnel search
    filters["personnel_search"] = st.sidebar.text_input(
        "🔎 Personel Ara",
        placeholder="Ad veya soyad yazın...",
        label_visibility="visible",
    )

    # Rank filter
    if filter_options.get("ranks"):
        filters["rank_filter"] = st.sidebar.multiselect(
            "🎖️ Ünvan",
            options=filter_options["ranks"],
            default=[],
            placeholder="Ünvan seçin...",
        )
    else:
        filters["rank_filter"] = []

    # Status filter
    if filter_options.get("statuses"):
        status_labels = {
            "EXPIRED": "🔴 Süresi Geçmiş",
            "CRITICAL": "🟠 Kritik (0-30 Gün)",
            "APPROACHING": "🟡 Yaklaşıyor (31-90 Gün)",
            "VALID": "🟢 Geçerli",
            "NO_DATE": "⚪ Tarih Yok",
        }
        status_options = [status_labels.get(s, s) for s in filter_options["statuses"]]

        selected_labels = st.sidebar.multiselect(
            "📊 Belge Durumu",
            options=status_options,
            default=[],
            placeholder="Durum seçin...",
        )

        # Convert labels back to status keys
        reverse_status = {v: k for k, v in status_labels.items()}
        filters["status_filter"] = [
            reverse_status.get(label, label) for label in selected_labels
        ]
    else:
        filters["status_filter"] = []

    # Document type filter
    if filter_options.get("documents"):
        filters["document_filter"] = st.sidebar.multiselect(
            "📄 Belge Türü",
            options=filter_options["documents"],
            default=[],
            placeholder="Belge türü seçin...",
        )
    else:
        filters["document_filter"] = []

    # Month filter
    if filter_options.get("months"):
        month_names = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
        }
        month_options = [month_names[m] for m in filter_options["months"]]
        selected_month = st.sidebar.selectbox(
            "📅 Ay",
            options=["Tümü"] + month_options,
            index=0,
        )
        if selected_month != "Tümü":
            reverse_months = {v: k for k, v in month_names.items()}
            filters["month_filter"] = reverse_months[selected_month]
        else:
            filters["month_filter"] = None
    else:
        filters["month_filter"] = None

    # Year filter
    if filter_options.get("years"):
        selected_year = st.sidebar.selectbox(
            "📅 Yıl",
            options=["Tümü"] + [str(y) for y in filter_options["years"]],
            index=0,
        )
        if selected_year != "Tümü":
            filters["year_filter"] = int(selected_year)
        else:
            filters["year_filter"] = None
    else:
        filters["year_filter"] = None

    # Reset button
    if st.sidebar.button("🔄 Filtreleri Sıfırla", use_container_width=True):
        st.rerun()

    return filters


def render_file_upload_section() -> Optional[Any]:
    """
    Render file upload widget in sidebar.

    Returns:
        UploadedFile or None.
    """
    st.sidebar.markdown("### 📤 Veri Yükleme")

    uploaded_file = st.sidebar.file_uploader(
        "Excel veya CSV dosyası yükleyin",
        type=["xlsx", "csv", "xls"],
        help="Personel belge verilerini içeren Excel/CSV dosyası",
    )

    return uploaded_file
