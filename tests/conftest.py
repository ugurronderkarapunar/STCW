import sys
import os
import pandas as pd
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_excel_bytes():
    """Create a minimal Excel file in memory for testing."""
    from io import BytesIO
    output = BytesIO()
    df = pd.DataFrame({
        "Ad": ["Ahmet Yılmaz", "Mehmet Demir"],
        "Pzs.tanımı": ["Kaptan", "Gemici"],
        "Nitelik": ["STCW", "Sağlık"],
        "Bitiş": ["01.01.2025", "15/06/2025"]
    })
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output.read()
