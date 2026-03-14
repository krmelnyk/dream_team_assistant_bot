from assistant.infrastructure.json_storage import read_json, write_json


def test_write_and_read_json(tmp_path):
    file_path = tmp_path / "test.json"
    payload = {"name": "Anton", "skills": ["python", "testing"]}

    write_json(file_path, payload)
    loaded = read_json(file_path)

    assert loaded == payload


def test_read_json_returns_default_for_missing_file(tmp_path):
    file_path = tmp_path / "missing.json"

    loaded = read_json(file_path, default=[])

    assert loaded == []