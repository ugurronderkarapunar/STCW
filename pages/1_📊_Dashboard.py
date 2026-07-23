"""
Main Dashboard Page with animations, real-time updates, interactive charts, and notifications.
"""

import streamlit as st
import pandas as pd
from datetime import date
import hashlib

from components.kpi_cards import render_kpi_cards
from components.charts import (
    render_status_distribution,
    render_rank_risk_chart,
    render_monthly_forecast,
    render_document_type_chart,
    render_top_risk_personnel,
)
from components.tables import (
    render_expired_table,
    render_critical_table,
    render_approaching_table,
    render_missing_date_table,
    render_invalid_date_table,
)
from components.filters import render_sidebar_filters, render_file_upload_section
from components.styles import get_custom_css, get_light_theme_css, get_dark_theme_css
from components.notifications import check_and_notify
from services.analysis_service import AnalysisService
from services.report_service import ReportService
from utils.config import APP_LOGO_URL, COMPANY_NAME


def init_session_state():
    """Initialize session state variables."""
    if "analysis_service" not in st.session_state:
        st.session_state.analysis_service = AnalysisService()
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
    if "filtered_data" not in st.session_state:
        st.session_state.filtered_data = None
    if "sample_data_used" not in st.session_state:
        st.session_state.sample_data_used = False
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "default_rank_filter" not in st.session_state:
        st.session_state.default_rank_filter = []
    if "default_status_filter" not in st.session_state:
        st.session_state.default_status_filter = []
    if "last_file_hash" not in st.session_state:
        st.session_state.last_file_hash = None


def generate_sample_data() -> pd.DataFrame:
    """Generate sample personnel document data for demo."""
    import numpy as np
    from datetime import timedelta

    np.random.seed(42)
    n_records = 200
    names = [
        "Ali Yılmaz", "Mehmet Demir", "Ayşe Kaya", "Fatma Çelik",
        "Mustafa Şahin", "Zeynep Aydın", "Hüseyin Özdemir", "Emine Arslan",
        "Ahmet Yıldız", "Hatice Doğan", "İbrahim Koç", "Elif Öztürk",
        "Osman Aksoy", "Merve Tekin", "Can Polat", "Selin Güneş",
        "Burak Kaplan", "Deniz Acar", "Ece Yalçın", "Cem Korkmaz",
    ]
    ranks = [
        "Kaptan", "Baş Makinist", "Güverte Lostromosu",
        "Gemici", "Yağcı",
    ]
    documents = [
        "00-Gemiadamları Sağlık Yoklama Belgesi",
        "05-Cankurtarma Araçlarını Kullanm.Yt.Bl.",
        "01-Denizde Kişisel Can Kurtarma Teknikl.",
        "23-GMDSS Sınırlı Telsiz Opert.Blg.(ROC)",
        "10-İleri Yangınla Mücadele Belgesi",
        "04-Personel Güvenliği ve Sosyal Sor.Bl.",
        "17-Ro-Ro Yolcu Gemileri Gemiadamları Blg",
        "02-Temel İlk Yardım Belgesi",
        "03-Yangın Önleme ve Yangınla Mücadele Bl",
        "31-Gemi Adamı Cüzdan Belgesi",
        "24-Genel Telsiz Operatörü (GOC) Belgesi",
        "25-Kısa Mesafe Telsiz Operatörü Belgesi",
    ]
    data = []
    today = date.today()
    for i in range(n_records):
        name = np.random.choice(names)
        rank = np.random.choice(ranks)
        doc = np.random.choice(documents)
        days_offset = np.random.choice([
            np.random.randint(-365, 0),
            np.random.randint(0, 30),
            np.random.randint(31, 90),
            np.random.randint(91, 730),
            99999,
        ], p=[0.15, 0.20, 0.25, 0.35, 0.05])
        if days_offset == 99999:
            expiry = None
        else:
            expiry = today + timedelta(days=int(days_offset))
        data.append({
            "Ad": name,
            "Pzs.tanımı": rank,
            "Nitelik": doc,
            "Bitiş Tarihi": expiry.strftime("%d.%m.%Y") if expiry else "",
        })
    return pd.DataFrame(data)


def main():
    st.set_page_config(
        page_title="Personel Belge Takip Sistemi",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    if st.session_state.theme == "dark":
        st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
    else:
        st.markdown(get_light_theme_css(), unsafe_allow_html=True)
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # ── Header with Logo & Company Name ──
    st.markdown(
        f"""
        <div class="app-header animate-fade-in">
            <img src="{APP_LOGO_URL}" class="app-logo" alt="Logo">
            <div>
                <h1 class="app-title">📊 Personel Belge Takip Sistemi</h1>
                <div class="company-name">{COMPANY_NAME}</div>
            </div>
        </div>
        <hr>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ──
    with st.sidebar:
        uploaded_file = render_file_upload_section()

        if not st.session_state.data_loaded and uploaded_file is None:
            if st.button("📋 Örnek Veri ile Dene", use_container_width=True):
                sample_df = generate_sample_data()
                csv_bytes = sample_df.to_csv(index=False).encode('utf-8-sig')
                service = st.session_state.analysis_service
                success = service.load_file(csv_bytes, "ornek_veri.csv")
                if success:
                    st.session_state.data_loaded = True
                    st.session_state.sample_data_used = True
                    st.success("✅ Örnek veri yüklendi!")
                    st.rerun()
                else:
                    st.error(f"❌ Hata: {'; '.join(service.errors)}")

        st.markdown("---")

    # ── File Upload Handling (with hash check for real-time update) ──
    if uploaded_file is not None:
        service = st.session_state.analysis_service
        file_bytes = uploaded_file.read()
        file_hash = hashlib.md5(file_bytes).hexdigest()

        if st.session_state.last_file_hash != file_hash:
            with st.spinner("📂 Dosya analiz ediliyor..."):
                success = service.load_file(file_bytes, uploaded_file.name)
            if success:
                st.session_state.data_loaded = True
                st.session_state.last_file_hash = file_hash
                st.sidebar.success(f"✅ {uploaded_file.name} başarıyla yüklendi!")
                st.rerun()
            else:
                st.sidebar.error(f"❌ Hata: {'; '.join(service.errors)}")
                for warning in service.warnings:
                    st.sidebar.warning(f"⚠️ {warning}")

    # ── Reload Button ──
    if st.session_state.data_loaded:
        if st.sidebar.button("🔄 Veriyi Yeniden Yükle", use_container_width=True):
            st.session_state.last_file_hash = None
            st.rerun()

    service = st.session_state.analysis_service

    # ── Filters & Mapping Debug ──
    if st.session_state.data_loaded:
        filter_options = service.get_filter_options()
        filters = render_sidebar_filters(filter_options)

        # Apply default filters from settings
        if not filters.get("rank_filter") and not filters.get("status_filter"):
            if st.session_state.default_rank_filter:
                filters["rank_filter"] = st.session_state.default_rank_filter
            if st.session_state.default_status_filter:
                filters["status_filter"] = st.session_state.default_status_filter

        filtered_data = service.get_filtered_data(
            rank_filter=filters.get("rank_filter") if filters.get("rank_filter") else None,
            status_filter=filters.get("status_filter") if filters.get("status_filter") else None,
            document_filter=filters.get("document_filter") if filters.get("document_filter") else None,
            personnel_search=filters.get("personnel_search") if filters.get("personnel_search") else None,
            month_filter=filters.get("month_filter"),
            year_filter=filters.get("year_filter"),
        )
        st.session_state.filtered_data = filtered_data

        # Column Mapping Debug Info
        mapping = service.get_column_mapping_info()
        if mapping:
            with st.sidebar.expander("🔍 Kolon Eşleşmeleri", expanded=False):
                st.markdown(f"**Personel Adı:** {mapping.get('personnel_name', '❌ Bulunamadı')}")
                st.markdown(f"**Ünvan:** {mapping.get('rank_title', '❌ Bulunamadı')}")
                st.markdown(f"**Belge Adı:** {mapping.get('document_name', '❌ Bulunamadı')}")
                st.markdown(f"**Bitiş Tarihi:** {mapping.get('expiry_date', '❌ Bulunamadı')}")
                if mapping.get('expiry_date') is None:
                    st.info("💡 Tarih sütunu bulunamadı. Belgeler 'Eklenecek' olarak işaretlenir.")
    else:
        st.session_state.filtered_data = None

    # ── Landing Page ──
    if not st.session_state.data_loaded:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                """
                <div style='text-align: center; padding: 40px 20px; background: var(--card-bg); 
                     border-radius: 16px; box-shadow: var(--shadow); animation: fadeIn 0.8s ease-out;'>
                    <h2 style='color: var(--primary);'>👋 Hoş Geldiniz</h2>
                    <p style='color: var(--text-light); font-size: 1.1rem; margin: 20px 0;'>
                        Personel belge takip sistemini kullanmak için lütfen
                        <strong>Excel veya CSV</strong> dosyası yükleyin.
                    </p>
                    <p style='color: var(--text-light);'>
                        📌 Sol paneldeki <strong>"Örnek Veri ile Dene"</strong> butonuna tıklayarak
                        sistemi test edebilirsiniz.
                    </p>
                    <hr style='margin: 24px 0;'>
                    <h4 style='color: var(--primary);'>🔍 Sistemin Sundukları</h4>
                    <div style='text-align: left; max-width: 400px; margin: 0 auto;'>
                        <p>✅ Otomatik kolon eşleştirme</p>
                        <p>✅ Çoklu tarih formatı desteği</p>
                        <p>✅ Risk bazlı belge sınıflandırması</p>
                        <p>✅ Personel bazlı özet kartları</p>
                        <p>✅ İnteraktif grafikler</p>
                        <p>✅ Excel, CSV raporlama</p>
                        <p>✅ Ünvan bazlı filtreleme</p>
                        <p>✅ Canlı arama</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        return

    # ── Dashboard Content ──
    data_to_use = st.session_state.filtered_data if st.session_state.filtered_data is not None else service.processed_data

    if data_to_use is None or data_to_use.empty:
        st.warning("⚠️ Filtrelere uygun veri bulunamadı.")
        return

    filtered_metrics = {
        "total_personnel": data_to_use["personnel_name"].nunique(),
        "total_ranks": data_to_use["rank_normalized"].nunique(),
        "total_documents": len(data_to_use),
        "expired": int((data_to_use["status"] == "EXPIRED").sum()),
        "critical": int((data_to_use["status"] == "CRITICAL").sum()),
        "approaching": int((data_to_use["status"] == "APPROACHING").sum()),
        "valid": int((data_to_use["status"] == "VALID").sum()),
        "no_date": int((data_to_use["status"] == "NO_DATE").sum()),
        "invalid_dates": int(data_to_use["is_invalid_date"].sum()) if "is_invalid_date" in data_to_use.columns else 0,
    }

    # ── Animated KPI Cards & Notifications ──
    render_kpi_cards(filtered_metrics)
    check_and_notify(filtered_metrics)  # Toast notifications

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive Graph Selection (Drill-down) ──
    # Using selectbox to simulate click on rank from risk chart
    rank_list = sorted(data_to_use["rank_normalized"].unique())
    selected_rank = st.selectbox("🎯 Grafikten ünvan seçerek filtrele (interaktif)", ["Tümü"] + rank_list)
    if selected_rank != "Tümü":
        data_to_use = data_to_use[data_to_use["rank_normalized"] == selected_rank]
        st.info(f"🔍 '{selected_rank}' için filtrelenmiş görünüm.")

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Grafikler", "📋 Risk Tabloları", "👤 Personel Kartları", "📄 Tüm Veriler"
    ])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            status_dist = data_to_use["status_label"].value_counts().reset_index()
            status_dist.columns = ["status", "count"]
            render_status_distribution(status_dist)
            doc_summary = service.document_summary
            if doc_summary is not None and not doc_summary.empty:
                render_document_type_chart(doc_summary)
            else:
                st.info("Belge türü dağılımı bulunamadı.")
        with col2:
            full_rank_summary = service.rank_summary
            if full_rank_summary is not None and not full_rank_summary.empty:
                render_rank_risk_chart(full_rank_summary)
            else:
                st.info("Ünvan bazlı risk grafiği bulunamadı.")
            full_monthly = service.monthly_forecast
            if full_monthly is not None and not full_monthly.empty:
                render_monthly_forecast(full_monthly)
            else:
                st.info("Aylık bitiş öngörüsü bulunamadı.")
        full_personnel_risk = service.personnel_summary
        if full_personnel_risk is not None and not full_personnel_risk.empty:
            render_top_risk_personnel(full_personnel_risk)

    with tab2:
        st.markdown("<div class='section-header'>🔴 Süresi Geçmiş Belgeler</div>", unsafe_allow_html=True)
        render_expired_table(data_to_use)
        st.markdown("<div class='section-header'>🟠 30 Gün İçinde Bitecek Belgeler</div>", unsafe_allow_html=True)
        render_critical_table(data_to_use)
        st.markdown("<div class='section-header'>🟡 90 Gün İçinde Bitecek Belgeler</div>", unsafe_allow_html=True)
        render_approaching_table(data_to_use)
        st.markdown("<div class='section-header'>⚪ Eklenecek Tarih Bilgisi</div>", unsafe_allow_html=True)
        render_missing_date_table(data_to_use)
        st.markdown("<div class='section-header'>⚠️ Hatalı Tarihler</div>", unsafe_allow_html=True)
        render_invalid_date_table(data_to_use)

    with tab3:
        render_personnel_cards(data_to_use)

    with tab4:
        st.markdown("<div class='section-header'>📄 Tüm Belge Kayıtları</div>", unsafe_allow_html=True)
        display_cols = [
            "personnel_name", "rank_normalized", "document_name",
            "expiry_date", "remaining_days", "status_emoji", "status_label"
        ]
        available_cols = [c for c in display_cols if c in data_to_use.columns]
        display_df = data_to_use[available_cols].copy()
        col_labels = ["Ad Soyad", "Ünvan", "Belge", "Bitiş Tarihi", "Kalan Gün", "Durum Emoji", "Durum"]
        display_df.columns = col_labels[:len(available_cols)]
        if "Bitiş Tarihi" in display_df.columns:
            display_df["Bitiş Tarihi"] = display_df["Bitiş Tarihi"].apply(
                lambda x: x.strftime("%d.%m.%Y") if pd.notna(x) and x is not None else "Eklenecek"
            )
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=600)

        st.markdown("<div class='download-section'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            csv_data = ReportService.generate_csv(data_to_use)
            st.download_button("📥 CSV İndir", csv_data, f"belge_raporu_{date.today().strftime('%Y%m%d')}.csv", "text/csv", use_container_width=True)
        with col2:
            excel_data = ReportService.generate_excel(
                data_to_use,
                service.personnel_summary if service.personnel_summary is not None else pd.DataFrame(),
                service.rank_summary if service.rank_summary is not None else pd.DataFrame(),
            )
            st.download_button("📥 Excel İndir", excel_data, f"belge_raporu_{date.today().strftime('%Y%m%d')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col3:
            summary_text = ReportService.generate_summary_text(filtered_metrics)
            st.download_button("📥 Özet Metin İndir", summary_text, f"ozet_rapor_{date.today().strftime('%Y%m%d')}.txt", "text/plain", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='text-align: center; color: var(--text-light); font-size: 0.8rem;'>
            🏢 Personel Belge Takip Sistemi v1.0 | Rapor Tarihi: {date.today().strftime('%d.%m.%Y')} |
            Toplam {filtered_metrics.get('total_personnel', 0)} Personel |
            {filtered_metrics.get('total_documents', 0)} Belge
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_personnel_cards(data: pd.DataFrame) -> None:
    """Render personnel summary cards with document status."""
    if data.empty:
        st.info("Gösterilecek personel bulunamadı.")
        return
    personnel_groups = data.groupby(["personnel_name", "rank_normalized"], dropna=False)
    search = st.text_input("🔎 Personel ara...", placeholder="İsim yazın...", key="personnel_card_search")
    st.markdown(f"**Toplam Personel:** {len(personnel_groups)}")
    count = 0
    for (name, rank), group in personnel_groups:
        if search and search.lower() not in str(name).lower():
            continue
        expired = group[group["status"] == "EXPIRED"]
        critical = group[group["status"] == "CRITICAL"]
        approaching = group[group["status"] == "APPROACHING"]
        if len(expired) > 0:
            risk_class = "risk-expired"
        elif len(critical) > 0:
            risk_class = "risk-critical"
        elif len(approaching) > 0:
            risk_class = "risk-approaching"
        else:
            risk_class = ""
        tags_html = ""
        for _, row in expired.iterrows():
            tags_html += f"<span class='document-tag tag-expired'>{row['document_name']} (Geçmiş)</span>"
        for _, row in critical.iterrows():
            days = int(row['remaining_days']) if pd.notna(row['remaining_days']) else 0
            tags_html += f"<span class='document-tag tag-critical'>{row['document_name']} ({days} gün)</span>"
        for _, row in approaching.iterrows():
            days = int(row['remaining_days']) if pd.notna(row['remaining_days']) else 0
            tags_html += f"<span class='document-tag tag-approaching'>{row['document_name']} ({days} gün)</span>"
        valid_count = len(group) - len(expired) - len(critical) - len(approaching)
        st.markdown(
            f"""
            <div class="personnel-card {risk_class}">
                <div class="personnel-name">{name}</div>
                <div class="personnel-rank">🎖️ {rank if rank and str(rank) != 'nan' else 'Belirtilmemiş'}</div>
                <div class="document-tags">
                    {tags_html if tags_html else '<span style="color: var(--text-light); font-size: 0.85rem;">✅ Tüm belgeler geçerli</span>'}
                </div>
                <div class="metric-row" style="margin-top: 10px;">
                    <div class="metric-item"><div class="metric-value">{len(expired)}</div><div class="metric-label">🔴 Geçmiş</div></div>
                    <div class="metric-item"><div class="metric-value">{len(critical)}</div><div class="metric-label">🟠 Kritik</div></div>
                    <div class="metric-item"><div class="metric-value">{len(approaching)}</div><div class="metric-label">🟡 Yaklaşıyor</div></div>
                    <div class="metric-item"><div class="metric-value">{valid_count}</div><div class="metric-label">🟢 Geçerli</div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        count += 1
        if count >= 50 and not search:
            st.info("İlk 50 personel gösteriliyor. Arama yaparak belirli bir personele ulaşabilirsiniz.")
            break
    if count == 0 and search:
        st.warning(f"'{search}' ile eşleşen personel bulunamadı.")


if __name__ == "__main__":
    main()
