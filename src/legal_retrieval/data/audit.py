"""Kiểm định corpus chỉ đọc; nội dung gốc không được xuất khỏi bộ tích lũy."""

import hashlib
import logging
import math
import re
import sqlite3
import tempfile
import unicodedata
from collections import Counter
from datetime import date, datetime
from html.parser import HTMLParser
from typing import Any, Iterable

from legal_retrieval.data.schema import normalize_id

DISTRIBUTION_FIELDS = {
    "loai_van_ban", "co_quan_ban_hanh", "linh_vuc", "nganh", "tinh_trang_hieu_luc",
    "nguon_thu_thap", "pham_vi", "legal_type", "legal_sectors", "issuing_authority",
    "effect_status", "relationship",
}
DATE_FIELDS = {
    "ngay_ban_hanh", "ngay_co_hieu_luc", "ngay_het_hieu_luc", "ngay_dang_cong_bao",
    "issuance_date", "effect_date", "effectless_date",
}
STRUCTURES = {
    "chuong": r"\bChương\s+[\dIVX]+", "muc": r"\bMục\s+\d+",
    "dieu": r"\bĐiều\s+\d+", "khoan": r"\bKhoản\s+\d+|(?:^|\n)\s*\d+\.",
    "diem": r"\bĐiểm\s+[a-zđ]|(?:^|\n)\s*[a-zđ]\)", "phu_luc": r"\bPhụ\s+lục\b",
    "legal_reference": r"\b(?:theo|tại|của)\s+(?:Điều|Khoản|Điểm)\s+\w+",
}


def missing(value: Any) -> bool:
    """Null và chuỗi trắng được xem là thiếu; không suy diễn ý nghĩa của số 0 hay nhãn đặc biệt."""
    return value is None or (isinstance(value, str) and not value.strip())


class HTMLDiagnostics(HTMLParser):
    """Đo gần đúng text hiển thị và cấu trúc thẻ, chỉ phục vụ thống kê kiểm định."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.tags: Counter[str] = Counter()
        self.hidden: list[str] = []
        self.table_depth = 0
        self.nested_tables = False
        self.unmatched_closing = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags[tag] += 1
        if tag in {"head", "script", "style"}:
            self.hidden.append(tag)
        if tag in {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "table"}:
            self.parts.append("\n")
        elif tag in {"td", "th"}:
            self.parts.append(" ")
        if tag == "table":
            self.table_depth += 1
            self.nested_tables |= self.table_depth > 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in {"br", "img", "hr", "input", "meta", "link"}:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.hidden:
            self.hidden.remove(tag)
        if tag == "table":
            if self.table_depth:
                self.table_depth -= 1
            else:
                self.unmatched_closing += 1
        if tag in {"p", "div", "tr", "li", "h1", "h2", "h3", "table"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


class AuditStore:
    """Lưu ID, hash và độ dài chính xác vào SQLite tạm để không giữ toàn corpus trong RAM."""

    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix="legal-audit-")
        self.db = sqlite3.connect(f"{self.directory.name}/audit.sqlite")
        self.db.executescript("""
            CREATE TABLE ids(t TEXT, k TEXT, n INTEGER, PRIMARY KEY(t,k));
            CREATE TABLE lengths(t TEXT, metric TEXT, value INTEGER);
            CREATE TABLE texts(t TEXT, digest TEXT, k TEXT);
            CREATE TABLE edges(t TEXT, source TEXT, target TEXT, label TEXT, n INTEGER,
                               PRIMARY KEY(t,source,target,label));
            CREATE INDEX lengths_lookup ON lengths(t,metric,value);
            CREATE INDEX texts_lookup ON texts(t,digest,k);
        """)

    def __enter__(self) -> "AuditStore":
        return self

    def __exit__(self, *args: Any) -> None:
        self.db.close()
        self.directory.cleanup()

    def lengths(self, table: str, metric: str) -> dict[str, Any]:
        """Tính quantile chính xác bằng nội suy tuyến tính tại vị trí q*(n-1) đã sắp xếp."""
        count, low, mean, high = self.db.execute(
            "SELECT count(*),min(value),avg(value),max(value) FROM lengths WHERE t=? AND metric=?",
            (table, metric),
        ).fetchone()

        def quantile(q: float) -> float | None:
            if not count:
                return None
            rank = q * (count - 1)
            left = math.floor(rank)
            values = [v[0] for v in self.db.execute(
                "SELECT value FROM lengths WHERE t=? AND metric=? ORDER BY value LIMIT 2 OFFSET ?",
                (table, metric, left),
            )]
            return values[0] + (values[-1] - values[0]) * (rank - left)

        return {"count": count, "min": low, "median": quantile(.5), "mean": mean,
                "p90": quantile(.9), "p95": quantile(.95), "p99": quantile(.99), "max": high}


def audit_records(
    rows: Iterable[dict[str, Any]], fields: list[str], id_field: str | None,
    text_field: str | None, store: AuditStore | None = None, table_name: str = "records",
) -> dict[str, Any]:
    """Chỉ thống kê những dòng đầu vào; nơi gọi ghi rõ phạm vi mẫu hay toàn bộ."""
    if store is None:
        with AuditStore() as owned:
            return audit_records(rows, fields, id_field, text_field, owned, table_name)
    counts: Counter[str] = Counter()
    nulls: Counter[str] = Counter()
    types: Counter[str] = Counter()
    quality: Counter[str] = Counter()
    structure: Counter[str] = Counter()
    tags: Counter[str] = Counter()
    dates = {field: Counter() for field in fields if field in DATE_FIELDS}
    distributions = {field: Counter() for field in fields if field in DISTRIBUTION_FIELDS}
    count = 0
    profiles = []
    relation_counts: Counter[str] = Counter()
    for row in rows:
        count += 1
        if count % 5000 == 0:
            logging.info("Đã đọc %s dòng trong %s", count, table_name)
        for field in fields:
            nulls[field] += missing(row.get(field))
        value = row.get(id_field) if id_field else None
        key = normalize_id(value)
        if len(profiles) < 3:
            profiles.append({"id_sha256": hashlib.sha256(key.encode()).hexdigest() if key else None,
                             "field_types": {f: type(row.get(f)).__name__ for f in fields},
                             "string_lengths": {f: len(row[f]) for f in fields
                                                if isinstance(row.get(f), str)},
                             "null_or_blank_fields": [f for f in fields if missing(row.get(f))]})
        types[type(value).__name__] += 1
        counts["null_or_blank"] += missing(value)
        counts["unsafe"] += key is None and not missing(value)
        if key is not None:
            store.db.execute("INSERT INTO ids VALUES(?,?,1) ON CONFLICT(t,k) DO UPDATE SET n=n+1",
                             (table_name, key))
        if "other_doc_id" in fields:
            target = normalize_id(row.get("other_doc_id"))
            relation_counts["unsafe_or_missing_target"] += target is None
            label = row.get("relationship")
            if key is not None and target is not None and isinstance(label, str):
                store.db.execute("INSERT INTO edges VALUES(?,?,?,?,1) ON CONFLICT(t,source,target,label) "
                                 "DO UPDATE SET n=n+1", (table_name, key, target, label))
        for field, frequency in distributions.items():
            if not missing(row.get(field)):
                frequency[str(row[field])] += 1
        for field, stats in dates.items():
            raw = row.get(field)
            if missing(raw):
                continue
            parsed = None
            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(str(raw), fmt).date()
                    break
                except ValueError:
                    pass
            stats["invalid"] += parsed is None
            if parsed:
                stats["future"] += parsed > date.today()
                stats[f"year:{parsed.year}"] += 1
        if not text_field:
            continue
        source = row.get(text_field)
        if source is None:
            quality["null"] += 1
            continue
        if not isinstance(source, str):
            quality["invalid_type"] += 1
            continue
        quality["blank_source"] += not source.strip()
        parser = HTMLDiagnostics()
        is_html = text_field == "content_html" or bool(re.search(r"</?[A-Za-z][^>]*>", source))
        if is_html:
            parser.feed(source)
            parser.close()
            text = "".join(parser.parts)
            tags.update(parser.tags)
            quality["html_records"] += 1
            quality["nested_tables"] += parser.nested_tables
            quality["html_structure_flags"] += bool(
                parser.hidden or parser.table_depth or parser.unmatched_closing
            )
            structure["tables"] += parser.tags["table"] > 0
        else:
            text = source
        visible = any(not c.isspace() and unicodedata.category(c)[0] != "C" for c in text)
        quality["empty_visible_text"] += not visible
        quality["short_visible_text_lt_100_chars"] += visible and len(text) < 100
        quality["very_long_visible_text_gt_100000_chars"] += len(text) > 100000
        quality["entities"] += bool(re.search(r"&(?:#\d+|#x[0-9a-f]+|\w+);", source, re.I))
        quality["non_nfc"] += unicodedata.normalize("NFC", source) != source
        quality["replacement_character"] += "�" in source
        quality["suspected_mojibake"] += bool(re.search(
            r"Ã[¡©³º¢ª´¹¼]|Â\xa0|áº|á»", source))
        quality["vietnamese_diacritics"] += bool(re.search(
            r"[ăâđêôơưĂÂĐÊÔƠƯàáèéìíòóùúỳýÀÁÈÉÌÍÒÓÙÚỲÝ\u1ea0-\u1ef9]", text))
        for name, pattern in STRUCTURES.items():
            structure[name] += bool(re.search(pattern, text, re.I))
        for metric, length in (("source_characters", len(source)), ("characters", len(text)),
                               ("whitespace_words", len(text.split()))):
            store.db.execute("INSERT INTO lengths VALUES(?,?,?)", (table_name, metric, length))
        if visible:
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            store.db.execute("INSERT INTO texts VALUES(?,?,?)", (table_name, digest, key))
    store.db.commit()
    distinct, duplicates, extra = store.db.execute(
        "SELECT count(*),coalesce(sum(n>1),0),coalesce(sum(n-1),0) FROM ids WHERE t=?",
        (table_name,),
    ).fetchone()
    if "other_doc_id" in fields:
        relation_counts["duplicate_edge_extra_rows"] = store.db.execute(
            "SELECT coalesce(sum(n-1),0) FROM edges WHERE t=?", (table_name,),
        ).fetchone()[0]
    if text_field:
        defaults = ["null", "invalid_type", "blank_source", "empty_visible_text", "html_records",
                    "nested_tables", "html_structure_flags", "entities", "non_nfc",
                    "replacement_character", "suspected_mojibake", "vietnamese_diacritics",
                    "short_visible_text_lt_100_chars", "very_long_visible_text_gt_100000_chars"]
        for name in defaults:
            quality.setdefault(name, 0)
        quality["same_text_different_id_groups"] = store.db.execute(
            "SELECT count(*) FROM (SELECT digest FROM texts WHERE t=? GROUP BY digest "
            "HAVING count(DISTINCT k)>1)", (table_name,),
        ).fetchone()[0]
    return {
        "scanned_records": count,
        "redacted_sample_profiles": profiles,
        "absent_schema_fields": [f for f in (id_field, text_field) if f and f not in fields],
        "missing_fields": {f: {"count": nulls[f], "rate": nulls[f] / count if count else None}
                           for f in fields},
        "id_integrity": {"null_or_blank": counts["null_or_blank"], "unsafe": counts["unsafe"],
                         "types": dict(types), "mixed_nonnull_types": len(types.keys() - {"NoneType"}) > 1,
                         "distinct_safe_ids": distinct},
        "duplicate_ids": {"groups": duplicates, "extra_rows": extra},
        "relationship_quality": dict(relation_counts) if "other_doc_id" in fields else None,
        "content_quality": dict(quality) if text_field else None,
        "metadata_distributions": {f: dict(v.most_common()) for f, v in distributions.items()},
        "date_quality": {f: {"invalid": v["invalid"], "future": v["future"],
                             "years": {k[5:]: n for k, n in v.items() if k.startswith("year:")}}
                         for f, v in dates.items()},
        "length_statistics": {m: store.lengths(table_name, m)
                              for m in ("characters", "whitespace_words", "source_characters")},
        "token_count": None,
        "legal_structure": {k: structure[k] for k in [*STRUCTURES, "tables"]},
        "html_tags": dict(tags.most_common()),
    }


def join_integrity(store: AuditStore, metadata: str, content: str) -> dict[str, Any]:
    """Join theo ID an toàn đã thực sự đọc trong lần audit này."""
    db = store.db
    shared = db.execute("SELECT count(*) FROM ids a JOIN ids b ON a.k=b.k WHERE a.t=? AND b.t=?",
                        (metadata, content)).fetchone()[0]
    left = db.execute("SELECT count(*) FROM ids WHERE t=?", (metadata,)).fetchone()[0]
    right = db.execute("SELECT count(*) FROM ids WHERE t=?", (content,)).fetchone()[0]
    many_left = db.execute("SELECT count(*) FROM ids WHERE t=? AND n>1", (metadata,)).fetchone()[0]
    many_right = db.execute("SELECT count(*) FROM ids WHERE t=? AND n>1", (content,)).fetchone()[0]
    return {"scope": "observed_records_only", "shared_distinct_ids": shared,
            "metadata_only_distinct_ids": left - shared, "content_only_distinct_ids": right - shared,
            "observed_cardinality": f"{'many' if many_left else 'one'}_to_"
                                    f"{'many' if many_right else 'one'}"}
