from utils.date_parser import parse_single_date, classify_document
from datetime import date

def test_parse_single_date_formats():
    assert parse_single_date("01.01.2025") == date(2025, 1, 1)
    assert parse_single_date("15/06/2025") == date(2025, 6, 15)
    assert parse_single_date("2025-12-31") == date(2025, 12, 31)
    assert parse_single_date("not a date") is None

def test_classify_document():
    assert classify_document(-5) == "EXPIRED"
    assert classify_document(10) == "CRITICAL"
    assert classify_document(60) == "APPROACHING"
    assert classify_document(100) == "VALID"
    assert classify_document(None) == "NO_DATE"
