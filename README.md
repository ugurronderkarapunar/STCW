# 🏢 Personel Belge Takip Sistemi

Kurumsal düzeyde personel belge takibi, risk analizi ve raporlama platformu.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 📋 Özellikler

- ✅ **Akıllı Kolon Eşleştirme**: Farklı isimlendirilmiş kolonları otomatik tanır
- ✅ **Çoklu Tarih Formatı**: GG.AA.YYYY, DD/MM/YYYY, YYYY-MM-DD ve daha fazlası
- ✅ **Risk Bazlı Sınıflandırma**: Süresi geçmiş, kritik, yaklaşıyor, geçerli
- ✅ **Personel Kartları**: Her personelin tüm belgelerini tek kartta gösterir
- ✅ **İnteraktif Grafikler**: Plotly ile zengin görselleştirmeler
- ✅ **Gelişmiş Filtreleme**: Ünvan, belge türü, durum, ay, yıl bazlı
- ✅ **Canlı Arama**: Personel adına göre anlık filtreleme
- ✅ **Çoklu Rapor Formatı**: Excel, CSV, TXT indirme desteği
- ✅ **100.000+ Satır Desteği**: Vectorized pandas işlemleri ile yüksek performans
- ✅ **Dark/Light Mode**: Otomatik tema desteği
- ✅ **Mobil Uyumlu**: Responsive tasarım
- ✅ **Hata Yönetimi**: Kullanıcı dostu hata ve uyarı mesajları

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.9 veya üzeri
- pip (Python paket yöneticisi)

### Adımlar

```bash
# 1. Depoyu klonlayın
git clone https://github.com/kullanici/personnel-document-tracker.git
cd personnel-document-tracker

# 2. Sanal ortam oluşturun (önerilir)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Uygulamayı çalıştırın
streamlit run app.py
