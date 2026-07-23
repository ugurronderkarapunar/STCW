"""
Configuration constants for the Personnel Document Tracking System.
Includes column mappings, status definitions, color palettes, rank lists,
visual identity, notification thresholds, and document validity periods.
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
KNOWN_RANKS: List[str] = []

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
APP_LOGO_URL: str = "https://img.icons8.com/fluency/96/document.png"
COMPANY_NAME: str = "şehir Hatları A.Ş."

# ─── Notification Thresholds ───
NOTIFICATION_THRESHOLDS: Dict[str, int] = {
    "expired_warning": 10,
    "critical_warning": 20,
    "missing_date_warning": 15
}

# ─── Document Validity Periods ───
DEFAULT_DOCUMENT_VALIDITY_DAYS: int = 365  # 1 yıl

DOCUMENT_VALIDITY_MAP: Dict[str, int] = {
    "sağlık": 730,
    "gemiadamları sağlık": 730,
    "gemi adamı sağlık": 730,
    "stcw": 1825,
    "src": 1825,
    "goc": 1825,
    "yangın": 1825,
    "ilk yardım": 1825,
    "cankurtarma": 1825,
    "güvenlik": 1825,
    "telsiz": 1825,
    "gemi adamı cüzdan": 1825,
    "gemiadamı cüzdan": 1825,
    "pasaport": 3650,
    "vize": 730,
    "ro-ro": 1825,
    "ecdıs": 1825,
    "arpa": 1825,
}
