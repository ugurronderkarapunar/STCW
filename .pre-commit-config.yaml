import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from components.styles import get_dark_theme_css, get_light_theme_css

def main():
    st.set_page_config(page_title="Ayarlar", page_icon="⚙️", layout="wide")

    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

    st.markdown("## ⚙️ Ayarlar")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎨 Tema")
        # Streamlit-extras toggle benzeri, normal radio ile değiştirilebilir
        theme_choice = st.radio(
            "Tema Seçimi",
            options=['☀️ Aydınlık', '🌙 Karanlık'],
            index=0 if st.session_state.theme == 'light' else 1,
            horizontal=True,
            key="theme_radio"
        )
        if theme_choice.startswith('☀️'):
            st.session_state.theme = 'light'
        else:
            st.session_state.theme = 'dark'

        if st.session_state.theme == 'dark':
            st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
        else:
            st.markdown(get_light_theme_css(), unsafe_allow_html=True)

    with col2:
        st.subheader("🔔 Bildirim Eşikleri")
        expired_threshold = st.number_input("Süresi geçmiş belge uyarı eşiği", value=10, min_value=1)
        critical_threshold = st.number_input("Kritik belge uyarı eşiği", value=20, min_value=1)
        missing_threshold = st.number_input("Tarihsiz belge uyarı eşiği", value=15, min_value=1)
        if st.button("Eşikleri Kaydet"):
            from utils.config import NOTIFICATION_THRESHOLDS
            NOTIFICATION_THRESHOLDS["expired_warning"] = expired_threshold
            NOTIFICATION_THRESHOLDS["critical_warning"] = critical_threshold
            NOTIFICATION_THRESHOLDS["missing_date_warning"] = missing_threshold
            st.success("Eşikler güncellendi!")

    st.markdown("---")
    st.subheader("📌 Varsayılan Filtreler")
    default_rank = st.multiselect(
        "Varsayılan Ünvanlar",
        options=["Kaptan", "Baş Makinist", "Güverte Lostromosu", "Gemici", "Yağcı"],
        default=st.session_state.get('default_rank_filter', [])
    )
    st.session_state.default_rank_filter = default_rank

    default_status = st.multiselect(
        "Varsayılan Belge Durumu",
        options=["Süresi Geçmiş", "Kritik (0-30 Gün)", "Yaklaşıyor (31-90 Gün)", "Geçerli", "Eklenecek"],
        default=st.session_state.get('default_status_filter', [])
    )
    status_map = {
        "Süresi Geçmiş": "EXPIRED",
        "Kritik (0-30 Gün)": "CRITICAL",
        "Yaklaşıyor (31-90 Gün)": "APPROACHING",
        "Geçerli": "VALID",
        "Eklenecek": "NO_DATE"
    }
    st.session_state.default_status_filter = [status_map[s] for s in default_status]

    if st.button("Varsayılanları Sıfırla"):
        st.session_state.default_rank_filter = []
        st.session_state.default_status_filter = []
        st.rerun()

if __name__ == "__main__":
    main()
