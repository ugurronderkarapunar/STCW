"""
Notification component for real-time alerts based on thresholds.
"""
import streamlit as st
from typing import Dict, Any
from utils.config import NOTIFICATION_THRESHOLDS

def check_and_notify(metrics: Dict[str, Any]) -> None:
    """
    Check KPI metrics against thresholds and display warnings.
    
    Args:
        metrics: Dictionary of KPI values from AnalysisService.
    """
    expired = metrics.get("expired", 0)
    critical = metrics.get("critical", 0)
    no_date = metrics.get("no_date", 0)
    
    if expired > NOTIFICATION_THRESHOLDS["expired_warning"]:
        st.toast(
            f"⚠️ Süresi geçmiş belge sayısı {expired} (eşik: {NOTIFICATION_THRESHOLDS['expired_warning']})",
            icon="🔴"
        )
    if critical > NOTIFICATION_THRESHOLDS["critical_warning"]:
        st.toast(
            f"⚠️ Kritik belge sayısı {critical} (eşik: {NOTIFICATION_THRESHOLDS['critical_warning']})",
            icon="🟠"
        )
    if no_date > NOTIFICATION_THRESHOLDS["missing_date_warning"]:
        st.toast(
            f"⚠️ Tarih bilgisi olmayan belge sayısı {no_date} (eşik: {NOTIFICATION_THRESHOLDS['missing_date_warning']})",
            icon="⚪"
        )
