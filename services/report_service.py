"""
Report generation service for Excel, CSV, and PDF exports.
"""

import pandas as pd
import io
from datetime import date, datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Generates exportable reports from analysis data."""

    @staticmethod
    def generate_excel(
        processed_data: pd.DataFrame,
        personnel_summary: pd.DataFrame,
        rank_summary: pd.DataFrame,
    ) -> bytes:
        """
        Generate an Excel report with multiple sheets.

        Args:
            processed_data: Full processed data.
            personnel_summary: Personnel summary DataFrame.
            rank_summary: Rank summary DataFrame.

        Returns:
            bytes: Excel file content.
        """
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Sheet 1: All Documents
            processed_data.to_excel(writer, sheet_name='Tüm Belgeler', index=False)

            # Sheet 2: Expired Documents
            expired = processed_data[processed_data["status"] == "EXPIRED"]
            expired.to_excel(writer, sheet_name='Süresi Geçmiş', index=False)

            # Sheet 3: Critical (0-30 days)
            critical = processed_data[processed_data["status"] == "CRITICAL"]
            critical.to_excel(writer, sheet_name='Kritik 0-30 Gün', index=False)

            # Sheet 4: Approaching (31-90 days)
            approaching = processed_data[processed_data["status"] == "APPROACHING"]
            approaching.to_excel(writer, sheet_name='Yaklaşıyor 31-90 Gün', index=False)

            # Sheet 5: Personnel Summary
            personnel_summary.to_excel(writer, sheet_name='Personel Özeti', index=False)

            # Sheet 6: Rank Summary
            rank_summary.to_excel(writer, sheet_name='Ünvan Özeti', index=False)

            # Format sheets
            workbook = writer.book
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#1B3A5C',
                'font_color': '#FFFFFF',
                'border': 1,
                'text_wrap': True,
            })

            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for col_num, value in enumerate(processed_data.columns.values if sheet_name == 'Tüm Belgeler' else []):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 18)

        output.seek(0)
        return output.getvalue()

    @staticmethod
    def generate_csv(dataframe: pd.DataFrame) -> str:
        """
        Generate CSV string from DataFrame.

        Args:
            dataframe: Data to export.

        Returns:
            str: CSV content.
        """
        return dataframe.to_csv(index=False, encoding='utf-8-sig')

    @staticmethod
    def generate_summary_text(metrics: Dict[str, Any]) -> str:
        """
        Generate a text summary of key metrics.

        Args:
            metrics: KPI metrics dictionary.

        Returns:
            str: Formatted summary text.
        """
        today = date.today().strftime("%d.%m.%Y")
        summary = f"""
        ═══════════════════════════════════════
           PERSONEL BELGE TAKİP SİSTEMİ
           Rapor Tarihi: {today}
        ═══════════════════════════════════════

        📊 GENEL ÖZET
        ─────────────────────────────────────
        • Toplam Personel Sayısı:    {metrics.get('total_personnel', 0)}
        • Toplam Ünvan Sayısı:       {metrics.get('total_ranks', 0)}
        • Toplam Belge Sayısı:       {metrics.get('total_documents', 0)}

        🔴 RİSK DURUMU
        ─────────────────────────────────────
        • Süresi Geçmiş Belgeler:    {metrics.get('expired', 0)}
        • Kritik (0-30 Gün):         {metrics.get('critical', 0)}
        • Yaklaşıyor (31-90 Gün):    {metrics.get('approaching', 0)}
        • Geçerli Belgeler:          {metrics.get('valid', 0)}
        • Tarih Bilgisi Yok:         {metrics.get('no_date', 0)}
        • Hatalı Tarihler:           {metrics.get('invalid_dates', 0)}
        ═══════════════════════════════════════
        """
        return summary
