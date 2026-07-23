import streamlit as st
from components.styles import get_custom_css, get_dark_theme_css, get_light_theme_css

def main():
    st.set_page_config(page_title="Ayarlar", page_icon="⚙️", layout="wide")
    
    # Tema seçimi session state'te tutulsun
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    st.markdown("## ⚙️ Ayarlar")
    
    # Tema seçimi
    theme_choice = st.radio(
        "Tema Seçimi",
        options=['☀️ Aydınlık', '🌙 Karanlık'],
        index=0 if st.session_state.theme == 'light' else 1,
        horizontal=True
    )
    if theme_choice.startswith('☀️'):
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'
    
    # Seçili temaya göre CSS enjekte et
    if st.session_state.theme == 'dark':
        st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
    else:
        st.markdown(get_light_theme_css(), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Varsayılan filtre ayarları
    st.subheader("Varsayılan Filtreler")
    st.caption("Dashboard ilk yüklendiğinde uygulanacak filtreleri belirleyin.")
    
    # Sadece demo amaçlı birkaç seçenek
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
    # Status'leri anahtarlara çevirelim
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
