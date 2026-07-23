"""
Belge Düzenleme Sayfası
Personel belgelerinin başlangıç/bitiş tarihlerini güncelleyin.
Değişiklikler sayfa yeniden yüklendiğinde görünür.
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from components.styles import get_custom_css
from utils.config import DOCUMENT_VALIDITY_MAP, DEFAULT_DOCUMENT_VALIDITY_DAYS


def get_default_validity(document_name: str) -> int:
    """Belge adına göre varsayılan geçerlilik süresini (gün) döndür."""
    doc_lower = str(document_name).lower()
    for key, days in DOCUMENT_VALIDITY_MAP.items():
        if key in doc_lower:
            return days
    return DEFAULT_DOCUMENT_VALIDITY_DAYS


def main():
    st.set_page_config(page_title="Belge Düzenle", page_icon="✏️", layout="wide")
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    st.markdown("<h1 style='color: #1B3A5C;'>✏️ Belge Tarihlerini Düzenle</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7F8C8D;'>Personel seçerek belgelerine yeni başlangıç ve bitiş tarihi girebilirsiniz.</p>", unsafe_allow_html=True)

    if "analysis_service" not in st.session_state or not st.session_state.data_loaded:
        st.warning("⚠️ Lütfen önce Dashboard'dan veri yükleyin.")
        return

    service = st.session_state.analysis_service

    # Her seferinde güncel veriyi doğrudan service'den al
    data = service.processed_data

    # Personel listesi
    personnel_list = sorted(data["personnel_name"].unique())

    # Seçili personeli session_state'te tut
    if "selected_person" not in st.session_state:
        st.session_state.selected_person = personnel_list[0] if personnel_list else None

    current_index = 0
    if st.session_state.selected_person in personnel_list:
        current_index = personnel_list.index(st.session_state.selected_person)

    selected_person = st.selectbox(
        "👤 Personel Seçin",
        options=personnel_list,
        index=current_index,
        key="person_selector"
    )
    st.session_state.selected_person = selected_person

    if not selected_person:
        return

    # Güncel veriden seçili personele ait satırları al
    person_df = data[data["personnel_name"] == selected_person].copy()
    rank = person_df["rank_normalized"].iloc[0] if not person_df.empty else "Bilinmiyor"

    st.markdown(f"**Ünvan:** {rank}")
    st.markdown("---")

    # Belge düzenleme kartları
    for idx, row in person_df.iterrows():
        doc = row["document_name"]
        # Güncel veriyi her seferinde service.processed_data'dan tekrar oku
        updated_row = service.processed_data.loc[idx]
        current_expiry = updated_row.get("expiry_date")
        current_start = updated_row.get("start_date") if "start_date" in updated_row.index else None

        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                st.markdown(f"**{doc}**")
                if current_expiry and pd.notna(current_expiry):
                    st.caption(f"Mevcut Bitiş: {current_expiry.strftime('%d.%m.%Y')}")
                else:
                    st.caption("Bitiş tarihi yok")

            with col2:
                new_start = st.date_input(
                    "📅 Başlangıç",
                    value=current_start if current_start and pd.notna(current_start) else None,
                    key=f"start_{idx}",
                    help="Belgenin yenilendiği tarih"
                )

            auto_expiry = None
            validity_years = 1
            if new_start:
                validity_days = get_default_validity(doc)
                auto_expiry = new_start + timedelta(days=validity_days)
                validity_years = validity_days // 365
                st.caption(f"Otomatik hesaplanan bitiş: {auto_expiry.strftime('%d.%m.%Y')} ({validity_years} yıl)")

            with col3:
                default_expiry = auto_expiry if auto_expiry else (
                    current_expiry if current_expiry and pd.notna(current_expiry) else None
                )
                new_expiry = st.date_input(
                    "📅 Bitiş",
                    value=default_expiry,
                    key=f"expiry_{idx}"
                )

            with col4:
                if st.button("💾 Kaydet", key=f"save_{idx}"):
                    success = service.update_document_dates(
                        personnel_name=selected_person,
                        document_name=doc,
                        start_date=new_start if new_start else None,
                        expiry_date=new_expiry if new_expiry else None,
                    )
                    if success:
                        st.success(f"✅ '{doc}' güncellendi!")
                        st.rerun()  # Sayfayı yenileyerek güncel veriyi göster
                    else:
                        st.error("Güncelleme başarısız oldu.")

            st.markdown("---")

    # Toplu güncelleme
    st.markdown("## 🔁 Tüm belgeleri aynı anda güncelle")
    st.caption("Aynı başlangıç tarihini tüm belgelere uygular, bitişleri otomatik hesaplar.")
    common_start = st.date_input("Ortak başlangıç tarihi", value=None, key="bulk_start")
    if st.button("Tüm belgelere uygula"):
        if not common_start:
            st.warning("Lütfen bir başlangıç tarihi seçin.")
        else:
            for idx, row in person_df.iterrows():
                doc = row["document_name"]
                expiry = common_start + timedelta(days=get_default_validity(doc))
                service.update_document_dates(
                    personnel_name=selected_person,
                    document_name=doc,
                    start_date=common_start,
                    expiry_date=expiry,
                )
            st.success(f"Tüm belgeler {common_start.strftime('%d.%m.%Y')} tarihine göre güncellendi.")
            st.rerun()


if __name__ == "__main__":
    main()
