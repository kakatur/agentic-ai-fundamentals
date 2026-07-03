import json
from pathlib import Path

import pytest

from safe_file_pipeline import DataLoadError, load_prompt_record, read_csv_rows, read_json, write_json


def test_json_round_trip_uses_context_manager(tmp_path: Path):
    path = tmp_path / "record.json"
    write_json(path, {"prompt": " hello "})
    assert read_json(path) == {"prompt": " hello "}


def test_invalid_json_raises_domain_error(tmp_path: Path):
    path = tmp_path / "broken.json"
    path.write_text("{bad", encoding="utf-8")
    with pytest.raises(DataLoadError, match="invalid json"):
        read_json(path)


def test_load_prompt_record_validates_shape(tmp_path: Path):
    path = tmp_path / "record.json"
    path.write_text(json.dumps({"prompt": "  summarize  "}), encoding="utf-8")
    assert load_prompt_record(path) == {"prompt": "summarize", "source": str(path)}


def test_read_csv_rows_returns_dicts(tmp_path: Path):
    path = tmp_path / "rows.csv"
    path.write_text("id,text\n1,hello\n", encoding="utf-8")
    assert read_csv_rows(path) == [{"id": "1", "text": "hello"}]
