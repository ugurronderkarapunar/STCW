"""
Reports Page
Generate and download detailed reports.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from components.styles import get_custom_css
from services.report_service import ReportService


def main():
    st.set_page_config(
        page_title="Raporlar - Belge Takip",
        page_icon="📈",
        layout="wide",
    )

    st.markdown(get_custom_css(), unsafe_allow_html=True)

    st.markdown(
        "<h1 style='color: #1B3A5C;'>📈 Rapor Merkezi</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color: #7F8C8D;'>Detaylı raporlar oluşturun ve indirin.</p>",
        unsafe_allow_html=True,
    )

    if "analysis_service" not in st.session_state or not st.session_state.data_loaded:
        st.warning("⚠️ Lütfen önce Ana Dashboard sayfasından bir dosya yükleyin.")
        return

    service = st.session_state.analysis_service
    data = service.processed_data

    if data is None or data.empty:
        st.warning("⚠️ Veri bulunamadı.")
        return

    # Report type selector
    report_type = st.selectbox(
        "📄 Rapor Türü",
        options=[
            "Özet Rapor",
            "Süresi Geçmiş Belgeler",
            "Kritik Belgeler (0-30 Gün)",
            "Yaklaşan Belgeler (31-90 Gün)",
            "Personel Özeti",
            "Ünvan Bazlı Özet",
            "Belge Türü Bazlı Özet",
            "Eksik Tarihli Belgeler",
            "Tam Veri Dökümü",
        ],
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if report_type == "Özet Rapor":
        render_summary_report(service, data)

    elif report_type == "Süresi Geçmiş Belgeler":
        render_filtered_report(data, "EXPIRED", "🔴 Süresi Geçmiş Belgeler")

    elif report_type == "Kritik Belgeler (0-30 Gün)":
        render_filtered_report(data, "CRITICAL", "🟠 Kritik Belgeler (0-30 Gün)")

    elif report_type == "Yaklaşan Belgeler (31-90 Gün)":
        render_filtered_report(data, "APPROACHING", "🟡 Yaklaşan Belgeler (31-90 Gün)")

    elif report_type == "Personel Özeti":
        render_dataframe_report(
            service.personnel_summary,
            "Personel Özeti",
            ["personnel_name", "rank_title", "total_documents", "expired_count", "critical_count", "approaching_count", "valid_count"],
            ["Ad Soyad", "Ünvan", "Toplam Belge", "Geçmiş", "Kritik", "Yaklaşıyor", "Geçerli"],
        )

    elif report_type == "Ünvan Bazlı Özet":
        render_dataframe_report(
            service.rank_summary,
            "Ünvan Bazlı Özet",
            ["rank_title", "personnel_count", "total_documents", "expired_count", "critical_count", "risk_score"],
            ["Ünvan", "Personel Sayısı", "Toplam Belge", "Geçmiş", "Kritik", "Risk Skoru"],
        )

    elif report_type == "Belge Türü Bazlı Özet":
        render_dataframe_report(
            service.document_summary,
            "Belge Türü Bazlı Özet",
            ["document_name", "total_count", "expired_count", "critical_count", "approaching_count", "valid_count"],
            ["Belge Adı", "Toplam", "Geçmiş", "Kritik", "Yaklaşıyor", "Geçerli"],
        )

    elif report_type == "Eksik Tarihli Belgeler":
        render_filtered_report(data, "NO_DATE", "⚪ Eksik Tarihli Belgeler")

    elif report_type == "Tam Veri Dökümü":
        render_full_data_report(data, service)


def render_summary_report(service, data):
    """Render executive summary report."""
    metrics = service.get_kpi_metrics()

    today = date.today()
    summary_text = ReportService.generate_summary_text(metrics)

    st.markdown("<div class='section-header'>📋 Yönetici Özeti</div>", unsafe_allow_html=True)

    st.code(summary_text, language=None)

    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Özet Metin İndir (.txt)",
            data=summary_text,
            file_name=f"yonetici_ozeti_{today.strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # Risk highlights
    st.markdown("<div class='section-header'>⚠️ Risk Özeti</div>", unsafe_allow_html=True)

    expired_personnel = data[data["status"] == "EXPIRED"]["personnel_name"].unique()
    critical_personnel = data[data["status"] == "CRITICAL"]["personnel_name"].unique()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔴 Süresi Geçmiş Belgesi Olan Personel:**")
        if len(expired_personnel) > 0:
            for p in expired_personnel[:20]:
                st.markdown(f"- {p}")
            if len(expired_personnel) > 20:
                st.caption(f"...ve {len(expired_personnel) - 20} kişi daha")
        else:
            st.success("✅ Süresi geçmiş belge yok.")

    with col2:
        st.markdown("**🟠 Kritik Durumda Olan Personel:**")
        if len(critical_personnel) > 0:
            for p in critical_personnel[:20]:
                st.markdown(f"- {p}")
            if len(critical_personnel) > 20:
                st.caption(f"...ve {len(critical_personnel) - 20} kişi daha")
        else:
            st.success("✅ Kritik durumda belge yok.")


def render_filtered_report(data, status, title):
    """Render report for specific status."""
    filtered = data[data["status"] == status].copy()

    st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)

    if filtered.empty:
        st.success("✅ Bu kategoride belge bulunmamaktadır.")
        return

    st.markdown(f"**Toplam Kayıt:** {len(filtered)}")

    display_df = filtered[[
        "personnel_name", "rank_normalized", "document_name",
        "expiry_date", "remaining_days"
    ]].copy()

    display_df.columns = ["Ad Soyad", "Ünvan", "Belge", "Bitiş Tarihi", "Kalan Gün"]
    display_df["Bitiş Tarihi"] = display_df["Bitiş Tarihi"].apply(
        lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) and x is not None else "-"
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)

    # Download
    csv_data = ReportService.generate_csv(filtered)
    st.download_button(
        label=f"📥 CSV İndir ({len(filtered)} kayıt)",
        data=csv_data,
        file_name=f"rapor_{status.lower()}_{date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render_dataframe_report(df, title, columns, labels):
    """Render a styled dataframe report."""
    st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)

    if df is None or df.empty:
        st.info("Bu rapor için yeterli veri bulunamadı.")
        return

    display_df = df[columns].copy()
    display_df.columns = labels

    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)

    csv_data = ReportService.generate_csv(display_df)
    st.download_button(
        label="📥 CSV İndir",
        data=csv_data,
        file_name=f"rapor_{date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render_full_data_report(data, service):
    """Render full data dump with all sheets as Excel."""
    st.markdown("<div class='section-header'>📄 Tam Veri Dökümü</div>", unsafe_allow_html=True)

    st.markdown(f"**Toplam Kayıt:** {len(data)}")

    # Preview
    st.dataframe(data, use_container_width=True, hide_index=True, height=400)

    # Generate Excel with all sheets
    excel_data = ReportService.generate_excel(
        data,
        service.personnel_summary if service.personnel_summary is not None else pd.DataFrame(),
        service.rank_summary if service.rank_summary is not None else pd.DataFrame(),
    )

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Tam Excel Raporu İndir",
            data=excel_data,
            file_name=f"tam_rapor_{date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col2:
        csv_data = ReportService.generate_csv(data)
        st.download_button(
            label="📥 CSV İndir",
            data=csv_data,
            file_name=f"tum_veri_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
