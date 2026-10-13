"""Khảo sát Hugging Face tại SHA khóa và đọc Parquet có giới hạn, không dùng token."""

import hashlib
import io
import json
import logging
import os
import random
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import pyarrow.parquet as pq

LOG = logging.getLogger(__name__)
HUB = "https://huggingface.co"
MAX_GROUP_BYTES = 256 * 1024**2


def fetch_json(url: str) -> Any:
    """Đọc JSON từ API công khai có timeout; không tự sử dụng thông tin xác thực."""
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.load(response)


class RangeFile(io.RawIOBase):
    """File HTTP chỉ đọc và seek được; từ chối Range sai trước khi tải nội dung."""

    def __init__(self, url: str, size: int, budget: int | None = None) -> None:
        super().__init__()
        self.url, self.size, self.position = url, size, 0
        self.budget = budget
        self.transferred = 0
        self.ranges: list[dict[str, Any]] = []

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.position

    def seek(self, offset: int, whence: int = 0) -> int:
        position = offset + (self.position if whence == 1 else self.size if whence == 2 else 0)
        if whence not in (0, 1, 2) or position < 0:
            raise ValueError("Invalid seek")
        self.position = position
        return position

    def read(self, size: int = -1) -> bytes:
        size = max(0, self.size - self.position) if size < 0 else min(
            size, max(0, self.size - self.position)
        )
        if not size:
            return b""
        if self.budget is not None and self.transferred + size > self.budget:
            raise OSError("Sample HTTP byte budget exceeded; reduce scope or use explicit full mode")
        parts = []
        while size:
            length = min(size, 8 * 1024 * 1024)
            start, end = self.position, self.position + length - 1
            separator = "&" if "?" in self.url else "?"
            url = f"{self.url}{separator}audit_range={start}-{end}"
            request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
            with urllib.request.urlopen(request, timeout=60) as response:
                expected = f"bytes {start}-{end}/{self.size}"
                if response.status != 206 or response.headers.get("Content-Range") != expected:
                    raise OSError("Server did not honor exact HTTP Range; refused body download")
                data = response.read(length + 1)
            if len(data) != length:
                raise OSError("Incomplete HTTP Range response")
            self.ranges.append({"start": start, "end": end,
                                "sha256": hashlib.sha256(data).hexdigest()})
            self.position += length
            self.transferred += length
            size -= length
            parts.append(data)
        return b"".join(parts)


def describe_parquet(source: Any) -> dict[str, Any]:
    """Đọc schema và số dòng trong footer Parquet thật, không lấy tổng từ dataset card."""
    parquet = pq.ParquetFile(source)
    return {"schema": {f.name: str(f.type) for f in parquet.schema_arrow},
            "total_records_if_verified": parquet.metadata.num_rows,
            "total_records_source": "parquet_footer_metadata_not_full_scan",
            "row_group_rows": [parquet.metadata.row_group(i).num_rows
                               for i in range(parquet.num_row_groups)],
            "row_group_compressed_bytes": [sum(parquet.metadata.row_group(i).column(j)
                                               .total_compressed_size
                                               for j in range(parquet.metadata.num_columns))
                                           for i in range(parquet.num_row_groups)],
            "row_group_uncompressed_bytes": [sum(parquet.metadata.row_group(i).column(j)
                                                 .total_uncompressed_size
                                                 for j in range(parquet.metadata.num_columns))
                                             for i in range(parquet.num_row_groups)]}


def sample_plan(group_rows: list[int], limit: int, seed: int) -> tuple[int | None, list[int]]:
    """Chọn đều một row group có dữ liệu rồi chọn đều vị trí dòng trong group đó."""
    if limit <= 0:
        raise ValueError("max-records must be positive")
    groups = [i for i, n in enumerate(group_rows) if n]
    if not groups:
        return None, []
    rng = random.Random(seed)
    group = rng.choice(groups)
    return group, sorted(rng.sample(range(group_rows[group]), min(limit, group_rows[group])))


def iter_records(table: dict[str, Any], mode: str, limit: int | None, seed: int,
                 start_group: int = 0) -> Iterator[dict[str, Any]]:
    """Đọc batch 64 dòng; mẫu có giới hạn, chế độ full có thể bắt đầu từ row group chỉ định."""
    if mode not in {"sample", "full"} or (limit is not None and limit <= 0):
        raise ValueError("Invalid audit mode or max-records")
    if start_group < 0 or start_group > len(table["row_group_rows"]):
        raise ValueError("start-group outside Parquet range")
    if mode == "sample" and start_group:
        raise ValueError("start-group only applies to full mode")
    if mode == "sample":
        group, positions = sample_plan(table["row_group_rows"], limit or 1000, seed)
        groups = [group] if group is not None else []
        selected = set(positions)
        table["selected_row_group"] = group
        table["selected_row_positions"] = positions
    else:
        groups = list(range(start_group, len(table["row_group_rows"])))
        selected = None
    sizes = table.get("row_group_compressed_bytes", [0] * len(table["row_group_rows"]))
    if any(sizes[group] > MAX_GROUP_BYTES for group in groups):
        raise OSError("Selected row group exceeds 256 MiB memory guard; source requires re-sharding")
    uncompressed = table.get("row_group_uncompressed_bytes", [0] * len(table["row_group_rows"]))
    if any(uncompressed[group] > MAX_GROUP_BYTES for group in groups):
        raise OSError("Selected uncompressed row group exceeds 256 MiB; source requires re-sharding")
    source = table.get("local_path") or RangeFile(table["url"], table["size_bytes"],
                                                  MAX_GROUP_BYTES if mode == "sample" else None)
    try:
        parquet = pq.ParquetFile(source)
        if any(parquet.metadata.row_group(g).total_byte_size > MAX_GROUP_BYTES for g in groups):
            raise OSError("Actual uncompressed row group exceeds memory guard; source requires re-sharding")
        emitted, position = 0, 0
        for batch in parquet.iter_batches(batch_size=64, row_groups=groups, use_threads=False):
            table["decoded_rows"] = table.get("decoded_rows", 0) + batch.num_rows
            for row in batch.to_pylist():
                if selected is None or position in selected:
                    yield row
                    emitted += 1
                    if limit is not None and emitted >= limit:
                        return
                position += 1
    finally:
        if isinstance(source, RangeFile):
            table["audit_ranges"] = source.ranges
            table["http_bytes_read"] = source.transferred
            source.close()


def _cache_file(dataset: str, revision: str, filename: str) -> Path:
    cache = Path(os.environ.get("HF_HUB_CACHE", Path(os.environ.get(
        "HF_HOME", Path.home() / ".cache/huggingface")) / "hub"))
    return cache / ("datasets--" + dataset.replace("/", "--")) / "snapshots" / revision / filename


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_dataset(dataset_id: str, revision: str | None = None,
                    configs: list[str] | None = None) -> dict[str, Any]:
    """Phát hiện config/split/file tại SHA khóa rồi kiểm tra footer từng file được chọn."""
    suffix = f"/revision/{revision}" if revision else ""
    info = fetch_json(f"{HUB}/api/datasets/{dataset_id}{suffix}")
    revision = info["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Hub returned an invalid revision")
    info = fetch_json(f"{HUB}/api/datasets/{dataset_id}/revision/{revision}")
    files = []
    url = f"{HUB}/api/datasets/{dataset_id}/tree/{revision}?recursive=true&expand=false"
    while url:
        with urllib.request.urlopen(url, timeout=60) as response:
            files.extend(json.load(response))
            link = response.headers.get("Link", "")
        match = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = match[1] if match else None
    by_path = {f["path"]: f for f in files}
    with urllib.request.urlopen(f"{HUB}/datasets/{dataset_id}/raw/{revision}/README.md",
                                timeout=60) as response:
        card = response.read().decode("utf-8")
    card_data = info.get("cardData", {})
    source_urls = sorted(set(re.findall(r"https?://(?:www\.)?vbpl\.vn[^\s)<>]*", card)))
    provenance = {"claimed_license": card_data.get("license"),
                  "license_status": "claimed_source_rights_unresolved",
                  "source_urls_from_card": source_urls, "source_rights": "unverified",
                  "card_url": f"{HUB}/datasets/{dataset_id}/blob/{revision}/README.md",
                  "card_sha256": hashlib.sha256(card.encode()).hexdigest(),
                  "method": "pinned Hub API/card, actual Parquet footer and checksum-verified cache"}
    try:
        with urllib.request.urlopen("https://vbpl.vn", timeout=20) as response:
            provenance["source_portal_access"] = {"http_status": response.status,
                                                  "checked_url": "https://vbpl.vn"}
    except OSError as exc:
        provenance["source_portal_access"] = {"status": "unverified", "error": str(exc)}
    report: dict[str, Any] = {
        "dataset_id": dataset_id, "revision": revision,
        "inspection_timestamp": datetime.now(timezone.utc).isoformat(),
        "license_and_provenance": provenance,
        "repository_files": [{"path": f["path"], "size_bytes": f.get("size")}
                             for f in files if f.get("type") == "file"],
        "card_claimed_statistics": card_data.get("dataset_info"),
        "tables": [], "warnings": ["License is a publisher claim; source rights remain unresolved."],
    }
    discovered_configs = card_data.get("configs")
    if not discovered_configs:
        raise ValueError("No config/file mappings discovered; refusing guessed config names")
    if configs and set(configs) - {c["config_name"] for c in discovered_configs}:
        raise ValueError("Requested config was not discovered")
    report["selected_configs"] = configs
    for config in discovered_configs:
        if configs and config["config_name"] not in configs:
            continue
        for data in config["data_files"]:
            paths = data["path"] if isinstance(data["path"], list) else [data["path"]]
            for filename in paths:
                if filename not in by_path or not filename.endswith(".parquet"):
                    raise ValueError(f"Unsupported or absent discovered data file: {filename}")
                file = by_path[filename]
                table = {"config": config["config_name"], "split": data["split"], "file": filename,
                         "size_bytes": file["size"], "hub_claimed_sha256": file.get("lfs", {}).get("oid"),
                         "url": f"{HUB}/datasets/{dataset_id}/resolve/{revision}/"
                                f"{urllib.parse.quote(filename, safe='/')}"}
                cache = _cache_file(dataset_id, revision, filename)
                if cache.is_file():
                    checksum = _sha256(cache)
                    if checksum != table["hub_claimed_sha256"] or cache.stat().st_size != file["size"]:
                        raise ValueError(f"Cache checksum mismatch: {filename}")
                    table.update(local_path=str(cache), verified_sha256=checksum)
                    table.update(describe_parquet(cache))
                else:
                    with RangeFile(table["url"], file["size"], 2 * 1024**2) as stream:
                        table.update(describe_parquet(stream))
                        table["footer_ranges"] = stream.ranges
                fields = table["schema"]
                table["id_field"] = "id" if "id" in fields else "doc_id" if "doc_id" in fields else None
                table["text_field"] = next((f for f in ("content_html", "content") if f in fields), None)
                table["record_level"] = "relationship" if "other_doc_id" in fields else "document"
                table["redacted_example"] = None
                LOG.info("Inspected %s/%s: %s footer rows", table["config"], table["split"],
                         table["total_records_if_verified"])
                report["tables"].append(table)
    return report
