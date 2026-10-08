import json
from pathlib import Path
from typing import Any


def ensure_json_file_exists(file_path: Path, default_data: Any) -> None:
    if not file_path.exists():
        save_json_file(file_path=file_path, data=default_data)


def load_json_file(file_path: Path, default_data: Any) -> Any:
    ensure_json_file_exists(file_path=file_path, default_data=default_data)

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(file_path: Path, data: Any) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)