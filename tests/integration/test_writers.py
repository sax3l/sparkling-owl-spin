import pytest
import json
from pathlib import Path
from sqlalchemy import create_engine, text, inspect

from src.scraper.template_runtime import JsonlWriter, CsvWriter, SqlAlchemyWriter

SAMPLE_DATA = [
    {"id": 1, "name": "Test A", "value": 100},
    {"id": 2, "name": "Test B", "value": 200},
]

@pytest.mark.integration
def test_jsonl_writer(tmp_path: Path):
    """Verify that JsonlWriter writes correct JSON lines to a file."""
    file_path = tmp_path / "output.jsonl"
    writer = JsonlWriter(file_path)
    writer.write_batch(SAMPLE_DATA)
    writer.close()

    lines = file_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["name"] == "Test A"
    assert json.loads(lines[1])["value"] == 200

@pytest.mark.integration
def test_csv_writer(tmp_path: Path):
    """Verify that CsvWriter writes a correct CSV file with headers."""
    file_path = tmp_path / "output.csv"
    fieldnames = ["id", "name", "value"]
    writer = CsvWriter(file_path, fieldnames=fieldnames)
    writer.write_batch(SAMPLE_DATA)
    writer.close()

    lines = file_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
    assert lines[0] == "id,name,value"
    assert lines[1] == "1,Test A,100"
    assert lines[2] == "2,Test B,200"

@pytest.mark.integration
def test_sqlalchemy_writer_in_memory():
    """Verify that SqlAlchemyWriter correctly inserts data into a database table."""
    # Use an in-memory SQLite database for this test
    engine = create_engine("sqlite:///:memory:")
    table_name = "test_data"

    # Create a table dynamically for the test
    with engine.begin() as conn:
        conn.execute(text(f"""
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
        """))

    writer = SqlAlchemyWriter(engine, table=table_name)
    writer.write_batch(SAMPLE_DATA)

    # Verify the data was inserted correctly
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name} ORDER BY id")).fetchall()
        assert len(result) == 2
        assert result[0][1] == "Test A" # Access by index
        assert result[1][2] == 200