from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


class DataLoadError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise DataLoadError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DataLoadError(f"invalid json in {path}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise DataLoadError("expected a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    except FileNotFoundError as exc:
        raise DataLoadError(f"missing file: {path}") from exc


def load_prompt_record(path: Path) -> dict[str, str]:
    data = read_json(path)
    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise DataLoadError("prompt must be a non-empty string")
    return {"prompt": prompt.strip(), "source": str(path)}
