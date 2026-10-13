import json

from app.domains.chat.repositories.json_repository import (
    ensure_json_file_exists,
    load_json_file,
    save_json_file,
)


def test_save_json_file_creates_file_with_data(tmp_path):
    file_path = tmp_path / "data.json"
    data = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
        }
    ]

    save_json_file(file_path=file_path, data=data)

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == data


def test_load_json_file_returns_existing_data(tmp_path):
    file_path = tmp_path / "data.json"
    data = [
        {
            "id": "choco-001",
            "name": "Dark Chocolate",
        }
    ]

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file)

    result = load_json_file(file_path=file_path, default_data=[])

    assert result == data


def test_load_json_file_creates_file_with_default_data_when_missing(tmp_path):
    file_path = tmp_path / "missing.json"
    default_data = [
        {
            "id": "default-product",
            "name": "Default Product",
        }
    ]

    result = load_json_file(file_path=file_path, default_data=default_data)

    assert result == default_data
    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == default_data


def test_ensure_json_file_exists_creates_missing_file(tmp_path):
    file_path = tmp_path / "new-file.json"
    default_data = {
        "message": "hello",
    }

    ensure_json_file_exists(file_path=file_path, default_data=default_data)

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == default_data


def test_ensure_json_file_exists_does_not_overwrite_existing_file(tmp_path):
    file_path = tmp_path / "existing.json"

    existing_data = {
        "message": "existing",
    }

    default_data = {
        "message": "default",
    }

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(existing_data, file)

    ensure_json_file_exists(file_path=file_path, default_data=default_data)

    with open(file_path, "r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == existing_data


def test_save_json_file_supports_unicode_text(tmp_path):
    file_path = tmp_path / "unicode.json"
    data = {
        "name": "Schokolade 🍫",
    }

    save_json_file(file_path=file_path, data=data)

    with open(file_path, "r", encoding="utf-8") as file:
        saved_text = file.read()

    assert "Schokolade 🍫" in saved_text
