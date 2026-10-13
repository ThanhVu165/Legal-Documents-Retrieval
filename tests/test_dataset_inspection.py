"""File Parquet và phản hồi HTTP giả để CI kiểm thử mà không truy cập Hub."""

import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from legal_retrieval.data.inspection import RangeFile, describe_parquet, iter_records, sample_plan

ROOT = Path(__file__).resolve().parents[1]


def test_sample_reproducible():
    a = sample_plan([10, 20, 30], 5, 42)
    assert a == sample_plan([10, 20, 30], 5, 42)
    assert a != sample_plan([10, 20, 30], 5, 43)
    assert len(a[1]) == 5
    assert len(set(a[1])) == 5
    assert sample_plan([], 5, 42) == (None, [])


def test_parquet_batch_sample_and_full(tmp_path):
    path = tmp_path / "fixture.parquet"
    pq.write_table(pa.table({"id": [str(i) for i in range(30)], "content": ["x"] * 30}),
                   path, row_group_size=10)
    descriptor = describe_parquet(path)
    assert descriptor["total_records_if_verified"] == 30
    assert descriptor["schema"] == {"id": "string", "content": "string"}
    table = {**descriptor, "local_path": str(path)}
    sample = list(iter_records(table, "sample", 5, 42))
    assert len(sample) == 5
    assert sample == list(iter_records(table, "sample", 5, 42))
    assert len(list(iter_records(table, "full", None, 42))) == 30
    assert len(list(iter_records(table, "full", 3, 42, start_group=1))) == 3
    assert list(iter_records(table, "full", 3, 42, start_group=1))[0]["id"] == "10"
    with pytest.raises(ValueError):
        list(iter_records(table, "sample", 0, 42))


def test_range_validation_and_seek(monkeypatch):
    class Response(io.BytesIO):
        status = 206
        headers = {"Content-Range": "bytes 2-4/6"}

    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Response(b"cde"))
    stream = RangeFile("https://example.test/file", 6)
    assert stream.seek(2) == 2
    assert stream.read(3) == b"cde"
    assert len(stream.ranges) == 1
    assert stream.ranges[0]["sha256"]
    Response.status = 200
    with pytest.raises(OSError, match="Range"):
        stream.seek(2)
        stream.read(3)


def test_range_wrong_offset_rejected(monkeypatch):
    class Response(io.BytesIO):
        status = 206
        headers = {"Content-Range": "bytes 2-4/6"}

    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: Response(b"abc"))
    with pytest.raises(OSError, match="Range"):
        RangeFile("https://example.test/file", 6).read(3)
    with pytest.raises(ValueError):
        RangeFile("https://example.test/file", 6).seek(-1)


def test_large_row_group_rejected_before_network(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("Unexpected download"))
    table = {"row_group_rows": [500000], "row_group_compressed_bytes": [3500000000],
             "url": "https://example.test/large", "size_bytes": 3500000000}
    with pytest.raises(OSError, match="row group"):
        list(iter_records(table, "sample", 1000, 42))


def test_compressed_bomb_rejected_before_network(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: pytest.fail("Unexpected download"))
    table = {"row_group_rows": [1], "row_group_compressed_bytes": [1000],
             "row_group_uncompressed_bytes": [300 * 1024**2],
             "url": "https://example.test/bomb", "size_bytes": 1000}
    with pytest.raises(OSError, match="uncompressed"):
        list(iter_records(table, "full", None, 42))


def test_actual_footer_guard_with_stale_descriptor(tmp_path, monkeypatch):
    import legal_retrieval.data.inspection as inspection

    path = tmp_path / "compressible.parquet"
    pq.write_table(pa.table({"id": ["1"], "content": ["x" * 2048]}), path)
    table = {"local_path": str(path), **describe_parquet(path)}
    table["row_group_uncompressed_bytes"] = [0]
    table["row_group_compressed_bytes"] = [0]
    monkeypatch.setattr(inspection, "MAX_GROUP_BYTES", 1024)
    with pytest.raises(OSError, match="uncompressed"):
        list(iter_records(table, "full", None, 42))


def test_multiple_config_files_explicitly_rejected(tmp_path):
    path = tmp_path / "fixture.parquet"
    pq.write_table(pa.table({"id": ["1"]}), path)
    table = {"config": "metadata", "split": "data", "file": "a.parquet",
             "local_path": str(path), **describe_parquet(path)}
    source = tmp_path / "inspection.json"
    source.write_text(json.dumps({"dataset_id": "synthetic/test", "revision": "a" * 40,
                                 "license_and_provenance": {},
                                 "tables": [table, {**table, "file": "b.parquet"}]}), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ROOT / "scripts/audit_corpus.py"),
                             "--inspection", str(source), "--configs", "metadata",
                             "--output", str(tmp_path / "out")],
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1
    assert "Multiple files/splits" in result.stderr


def test_partial_failure_still_reports_schema(tmp_path):
    source = tmp_path / "inspection.json"
    descriptor = {"config": "large", "split": "test", "file": "large.parquet",
                  "schema": {"id": "string", "content": "string"},
                  "total_records_if_verified": 500000, "row_group_rows": [500000],
                  "row_group_compressed_bytes": [3500000000], "size_bytes": 3500000000,
                  "url": "https://example.test/large"}
    source.write_text(json.dumps({"dataset_id": "synthetic/test", "revision": "a" * 40,
                                 "license_and_provenance": {}, "tables": [descriptor]}), encoding="utf-8")
    output = tmp_path / "out"
    result = subprocess.run([sys.executable, str(ROOT / "scripts/audit_corpus.py"),
                             "--inspection", str(source), "--configs", "large",
                             "--output", str(output)],
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1
    report = json.loads((output / "corpus_audit.json").read_text(encoding="utf-8"))
    assert report["tables"][0]["schema"] == descriptor["schema"]
    assert report["tables"][0]["content_quality"] is None
    assert report["tables"][0]["missing_fields"] is None
    assert report["scanned_records"] == 0
    assert report["status"] == "partial_failure"
    assert "500000" in (output / "CORPUS_AUDIT.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("script", ["inspect_dataset.py", "audit_corpus.py"])
def test_cli_help(script):
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--help"],
                            capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert "--output" in result.stdout


def test_offline_cli_report(tmp_path):
    path = tmp_path / "fixture.parquet"
    pq.write_table(pa.table({"id": ["1", "2"], "content": ["Điều 1", ""]}), path)
    inspection = {"dataset_id": "synthetic/unit-test", "revision": "a" * 40,
                  "license_and_provenance": {"status": "synthetic"}, "warnings": [],
                  "tables": [{"config": "fixture", "split": "test", "file": "fixture.parquet",
                              "local_path": str(path), **describe_parquet(path)}]}
    source = tmp_path / "inspection.json"
    source.write_text(json.dumps(inspection), encoding="utf-8")
    output = tmp_path / "output"
    result = subprocess.run([sys.executable, str(ROOT / "scripts/audit_corpus.py"),
                             "--inspection", str(source), "--output", str(output),
                             "--configs", "fixture", "--max-records", "2"], capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    report = json.loads((output / "corpus_audit.json").read_text(encoding="utf-8"))
    assert report["scanned_records"] == 2
    assert report["tables"][0]["content_quality"]["blank_source"] == 1
    assert (output / "corpus_audit_manifest.json").exists()
    assert (output / "CORPUS_AUDIT.md").exists()
    manifest = json.loads((output / "corpus_audit_manifest.json").read_text(encoding="utf-8"))
    assert manifest["report_sha256"] == hashlib.sha256(
        (output / "corpus_audit.json").read_bytes()).hexdigest()
