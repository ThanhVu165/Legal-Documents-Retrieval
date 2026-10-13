"""Dữ liệu giả nhỏ kiểm tra quét đầy đủ; không dùng làm kết quả corpus thật."""

import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from legal_retrieval.data.inspection import describe_parquet

ROOT = Path(__file__).resolve().parents[1]


def test_default_full_only_current_tables(tmp_path):
    tables = []
    fixtures = {
        "metadata": {"id": ["1", "2", "3"], "title": ["a", "b", "c"]},
        "content": {"id": ["1", "2"], "content_html": ["<p>Điều 1</p>", "<p></p>"]},
        "relationships": {"doc_id": ["1", "2"], "other_doc_id": ["2", "4"],
                          "relationship": ["dẫn chiếu", "dẫn chiếu"]},
    }
    for name, rows in fixtures.items():
        path = tmp_path / f"{name}.parquet"
        pq.write_table(pa.table(rows), path, row_group_size=1)
        tables.append({"config": name, "split": "data", "file": path.name,
                       "local_path": str(path), **describe_parquet(path)})
    tables.append({"config": "legacy_content", "split": "content", "file": "not-read.parquet"})
    source = tmp_path / "inspection.json"
    source.write_text(json.dumps({"dataset_id": "synthetic/test", "revision": "a" * 40,
                                 "license_and_provenance": {}, "tables": tables}), encoding="utf-8")
    output = tmp_path / "out"
    result = subprocess.run([sys.executable, str(ROOT / "scripts/audit_corpus.py"),
                             "--inspection", str(source), "--output", str(output)],
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    report = json.loads((output / "corpus_audit.json").read_text(encoding="utf-8"))
    assert report["mode"] == "full"
    assert report["scanned_records"] == 7
    assert report["audit_completed"] is True
    assert {t["config"] for t in report["tables"]} == set(fixtures)
    assert all(t["coverage"] == "complete" for t in report["tables"])
    join = report["join_integrity"]["metadata->content"]
    assert join["scope"] == "full_tables"
    assert join["shared_distinct_ids"] == 2
    assert join["metadata_only_distinct_ids"] == 1
    assert report["join_integrity"]["metadata->relationship_targets"]["content_only_distinct_ids"] == 1
    assert not any("sample" in warning.lower() for warning in report["warnings"])


def test_inspection_filters_before_reading_legacy(tmp_path, monkeypatch):
    import legal_retrieval.data.inspection as module

    path = tmp_path / "current.parquet"
    pq.write_table(pa.table({"id": ["1"]}), path)
    info = {"sha": "a" * 40, "cardData": {"configs": [
        {"config_name": "metadata", "data_files": [{"split": "data", "path": "current.parquet"}]},
        {"config_name": "legacy_content", "data_files": [{"split": "content", "path": "missing.parquet"}]},
    ]}}
    monkeypatch.setattr(module, "fetch_json", lambda url: info)
    monkeypatch.setattr(module, "_cache_file", lambda *args: path)

    class Response:
        headers = {}
        status = 200

        def __init__(self, url):
            self.url = url

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, *args):
            if "/tree/" in self.url:
                return json.dumps([{"path": "current.parquet", "type": "file", "size": path.stat().st_size,
                                    "lfs": {"oid": module._sha256(path)}}]).encode()
            return b"https://vbpl.vn"

    monkeypatch.setattr("urllib.request.urlopen", lambda url, **kwargs: Response(url))
    report = module.inspect_dataset("synthetic/test", configs=["metadata"])
    assert [t["config"] for t in report["tables"]] == ["metadata"]
