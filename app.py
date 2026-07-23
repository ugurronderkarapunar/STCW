"""
Personnel Document Tracking System - Main Entry Point
A professional document tracking and management system for organizations.
"""

import streamlit as st
from components.styles import get_custom_css


def main():
    """
    Main entry point for the Personnel Document Tracking System.
    Streamlit automatically discovers pages in the pages/ directory.
    This file serves as the landing page redirect.
    """
    st.set_page_config(
        page_title="Personel Belge Takip Sistemi",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Hero section
    st.markdown(
        """
        <div style='text-align: center; padding: 60px 20px;'>
            <h1 style='color: #1B3A5C; font-size: 2.5rem; margin-bottom: 10px;'>
                🏢 Personel Belge Takip Sistemi
            </h1>
            <p style='color: #7F8C8D; font-size: 1.2rem; max-width: 700px; margin: 0 auto;'>
                Kurumsal düzeyde personel belge yönetimi, risk analizi ve raporlama platformu.
                Belgelerinizi yükleyin, analiz edin, riskleri görün.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div style='background: #FFFFFF; padding: 24px; border-radius: 12px;
                 box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center; height: 200px;'>
                <div style='font-size: 2.5rem;'>📂</div>
                <h3 style='color: #1B3A5C;'>Akıllı Yükleme</h3>
                <p style='color: #7F8C8D; font-size: 0.9rem;'>
                    Excel/CSV dosyalarını yükleyin. Kolonlar otomatik eşleşsin.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style='background: #FFFFFF; padding: 24px; border-radius: 12px;
                 box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center; height: 200px;'>
                <div style='font-size: 2.5rem;'>📊</div>
                <h3 style='color: #1B3A5C;'>Risk Analizi</h3>
                <p style='color: #7F8C8D; font-size: 0.9rem;'>
                    Belgeleri otomatik sınıflandırın. Riskleri anında görün.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style='background: #FFFFFF; padding: 24px; border-radius: 12px;
                 box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center; height: 200px;'>
                <div style='font-size: 2.5rem;'>📈</div>
                <h3 style='color: #1B3A5C;'>Raporlama</h3>
                <p style='color: #7F8C8D; font-size: 0.9rem;'>
                    Excel, CSV, PDF formatında detaylı raporlar alın.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            """
            <div style='background: #FFFFFF; padding: 24px; border-radius: 12px;
                 box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center; height: 200px;'>
                <div style='font-size: 2.5rem;'>🔍</div>
                <h3 style='color: #1B3A5C;'>Akıllı Filtre</h3>
                <p style='color: #7F8C8D; font-size: 0.9rem;'>
                    Ünvan, belge türü, tarih bazlı gelişmiş filtreleme.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation guidance
    st.markdown(
        """
        <div style='text-align: center; padding: 30px; background: #1B3A5C; border-radius: 12px; color: #FFFFFF;'>
            <h2 style='color: #FFFFFF;'>🚀 Başlamak İçin</h2>
            <p style='font-size: 1.1rem;'>
                Sol menüden <strong>📊 Dashboard</strong> sayfasına giderek veri yükleyebilir
                veya örnek veri ile sistemi test edebilirsiniz.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Footer
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; color: #7F8C8D; font-size: 0.8rem;'>
            🏢 Personel Belge Takip Sistemi v1.0 | Streamlit Cloud Ready |
            GitHub: <a href='https://github.com' style='color: #2C5F8A;'>Proje Deposu</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
