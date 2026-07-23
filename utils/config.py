"""
Configuration constants for the Personnel Document Tracking System.
Includes column mappings, status definitions, color palettes, rank lists,
visual identity, and notification thresholds.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field

# ─── Column Name Mappings (Case-Insensitive, Multi-Language) ───
PERSONNEL_NAME_PATTERNS: List[str] = [
    "ad",
    "personel adı", "ad soyad", "personel", "employee",
    "crew", "crew name", "name", "isim", "adı soyadı",
    "çalışan", "çalışan adı", "personnel", "full name",
    "ad soyad", "soyad", "first name", "last name"
]

RANK_TITLE_PATTERNS: List[str] = [
    "pzs.tanımı",
    "ünvan", "görev", "rank", "position", "title",
    "rütbe", "pozisyon", "görevi", "ünvanı", "job title",
    "role", "designation", "meslek", "unvan"
]

DOCUMENT_NAME_PATTERNS: List[str] = [
    "nitelik",
    "belge adı", "certificate", "document", "belge",
    "cert", "doc", "sertifika", "belge türü", "doküman",
    "document type", "certificate name", "certificate type",
    "document name", "doküman adı", "evrak adı", "evrak",
    "belge isim", "sertifika adı"
]

EXPIRY_DATE_PATTERNS: List[str] = [
    "bitiş tarihi", "expiration", "expiry", "son geçerlilik",
    "valid until", "belge tarihi", "expiration date",
    "expiry date", "geçerlilik tarihi", "son tarih",
    "end date", "due date", "validity", "valid till",
    "son geçerlilik tarihi", "bitiş"
]

# ─── Document Status Definitions ───
STATUS_MAP: Dict[str, Tuple[str, str, str]] = {
    "EXPIRED": ("🔴", "Süresi Geçmiş", "#FF4136"),
    "CRITICAL": ("🟠", "Kritik (0-30 Gün)", "#FF851B"),
    "APPROACHING": ("🟡", "Yaklaşıyor (31-90 Gün)", "#FFDC00"),
    "VALID": ("🟢", "Geçerli", "#2ECC40"),
    "NO_DATE": ("⚪", "Eklenecek", "#AAAAAA"),
}

# ─── Known Rank/Title List (for normalization) ───
KNOWN_RANKS: List[str] = []   # Dosyadan otomatik öğrenilir

# ─── Color Palette (Corporate) ───
COLORS: Dict[str, str] = {
    "primary": "#1B3A5C",
    "secondary": "#2C5F8A",
    "accent": "#E8913A",
    "background": "#F5F7FA",
    "card_bg": "#FFFFFF",
    "text": "#2C3E50",
    "text_light": "#7F8C8D",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "info": "#3498DB",
    "expired": "#FF4136",
    "critical": "#FF851B",
    "approaching": "#FFDC00",
    "valid": "#2ECC40",
    "no_date": "#AAAAAA",
}

# ─── Dashboard Constants ───
MAX_ROWS_FOR_TABLE = 5000
ITEMS_PER_PAGE = 25
DATE_FORMATS: List[str] = [
    "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y",
    "%d-%m-%Y", "%Y/%m/%d", "%d %B %Y", "%B %d, %Y",
    "%d.%m.%y", "%d/%m/%y", "%y-%m-%d",
]

# ─── File Settings ───
ALLOWED_EXTENSIONS: List[str] = ["xlsx", "csv", "xls"]
MAX_FILE_SIZE_MB: int = 200

# ─── Visual Identity ───
APP_NAME: str = "Personel Belge Takip Sistemi"
APP_LOGO_URL: str = "https://upload.wikimedia.org/wikipedia/tr/5/50/%C5%9Eehir_Hatlar%C4%B1_logo.png?_=20220616202749"
COMPANY_NAME: str = "İBB ŞEHİR HATLARI."

# ─── Notification Thresholds ───
NOTIFICATION_THRESHOLDS: Dict[str, int] = {
    "expired_warning": 10,      # 10'dan fazla süresi geçmiş belge varsa uyar
    "critical_warning": 20,     # 20'den fazla kritik belge varsa uyar
    "missing_date_warning": 15  # 15'den fazla tarihsiz belge varsa uyar
}
