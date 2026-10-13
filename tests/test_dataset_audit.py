"""Small synthetic rows test the audit without Internet or source data."""

import copy
import json
import math

import pytest

from legal_retrieval.data.audit import AuditStore, audit_records, join_integrity


def test_missing_duplicate_lengths_and_immutability():
    rows = [{"id": "a", "content": "abcd"}, {"id": "a", "content": " "},
            {"id": None, "content": None}, {"content": "abcdefgh"}]
    original = copy.deepcopy(rows)
    report = audit_records(iter(rows), ["id", "content"], "id", "content")
    assert rows == original
    assert report["scanned_records"] == 4
    assert report["missing_fields"]["id"] == {"count": 2, "rate": 0.5}
    assert report["duplicate_ids"]["extra_rows"] == 1
    assert report["id_integrity"]["null_or_blank"] == 2
    assert report["content_quality"]["null"] == 1
    assert report["content_quality"]["blank_source"] == 1
    assert report["length_statistics"]["characters"] == {
        "count": 3, "min": 1, "median": 4.0, "mean": 13 / 3,
        "p90": 7.2, "p95": 7.6, "p99": 7.92, "max": 8,
    }
    json.dumps(report, allow_nan=False)


def test_empty_and_missing_schema():
    report = audit_records([], ["id"], "id", None)
    assert report["missing_fields"]["id"]["rate"] is None
    assert report["length_statistics"]["characters"]["median"] is None
    assert report["content_quality"] is None
    report = audit_records([{"title": "x"}], ["title"], "id", "body")
    assert set(report["absent_schema_fields"]) == {"id", "body"}


def test_html_unicode_dates_and_identical_text():
    rows = [
        {"id": "1", "body": "<style>hidden</style><p>Điều 1. Thuế &amp; phí</p>",
         "ngay_ban_hanh": "13/03/3024", "loai_van_ban": "Luật"},
        {"id": "2", "body": "<p>Điều 1. Thuế &amp; phí</p>",
         "ngay_ban_hanh": "31/02/2020", "loai_van_ban": "Luật"},
        {"id": "3", "body": "<p>\u200b\xa0</p>", "ngay_ban_hanh": None},
        {"id": "4", "body": "<p>a\u0301 �</p>"},
    ]
    report = audit_records(rows, list(rows[0]), "id", "body")
    quality = report["content_quality"]
    assert quality["empty_visible_text"] == 1
    assert quality["non_nfc"] == 1
    assert quality["replacement_character"] == 1
    assert quality["same_text_different_id_groups"] == 1
    assert report["legal_structure"]["dieu"] == 2
    assert report["date_quality"]["ngay_ban_hanh"]["invalid"] == 1
    assert report["date_quality"]["ngay_ban_hanh"]["future"] == 1
    assert report["metadata_distributions"]["loai_van_ban"]["Luật"] == 2


def test_join_cardinality_and_legacy_id_mapping():
    with AuditStore() as store:
        audit_records([{"id": "1"}, {"id": "2"}, {"id": "2"}, {"id": "001"}],
                      ["id"], "id", None, store, "metadata")
        audit_records([{"id": "2"}, {"id": "3"}], ["id"], "id", None, store, "content")
        report = join_integrity(store, "metadata", "content")
        assert report["shared_distinct_ids"] == 1
        assert report["metadata_only_distinct_ids"] == 2
        assert report["content_only_distinct_ids"] == 1
        assert report["observed_cardinality"] == "many_to_one"
        audit_records([{"id": 1}], ["id"], "id", None, store, "legacy")
        assert join_integrity(store, "metadata", "legacy")["shared_distinct_ids"] == 1


def test_invalid_type_not_counted_as_missing():
    report = audit_records([{"id": 1.0, "text": 42}], ["id", "text"], "id", "text")
    assert report["id_integrity"]["unsafe"] == 1
    assert report["missing_fields"]["text"]["count"] == 0
    assert report["content_quality"]["invalid_type"] == 1


def test_valid_vietnamese_not_mojibake():
    report = audit_records([{"id": "1", "text": "Âm nhạc, MÃ SỐ, QUYẾT ĐỊNH"},
                            {"id": "2", "text": "Tiáº¿ng Viá»‡t"}],
                           ["id", "text"], "id", "text")
    assert report["content_quality"]["suspected_mojibake"] == 1


def test_relationship_edges_not_document_duplicates():
    rows = [{"doc_id": "1", "other_doc_id": "2", "relationship": "cites"},
            {"doc_id": "1", "other_doc_id": "3", "relationship": "cites"},
            {"doc_id": "1", "other_doc_id": "2", "relationship": "cites"}]
    report = audit_records(rows, list(rows[0]), "doc_id", None)
    assert report["duplicate_ids"]["extra_rows"] == 2
    assert report["relationship_quality"]["duplicate_edge_extra_rows"] == 1


def test_invisible_id_rejected():
    from legal_retrieval.data.schema import normalize_id

    assert normalize_id("a\u200bb") is None


@pytest.mark.parametrize("values,median", [([0], 0), ([0, 10], 5), ([1, 2, 9], 2)])
def test_quantiles(values, median):
    report = audit_records([{"id": str(i), "text": "a" * n}
                            for i, n in enumerate(values)], ["id", "text"], "id", "text")
    stats = report["length_statistics"]["characters"]
    assert stats["median"] == median
    assert math.isfinite(stats["mean"])
