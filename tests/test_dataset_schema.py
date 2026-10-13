"""Dữ liệu giả dùng cho unit test; không dùng làm bằng chứng đo corpus thật."""

import json

import pytest

from legal_retrieval.data.schema import load_config, normalize_id


@pytest.mark.parametrize("value,expected", [(1, "1"), ("001", "001"), ("uuid-a", "uuid-a")])
def test_safe_ids(value, expected):
    assert normalize_id(value) == expected


@pytest.mark.parametrize("value", [None, "", " ", " 1", True, 1.0, {}, []])
def test_unsafe_ids(value):
    assert normalize_id(value) is None


def test_config_validation(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text('dataset: {id: a/b, revision: null}\nseed: 42', encoding="utf-8")
    assert load_config(path)["seed"] == 42
    path.write_text('dataset: {id: a/b, revision: wrong}', encoding="utf-8")
    with pytest.raises(ValueError, match="revision"):
        load_config(path)


def test_config_invalid_shape(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(json.dumps([]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(path)
