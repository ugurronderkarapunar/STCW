"""
KPI Card components for the dashboard.
"""

import streamlit as st
from typing import Dict, Any


def render_kpi_cards(metrics: Dict[str, Any]) -> None:
    """
    Render KPI metric cards in a responsive grid.

    Args:
        metrics: Dictionary of KPI metrics from AnalysisService.
    """
    if not metrics:
        return

    # Row 1: Personnel & Document counts
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-emoji">👥</div>
                <div class="kpi-value">{metrics.get('total_personnel', 0):,}</div>
                <div class="kpi-label">Toplam Personel</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-emoji">🎖️</div>
                <div class="kpi-value">{metrics.get('total_ranks', 0):,}</div>
                <div class="kpi-label">Toplam Ünvan</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-emoji">📄</div>
                <div class="kpi-value">{metrics.get('total_documents', 0):,}</div>
                <div class="kpi-label">Toplam Belge</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card danger">
                <div class="kpi-emoji">🔴</div>
                <div class="kpi-value">{metrics.get('expired', 0):,}</div>
                <div class="kpi-label">Süresi Geçmiş</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Row 2: Risk breakdown
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card warning">
                <div class="kpi-emoji">🟠</div>
                <div class="kpi-value">{metrics.get('critical', 0):,}</div>
                <div class="kpi-label">30 Gün İçinde Bitecek</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card approaching">
                <div class="kpi-emoji">🟡</div>
                <div class="kpi-value">{metrics.get('approaching', 0):,}</div>
                <div class="kpi-label">90 Gün İçinde Bitecek</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card no-date">
                <div class="kpi-emoji">⚪</div>
                <div class="kpi-value">{metrics.get('no_date', 0):,}</div>
                <div class="kpi-label">Eksik Tarih</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card {('danger' if metrics.get('invalid_dates', 0) > 0 else 'success')}">
                <div class="kpi-emoji">⚠️</div>
                <div class="kpi-value">{metrics.get('invalid_dates', 0):,}</div>
                <div class="kpi-label">Hatalı Tarih</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
