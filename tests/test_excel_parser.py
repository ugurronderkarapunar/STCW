from utils.excel_parser import ExcelParser, ColumnMapper
import pandas as pd

def test_column_mapper_detects_columns():
    df = pd.DataFrame(columns=["Ad", "Pzs.tanımı", "Nitelik", "Bitiş Tarihi"])
    mapper = ColumnMapper(df)
    mapping = mapper.map_all()
    assert mapping["personnel_name"] == "Ad"
    assert mapping["rank_title"] == "Pzs.tanımı"
    assert mapping["document_name"] == "Nitelik"
    assert mapping["expiry_date"] == "Bitiş Tarihi"

def test_parser_reads_sample(sample_excel_bytes):
    parser = ExcelParser(file_bytes=sample_excel_bytes)
    df = parser.read_file()
    assert not df.empty
    assert parser.map_columns()
    mapped_df = parser.get_mapped_dataframe()
    assert list(mapped_df.columns) == ["personnel_name", "rank_title", "document_name", "expiry_date_raw"]
    assert mapped_df.iloc[0]["personnel_name"] == "Ahmet Yılmaz"
    assert mapped_df.iloc[0]["rank_title"] == "Kaptan"
