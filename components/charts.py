"""
Chart components using Plotly for interactive visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import Optional, List
from utils.config import COLORS, STATUS_MAP


def render_status_distribution(status_counts: pd.DataFrame) -> None:
    """
    Render a pie/donut chart showing document status distribution.

    Args:
        status_counts: DataFrame with status_label and count columns.
    """
    if status_counts.empty:
        st.info("Grafik için yeterli veri bulunamadı.")
        return

    color_map = {
        "Süresi Geçmiş": COLORS["expired"],
        "Kritik (0-30 Gün)": COLORS["critical"],
        "Yaklaşıyor (31-90 Gün)": COLORS["approaching"],
        "Geçerli": COLORS["valid"],
        "Tarih Yok": COLORS["no_date"],
    }

    fig = px.pie(
        status_counts,
        values=status_counts.iloc[:, 1],
        names=status_counts.iloc[:, 0],
        title="Belge Durumu Dağılımı",
        color=status_counts.iloc[:, 0],
        color_discrete_map=color_map,
        hole=0.45,
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=2)),
    )

    fig.update_layout(
        height=450,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_rank_risk_chart(rank_summary: pd.DataFrame) -> None:
    """
    Render horizontal bar chart showing risk by rank.

    Args:
        rank_summary: Rank summary DataFrame.
    """
    if rank_summary.empty:
        st.info("Ünvan bazlı risk grafiği için yeterli veri yok.")
        return

    # Top 15 ranks by risk
    top_ranks = rank_summary.nlargest(15, "risk_score")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top_ranks["rank_title"],
        x=top_ranks["expired_count"],
        name="Süresi Geçmiş",
        orientation='h',
        marker_color=COLORS["expired"],
        text=top_ranks["expired_count"],
        textposition='inside',
    ))

    fig.add_trace(go.Bar(
        y=top_ranks["rank_title"],
        x=top_ranks["critical_count"],
        name="Kritik (0-30 Gün)",
        orientation='h',
        marker_color=COLORS["critical"],
        text=top_ranks["critical_count"],
        textposition='inside',
    ))

    fig.add_trace(go.Bar(
        y=top_ranks["rank_title"],
        x=top_ranks["approaching_count"],
        name="Yaklaşıyor (31-90 Gün)",
        orientation='h',
        marker_color=COLORS["approaching"],
        text=top_ranks["approaching_count"],
        textposition='inside',
    ))

    fig.update_layout(
        barmode='stack',
        title="Ünvana Göre Risk Dağılımı (En Riskli 15)",
        height=500,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_title="Belge Sayısı",
        yaxis_title="",
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_monthly_forecast(monthly_data: pd.DataFrame) -> None:
    """
    Render monthly expiry forecast line/bar chart.

    Args:
        monthly_data: Monthly forecast DataFrame.
    """
    if monthly_data.empty:
        st.info("Aylık bitiş öngörüsü için yeterli veri yok.")
        return

    fig = px.bar(
        monthly_data,
        x="month_label",
        y="expiring_count",
        title="Aylara Göre Bitecek Belgeler (Önümüzdeki 12 Ay)",
        labels={"month_label": "Ay", "expiring_count": "Bitecek Belge Sayısı"},
        color="expiring_count",
        color_continuous_scale=["#2ECC40", "#FFDC00", "#FF851B", "#FF4136"],
    )

    fig.update_layout(
        height=400,
        margin=dict(t=50, b=40, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_document_type_chart(doc_summary: pd.DataFrame) -> None:
    """
    Render document type distribution treemap.

    Args:
        doc_summary: Document type summary DataFrame.
    """
    if doc_summary.empty:
        st.info("Belge türü grafiği için yeterli veri yok.")
        return

    top_docs = doc_summary.nlargest(30, "total_count")

    fig = px.treemap(
        top_docs,
        path=["document_name"],
        values="total_count",
        title="Belge Türlerine Göre Dağılım (İlk 30)",
        color="expired_count",
        color_continuous_scale=["#2ECC40", "#FFDC00", "#FF4136"],
        hover_data={
            "total_count": True,
            "expired_count": True,
            "critical_count": True,
        },
    )

    fig.update_layout(
        height=450,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_top_risk_personnel(personnel_risk: pd.DataFrame) -> None:
    """
    Render horizontal bar of top risky personnel.

    Args:
        personnel_risk: Top risk personnel DataFrame.
    """
    if personnel_risk.empty:
        st.info("Riskli personel grafiği için yeterli veri yok.")
        return

    top10 = personnel_risk.head(10)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=[f"{row['personnel_name']} ({row['rank_title']})" for _, row in top10.iterrows()],
        x=top10["expired_count"],
        name="Süresi Geçmiş",
        orientation='h',
        marker_color=COLORS["expired"],
    ))

    fig.add_trace(go.Bar(
        y=[f"{row['personnel_name']} ({row['rank_title']})" for _, row in top10.iterrows()],
        x=top10["critical_count"],
        name="Kritik",
        orientation='h',
        marker_color=COLORS["critical"],
    ))

    fig.add_trace(go.Bar(
        y=[f"{row['personnel_name']} ({row['rank_title']})" for _, row in top10.iterrows()],
        x=top10["approaching_count"],
        name="Yaklaşıyor",
        orientation='h',
        marker_color=COLORS["approaching"],
    ))

    fig.update_layout(
        barmode='stack',
        title="En Riskli Personeller (İlk 10)",
        height=400,
        margin=dict(t=50, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
