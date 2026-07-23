"""
Configuration constants for the Personnel Document Tracking System.
Includes column mappings, status definitions, color palettes, and rank lists.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field

# ─── Column Name Mappings (Case-Insensitive, Multi-Language) ───
PERSONNEL_NAME_PATTERNS: List[str] = [
    "ad",                    # Özel başlık: "Ad"
    "personel adı", "ad soyad", "personel", "employee",
    "crew", "crew name", "name", "isim", "adı soyadı",
    "çalışan", "çalışan adı", "personnel", "full name",
    "ad soyad", "soyad", "first name", "last name"
]

RANK_TITLE_PATTERNS: List[str] = [
    "pzs.tanımı",            # Özel başlık: "Pzs.tanımı"
    "ünvan", "görev", "rank", "position", "title",
    "rütbe", "pozisyon", "görevi", "ünvanı", "job title",
    "role", "designation", "meslek", "unvan"
]

DOCUMENT_NAME_PATTERNS: List[str] = [
    "nitelik",               # Özel başlık: "Nitelik"
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
@dataclass
class DocumentStatus:
    """Document status with visual properties."""
    EXPIRED: Tuple[str, str, str] = field(default=("🔴", "Süresi Geçmiş", "#FF4136"))
    CRITICAL: Tuple[str, str, str] = field(default=("🟠", "Kritik (0-30 Gün)", "#FF851B"))
    APPROACHING: Tuple[str, str, str] = field(default=("🟡", "Yaklaşıyor (31-90 Gün)", "#FFDC00"))
    VALID: Tuple[str, str, str] = field(default=("🟢", "Geçerli", "#2ECC40"))
    NO_DATE: Tuple[str, str, str] = field(default=("⚪", "Tarih Yok", "#AAAAAA"))


STATUS_MAP: Dict[str, Tuple[str, str, str]] = {
    "EXPIRED": ("🔴", "Süresi Geçmiş", "#FF4136"),
    "CRITICAL": ("🟠", "Kritik (0-30 Gün)", "#FF851B"),
    "APPROACHING": ("🟡", "Yaklaşıyor (31-90 Gün)", "#FFDC00"),
    "VALID": ("🟢", "Geçerli", "#2ECC40"),
    "NO_DATE": ("⚪", "Tarih Yok", "#AAAAAA"),
}

# ─── Known Rank/Title List (for normalization) ───
# Yalnızca sizin verinizde bulunan ünvanlar
KNOWN_RANKS: List[str] = [
    "Kaptan",
    "Baş Makinist",
    "Güverte Lostromosu",
    "Gemici",
    "Yağcı"
]

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
