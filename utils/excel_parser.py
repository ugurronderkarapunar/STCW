"""
Excel/CSV file parser with automatic column detection.
Uses weighted scoring to avoid misclassification (e.g., "Ad" as document name).
Handles large files efficiently with chunked reading.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple, Any
import logging
from pathlib import Path
import io
import re

from utils.config import (
    PERSONNEL_NAME_PATTERNS,
    RANK_TITLE_PATTERNS,
    DOCUMENT_NAME_PATTERNS,
    EXPIRY_DATE_PATTERNS,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
)

logger = logging.getLogger(__name__)


class ColumnMapper:
    """
    Automatically maps DataFrame columns to expected fields
    using improved weighted scoring to avoid misclassification.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.columns: List[str] = list(df.columns)
        self.column_map: Dict[str, Optional[str]] = {
            "personnel_name": None,
            "rank_title": None,
            "document_name": None,
            "expiry_date": None,
        }

    def _normalize(self, text: str) -> str:
        """Normalize column name: lowercase, remove punctuation, collapse spaces."""
        text = str(text).strip().lower()
        # Noktalama işaretlerini temizle (Pzs.tanımı -> pzstanımı gibi)
        text = re.sub(r'[^\w\s]', '', text)
        # Alt tire ve tireyi boşluğa çevir
        text = text.replace('_', ' ').replace('-', ' ')
        # Fazla boşlukları tek boşluğa indir
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _score_column_for_category(self, col: str, patterns: List[str]) -> int:
        """
        Calculate a score for how well a column matches a set of patterns.
        - Exact match (after normalization) gets very high score.
        - Longer pattern match gets higher score.
        """
        col_norm = self._normalize(col)
        best_score = 0
        for pattern in patterns:
            pattern_norm = self._normalize(pattern)
            if col_norm == pattern_norm:
                # Tam eşleşme: çok yüksek puan
                score = 1000 + len(pattern_norm) * 10
            elif pattern_norm in col_norm or col_norm in pattern_norm:
                # Kısmi eşleşme: daha uzun desen daha spesifik
                score = 500 + len(pattern_norm)
            else:
                # Kelime bazında: bütün kelimeler varsa
                pattern_words = set(pattern_norm.split())
                col_words = set(col_norm.split())
                if pattern_words and pattern_words.issubset(col_words):
                    score = 300 + len(pattern_words) * 50
                else:
                    score = 0
            if score > best_score:
                best_score = score
        return best_score

    def map_all(self) -> Dict[str, Optional[str]]:
        """
        Run all column mappings using weighted scoring.
        Each column is assigned to the category with the highest score.
        """
        categories = {
            "personnel_name": PERSONNEL_NAME_PATTERNS,
            "rank_title": RANK_TITLE_PATTERNS,
            "document_name": DOCUMENT_NAME_PATTERNS,
            "expiry_date": EXPIRY_DATE_PATTERNS,
        }

        # For each column, compute score for each category
        col_best_category = {}
        for col in self.columns:
            best_cat = None
            best_score = 0
            for cat, patterns in categories.items():
                score = self._score_column_for_category(col, patterns)
                if score > best_score:
                    best_score = score
                    best_cat = cat
            # Only assign if score is above a threshold
            if best_score > 10:
                col_best_category[col] = best_cat
            else:
                logger.debug(f"Column '{col}' did not match any category significantly (score={best_score})")

        # Now assign each category the best column (if any)
        for cat in categories:
            candidates = [(col, self._score_column_for_category(col, categories[cat]))
                          for col in self.columns if col_best_category.get(col) == cat]
            if candidates:
                # Pick the column with the highest score for this category
                best_col = max(candidates, key=lambda x: x[1])[0]
                self.column_map[cat] = best_col
                logger.info(f"Category '{cat}' mapped to column '{best_col}' (score={max(candidates, key=lambda x: x[1])[1]})")
            else:
                logger.warning(f"No column matched category '{cat}'")

        return self.column_map

    def get_mapped_columns(self) -> List[Optional[str]]:
        """Return list of mapped columns in standard order."""
        return [
            self.column_map["personnel_name"],
            self.column_map["rank_title"],
            self.column_map["document_name"],
            self.column_map["expiry_date"],
        ]


class ExcelParser:
    """
    Handles reading Excel/CSV files with automatic format detection
    and column mapping. Supports files up to 100k+ rows efficiently.
    """

    def __init__(self, file_path: Optional[str] = None, file_bytes: Optional[bytes] = None):
        """
        Initialize parser with either file path or bytes.

        Args:
            file_path: Path to the file.
            file_bytes: File content as bytes (for Streamlit upload).
        """
        self.file_path = file_path
        self.file_bytes = file_bytes
        self.raw_df: Optional[pd.DataFrame] = None
        self.mapped_df: Optional[pd.DataFrame] = None
        self.column_map: Dict[str, Optional[str]] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _validate_file(self) -> bool:
        """Validate file extension and size."""
        if self.file_path:
            path = Path(self.file_path)
            ext = path.suffix.lower().lstrip('.')
            if ext not in ALLOWED_EXTENSIONS:
                self.errors.append(f"Desteklenmeyen dosya formatı: .{ext}. İzin verilenler: {', '.join(ALLOWED_EXTENSIONS)}")
                return False

            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                self.errors.append(f"Dosya boyutu çok büyük: {size_mb:.1f} MB. Maksimum: {MAX_FILE_SIZE_MB} MB")
                return False

        if self.file_bytes:
            size_mb = len(self.file_bytes) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                self.errors.append(f"Dosya boyutu çok büyük: {size_mb:.1f} MB. Maksimum: {MAX_FILE_SIZE_MB} MB")
                return False

        return True

    def read_file(self) -> pd.DataFrame:
        """
        Read the file into a pandas DataFrame.
        Automatically detects format and handles errors gracefully.

        Returns:
            pd.DataFrame: Raw DataFrame from file.
        """
        if not self._validate_file():
            return pd.DataFrame()

        try:
            if self.file_path:
                path = Path(self.file_path)
                ext = path.suffix.lower()

                if ext == '.csv':
                    # Try multiple encodings
                    for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'iso-8859-9', 'cp1254']:
                        try:
                            self.raw_df = pd.read_csv(
                                self.file_path,
                                encoding=encoding,
                                dtype=str,
                                low_memory=False,
                            )
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        self.raw_df = pd.read_csv(
                            self.file_path,
                            encoding='latin1',
                            dtype=str,
                            low_memory=False,
                        )
                elif ext in ['.xlsx', '.xls']:
                    self.raw_df = pd.read_excel(
                        self.file_path,
                        dtype=str,
                        engine='openpyxl',
                    )
                else:
                    self.errors.append(f"Desteklenmeyen dosya uzantısı: {ext}")
                    return pd.DataFrame()

            elif self.file_bytes is not None:
                # Try CSV first
                try:
                    self.raw_df = pd.read_csv(
                        io.BytesIO(self.file_bytes),
                        encoding='utf-8-sig',
                        dtype=str,
                        low_memory=False,
                    )
                except (UnicodeDecodeError, pd.errors.ParserError):
                    # Try Excel
                    self.raw_df = pd.read_excel(
                        io.BytesIO(self.file_bytes),
                        dtype=str,
                        engine='openpyxl',
                    )

            if self.raw_df is None or self.raw_df.empty:
                self.errors.append("Dosya boş veya okunamadı.")
                return pd.DataFrame()

            # Clean column names
            self.raw_df.columns = [str(col).strip() for col in self.raw_df.columns]

            # Remove completely empty rows
            self.raw_df = self.raw_df.dropna(how='all').reset_index(drop=True)

            logger.info(f"File read successfully. Shape: {self.raw_df.shape}")
            return self.raw_df

        except Exception as e:
            self.errors.append(f"Dosya okuma hatası: {str(e)}")
            logger.exception("Error reading file")
            return pd.DataFrame()

    def map_columns(self) -> bool:
        """
        Map DataFrame columns to standard fields.

        Returns:
            bool: True if at least personnel_name and one other field mapped.
        """
        if self.raw_df is None or self.raw_df.empty:
            self.errors.append("Veri bulunamadı. Önce dosyayı okuyun.")
            return False

        mapper = ColumnMapper(self.raw_df)
        self.column_map = mapper.map_all()

        # Check critical columns
        if self.column_map["personnel_name"] is None:
            self.errors.append(
                "Personel adı kolonu tespit edilemedi. Lütfen kolon isimlerinin "
                "'Personel Adı', 'Ad Soyad', 'Employee', 'Crew' vb. olduğundan emin olun."
            )
            return False

        if self.column_map["document_name"] is None:
            self.warnings.append("Belge adı kolonu tespit edilemedi. Belge analizi sınırlı olacak.")

        if self.column_map["expiry_date"] is None:
            self.warnings.append("Bitiş tarihi kolonu tespit edilemedi. Tarih analizi yapılamayacak.")

        return True

    def get_mapped_dataframe(self) -> pd.DataFrame:
        """
        Create a standardized DataFrame with mapped columns.

        Returns:
            pd.DataFrame: Standardized DataFrame with columns:
                personnel_name, rank_title, document_name, expiry_date_raw
        """
        if self.raw_df is None or not self.column_map:
            return pd.DataFrame()

        mapped_data = {}

        # Personnel name
        name_col = self.column_map.get("personnel_name")
        if name_col and name_col in self.raw_df.columns:
            mapped_data["personnel_name"] = self.raw_df[name_col].astype(str).str.strip()
        else:
            mapped_data["personnel_name"] = "Bilinmiyor"

        # Rank/Title
        rank_col = self.column_map.get("rank_title")
        if rank_col and rank_col in self.raw_df.columns:
            mapped_data["rank_title"] = self.raw_df[rank_col].astype(str).str.strip()
        else:
            mapped_data["rank_title"] = "Belirtilmemiş"

        # Document name
        doc_col = self.column_map.get("document_name")
        if doc_col and doc_col in self.raw_df.columns:
            mapped_data["document_name"] = self.raw_df[doc_col].astype(str).str.strip()
        else:
            mapped_data["document_name"] = "Bilinmiyor"

        # Expiry date (keep as string for now)
        date_col = self.column_map.get("expiry_date")
        if date_col and date_col in self.raw_df.columns:
            mapped_data["expiry_date_raw"] = self.raw_df[date_col].astype(str).str.strip()
        else:
            mapped_data["expiry_date_raw"] = None

        self.mapped_df = pd.DataFrame(mapped_data)

        # Replace empty strings and 'nan' with None
        for col in self.mapped_df.columns:
            self.mapped_df[col] = self.mapped_df[col].replace(['', 'nan', 'NaN', 'None', 'NaT'], None)

        return self.mapped_df
