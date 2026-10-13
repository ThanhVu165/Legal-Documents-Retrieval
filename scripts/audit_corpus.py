"""Read-only W01 sample/full audit. Full mode is explicit and never part of CI."""

import argparse
import hashlib
import importlib.metadata
import json
import logging
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from legal_retrieval.data.audit import AuditStore, audit_records, join_integrity  # noqa: E402
from legal_retrieval.data.inspection import inspect_dataset, iter_records  # noqa: E402
from legal_retrieval.data.schema import load_config, normalize_id  # noqa: E402


def render_markdown(report: dict[str, Any]) -> str:
    """Generate all numeric tables directly from the actual machine-readable report."""
    lines = ["# W01 — Corpus Audit", "", "## 1. Dataset Overview", "",
             f"Dataset: `{report['dataset_id']}`; revision: `{report['revision']}`.",
             f"Audit UTC: {report['audit_timestamp']}; mode: **{report['mode']}**.", "",
             "## 2. Data Source and Licensing", "",
             json.dumps(report["license_and_provenance"], ensure_ascii=False, indent=2), "",
             "License công bố chưa chứng minh quyền với mọi tài liệu nguồn. Không có raw dump trong báo cáo.",
             "", "## 3. Schema Inspection", ""]
    for table in report["tables"]:
        lines += [f"- `{table['config']}/{table['split']}` ({table['record_level']}): "
                  + ", ".join(f"`{k}: {v}`" for k, v in table["schema"].items())]
    lines += ["", "## 4. Data Volume", "",
              "Footer Parquet là thống kê file, chưa phải full scan nội dung. Số đo chất lượng chỉ thuộc các record đã audit.",
              "", "| Config/split | Footer rows | Audited rows | Coverage | Row group |",
              "| --- | ---: | ---: | --- | ---: |"]
    for t in report["tables"]:
        lines += [f"| {t['config']}/{t['split']} | {t['total_records_if_verified']} | "
                  f"{t['scanned_records']} | {t['coverage']} | {t.get('selected_row_group')} |"]
    lines += ["", "## 5. Metadata/Content Relationships", "",
              "Join chỉ trên ID quan sát được; phía không có trong mẫu khác không phải orphan toàn corpus.",
              "", "```json", json.dumps(report["join_integrity"], ensure_ascii=False, indent=2), "```",
              "", "## 6. Missing and Duplicate Analysis", "",
              "| Config | ID null/blank | Unsafe ID | Duplicate key extra rows | Missing fields (count / audited) |",
              "| --- | ---: | ---: | ---: | --- |"]
    for t in report["tables"]:
        if t["missing_fields"] is None:
            lines += [f"| {t['config']} | unmeasured | unmeasured | unmeasured | audit unavailable |"]
            continue
        missing = "; ".join(f"{k}: {v['count']}/{t['scanned_records']} ({v['rate']:.1%})"
                            for k, v in t["missing_fields"].items() if v["count"] and v["rate"] is not None)
        lines += [f"| {t['config']} | {t['id_integrity']['null_or_blank']} | "
                  f"{t['id_integrity']['unsafe']} | {t['duplicate_ids']['extra_rows']} | {missing or '0 observed'} |"]
    lines += ["", "Relationships ở cấp edge: lặp doc_id là degree, không phải duplicate document/edge.",
              "", "## 7. Text/HTML Quality", "",
              "Diagnostic text bỏ head/script/style chỉ để đo; không lưu processed text. HTML parser khoan dung không xác nhận HTML hợp lệ.",
              "| Config | Null | Blank source | Empty visible | Non-NFC | Same text/different IDs groups | HTML flags |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for t in report["tables"]:
        q = t["content_quality"]
        if q:
            lines += [f"| {t['config']} | {q['null']} | {q['blank_source']} | {q['empty_visible_text']} | "
                      f"{q['non_nfc']} | {q['same_text_different_id_groups']} | {q['html_structure_flags']} |"]
    lines += ["", "Date/metadata distributions (aggregate values; no signer or title excerpts):", "", "```json",
              json.dumps({t["config"]: {"dates": t["date_quality"],
                         "metadata": {k: dict(list(v.items())[:12])
                                      for k, v in t["metadata_distributions"].items()}}
                         for t in report["tables"] if t["metadata_distributions"]},
                         ensure_ascii=False, indent=2), "```",
              "", "Top 12 displayed per metadata field; complete observed frequencies are in JSON.",
              "", "## 8. Length Distribution", "",
              "Characters = diagnostic text length; whitespace words không phải BKAI tokens. Quantile dùng nội suy rank q*(n-1).",
              "", "| Config | Metric | n | min | median | mean | p90 | p95 | p99 | max |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for t in report["tables"]:
        if t["content_quality"]:
            for metric, s in t["length_statistics"].items():
                vals = [str(round(s[k], 2)) if isinstance(s[k], float) else str(s[k])
                        for k in ("count", "min", "median", "mean", "p90", "p95", "p99", "max")]
                lines += [f"| {t['config']} | {metric} | " + " | ".join(vals) + " |"]
    lines += ["", "Token count: **unverified**, tokenizer chưa cài/chạy.",
              "", "## 9. Legal Document Structure", "",
              "Regex heuristic: số record có dấu hiệu, không phải số điều/khoản chính xác.", "", "```json",
              json.dumps({t["config"]: t["legal_structure"] for t in report["tables"]
                          if t["content_quality"]}, ensure_ascii=False, indent=2), "```",
              "", "## 10. Recommended Corpus Selection", "",
              "Có thể nghiên cứu retrieval với metadata + content hiện hành; chưa đủ bằng chứng chất lượng để chốt corpus.",
              "Đề xuất W02: index chunk theo Điều/khoản khi cấu trúc đủ rõ, fallback theo đoạn; trả kết quả và đánh giá ở cấp document.",
              "Chunk giữ source ID, revision, config/split/file, vị trí gốc và document ID; chưa chốt token budget.",
              "", "| Phương án | Lợi ích | Hạn chế / ảnh hưởng retrieval | Quyết định |",
              "| --- | --- | --- | --- |",
              "| Current metadata + content | HTML và metadata filter đã kiểm tra schema | Nội dung rỗng/thiếu cần review; mẫu không xác nhận mọi join | Đề xuất ưu tiên, chưa chọn subset |",
              "| Stratify theo loại + năm | Tránh bias của prefix; metadata hỗ trợ filter | Ngày thiếu/sai và lệch lớp cần strata riêng | Đề xuất sau kiểm tra coverage |",
              "| Filter lĩnh vực | Gọn và có mục đích | Giá trị missing/Chưa phân loại không chứng minh ngoài domain | Chờ đo đầy đủ và nhóm chọn domain |",
              "| Trộn legacy | Tăng coverage lịch sử | ID int, metadata English, plain text; nguy cơ duplicate/leakage | Không trộn tự động |",
              "", "Filter dùng loai_van_ban/co_quan_ban_hanh/ngay_ban_hanh/linh_vuc nếu có giá trị; title + so_ky_hieu dùng hiển thị.",
              "Source reference phải giữ portal ID và snapshot; chưa xác minh URL chi tiết cho từng tài liệu.",
              "", "## 11. Risks and Limitations", ""]
    lines += [f"- {warning}" for warning in report["warnings"]]
    lines += ["- Không có relevance labels/split. Rủi ro fine-tuning chính: nhãn yếu, false negatives, duplicate/leakage và truncate văn bản dài.",
              "- HTML flags, mojibake, date tương lai là dấu hiệu review; không tự động chứng minh record sai.",
              "", "## 12. Next Steps for W02", "",
              "Bảo toàn raw, xử lý NFC trên bản derived, review empty/image-only/HTML tables/encoding/date flags; không loại chỉ dựa độ dài.",
              "Kiểm tra join và duplicate đầy đủ trước labels/splits; tạo nhóm duplicate chống leakage.",
              "Lấy mẫu phân tầng theo năm/loại và review nguồn; kiểm tra tokenizer thật trước quyết định chunk tokens/overlap.",
              "Quyền sử dụng, tiêu chí loại/giữ và corpus selection cần được nhóm nghiệm thu.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Audit real discovered tables or a supplied inspection file, then save evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/corpus.yaml"))
    parser.add_argument("--inspection", type=Path)
    parser.add_argument("--mode", choices=["sample", "full"], default="sample")
    parser.add_argument("--max-records", type=int, help="Per-file limit; sample default 1000")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--start-group", type=int, default=0, help="Full restart group; separate report")
    parser.add_argument("--configs", nargs="+", help="Only discovered config names")
    parser.add_argument("--output", type=Path, default=Path("results/w01"))
    args = parser.parse_args(argv)
    if (args.max_records is not None and args.max_records <= 0) or args.start_group < 0:
        parser.error("max-records must be positive; start-group must be nonnegative")
    if args.mode == "sample" and args.start_group:
        parser.error("start-group only applies to full mode")
    limit = args.max_records if args.max_records is not None else 1000 if args.mode == "sample" else None
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        config = load_config(args.config)
        seed = config.get("seed", 42) if args.seed is None else args.seed
        source = json.loads(args.inspection.read_text(encoding="utf-8")) if args.inspection else (
            inspect_dataset(config["dataset"]["id"], config["dataset"]["revision"]))
        if args.configs and set(args.configs) - {t["config"] for t in source["tables"]}:
            raise ValueError("Requested config was not discovered")
        selected_configs = [t["config"] for t in source["tables"]
                            if not args.configs or t["config"] in args.configs]
        if len(selected_configs) != len(set(selected_configs)):
            raise ValueError("Multiple files/splits per config are not supported by this audit; "
                             "refusing incomplete joins/totals")
        report = {"dataset_id": source["dataset_id"], "revision": source["revision"],
                  "audit_timestamp": datetime.now(timezone.utc).isoformat(), "mode": args.mode,
                  "sampling_method": "one seeded uniform row group per file; uniform positions inside cluster"
                  if args.mode == "sample" else "sequential row-group batches",
                  "sampling_seed": seed, "max_records_per_file": limit, "start_group": args.start_group,
                  "license_and_provenance": source["license_and_provenance"],
                  "tables": [], "warnings": list(source.get("warnings", [])), "join_integrity": {}}
        if args.mode == "sample":
            report["warnings"].append("Cluster sample is not representative by year/type/domain; no population extrapolation.")
        report["warnings"].append("Partial joins compare independently sampled records; observed sample-only IDs are not corpus orphans.")
        report["warnings"].append("HTML visible-text/structure diagnostics are heuristics; no cleaning or processed corpus produced.")
        failed = False
        names = {}
        with AuditStore() as store:
            for table in source["tables"]:
                if args.configs and table["config"] not in args.configs:
                    continue
                name = f"{table['config']}/{table['split']}/{table['file']}"
                logging.info("Auditing %s (%s)", name, args.mode)
                try:
                    id_field = table.get("id_field") or ("id" if "id" in table["schema"] else "doc_id")
                    text_field = table.get("text_field") or next(
                        (f for f in ("content_html", "content") if f in table["schema"]), None)

                    def records() -> Any:
                        for row in iter_records(table, args.mode, limit, seed, args.start_group):
                            if "other_doc_id" in row:
                                key = normalize_id(row["other_doc_id"])
                                if key is not None:
                                    store.db.execute("INSERT INTO ids VALUES(?,?,1) ON CONFLICT(t,k) DO UPDATE SET n=n+1",
                                                     (name + ":targets", key))
                            yield row

                    stats = audit_records(records(), list(table["schema"]), id_field, text_field,
                                          store, name)
                    coverage = "complete" if args.mode == "full" and args.start_group == 0 and (
                        stats["scanned_records"] == table["total_records_if_verified"]) else "partial"
                    public = {k: v for k, v in table.items() if k != "local_path"}
                    public.setdefault("record_level", "relationship" if "other_doc_id" in table["schema"] else "document")
                    report["tables"].append({**public, **stats, "coverage": coverage,
                                             "audit_status": "measured"})
                    names[table["config"]] = name
                    logging.info("Audited %s rows in %s", stats["scanned_records"], name)
                except (OSError, ValueError, KeyError) as exc:
                    failed = True
                    public = {k: v for k, v in table.items() if k != "local_path"}
                    public.setdefault("record_level", "document")
                    report["tables"].append({**public, "audit_status": "unmeasured",
                                             "coverage": "unmeasured", "scanned_records": None,
                                             "missing_fields": None, "id_integrity": None,
                                             "duplicate_ids": None, "content_quality": None,
                                             "metadata_distributions": {}, "date_quality": {},
                                             "length_statistics": None, "legal_structure": None,
                                             "error": str(exc)})
                    report["warnings"].append(f"FAILED {name}: {exc}; statistics unavailable")
                    logging.error("Audit failed for %s: %s", name, exc)
            for left, right in [("metadata", "content"), ("legacy_metadata", "legacy_content"),
                                ("metadata", "legacy_metadata"), ("metadata", "relationships")]:
                if left in names and right in names:
                    report["join_integrity"][f"{left}->{right}"] = join_integrity(store, names[left], names[right])
            if "metadata" in names and "relationships" in names:
                report["join_integrity"]["metadata->relationship_targets"] = join_integrity(
                    store, names["metadata"], names["relationships"] + ":targets")
        report["scanned_records"] = sum(t["scanned_records"] or 0 for t in report["tables"])
        report["total_records_if_verified"] = {t["config"]: t["total_records_if_verified"] for t in report["tables"]}
        report["status"] = "partial_failure" if failed else "audit_executed"
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        git_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        versions = {}
        for package in ("PyYAML", "pyarrow", "pytest", "ruff"):
            try:
                versions[package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                versions[package] = None
        manifest = {k: report[k] for k in ("dataset_id", "revision", "audit_timestamp", "mode",
                                         "sampling_method", "sampling_seed", "scanned_records", "status")}
        manifest.update(git_commit_at_run=commit.stdout.strip() if commit.returncode == 0 else None,
                        git_working_tree_dirty=bool(git_status.stdout.strip()) if git_status.returncode == 0 else None,
                        environment={"python": platform.python_version(), "platform": platform.platform(),
                                     "packages": versions},
                        source_url=f"https://huggingface.co/datasets/{report['dataset_id']}",
                        max_records_per_file=limit, start_group=args.start_group,
                        limitations=report["warnings"],
                        files=[{k: t.get(k) for k in ("config", "split", "file", "size_bytes",
                               "verified_sha256", "hub_claimed_sha256", "footer_ranges", "audit_ranges",
                               "http_bytes_read", "selected_row_group", "scanned_records", "coverage")}
                               for t in report["tables"]])
        root = Path(__file__).resolve().parents[1]
        manifest["audit_code_sha256"] = {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in ("scripts/audit_corpus.py", "scripts/inspect_dataset.py",
                         "src/legal_retrieval/data/audit.py", "src/legal_retrieval/data/schema.py",
                         "src/legal_retrieval/data/inspection.py")}
        args.output.mkdir(parents=True, exist_ok=True)
        report_text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
        manifest["report_sha256"] = hashlib.sha256(report_text.encode("utf-8")).hexdigest()
        manifest["config_sha256"] = hashlib.sha256(args.config.read_bytes()).hexdigest()
        manifest["cli_arguments"] = sys.argv[1:] if argv is None else argv
        (args.output / "corpus_audit.json").write_text(report_text, encoding="utf-8", newline="\n")
        (args.output / "corpus_audit_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        (args.output / "CORPUS_AUDIT.md").write_text(render_markdown(report), encoding="utf-8")
        logging.info("Saved aggregate evidence to %s", args.output)
        return int(failed)
    except (OSError, ValueError, KeyError) as exc:
        logging.error("Audit failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
