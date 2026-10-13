# W01 — Verification evidence

Ngày thực hiện: 2026-10-13 (Asia/Saigon). Python 3.11.9, Windows;
PyYAML 6.0.3, PyArrow 26.0.0, pytest 9.1.1, Ruff 0.17.0.

## Những kiểm tra đã chạy

| Kiểm tra | Lệnh từ repository root | Kết quả |
| --- | --- | --- |
| Offline suite | `.\.venv\Scripts\python.exe -m pytest -q` | 43 passed, 0 failed |
| Lint | `.\.venv\Scripts\python.exe -m ruff check .` | All checks passed |
| Actual-file compilation | `.\.venv\Scripts\python.exe -m compileall -q src scripts` | Exit 0 |
| Source inspection | `.\.venv\Scripts\python.exe -X utf8 scripts/inspect_dataset.py` | Exit 0; 5 actual Parquet footers |
| Sample audit | `.\.venv\Scripts\python.exe -X utf8 scripts/audit_corpus.py --inspection results/w01/inspection.json --mode sample --max-records 1000 --seed 42` | Exit 1, intentional partial_failure; 4000 evaluated rows across 4 configs; legacy_content quality unavailable |
| Bounded full CLI | `.\.venv\Scripts\python.exe -X utf8 scripts/audit_corpus.py --inspection results/w01/inspection.json --mode full --configs metadata content --max-records 20 --output results/w01_full_bounded` | Exit 0; 40 evaluated rows, partial coverage |

`results/w01/inspection.json` chứa schema/footer counts, config mappings, pinned card,
cache checksums, range checksums và kết quả truy cập portal. `corpus_audit.json`
chứa số đo thực; `corpus_audit_manifest.json` chứa SHA-256 của JSON, cấu hình,
mã audit và phiên bản môi trường. Chỉ bản manifest nhỏ và aggregate Markdown
được commit; JSON runtime và raw vẫn bị ignore.

Manifest ghi Git HEAD lúc chạy và working-tree dirty cùng hashes mã nguồn:
audit được thực hiện trước delivery commit, không coi baseline HEAD là code audit
đã commit. Hash kiểm tra bytes của artifact thực, không phải card count hay path revision.

## Coverage và gate còn mở

- Schema cả 5 bảng đã xác minh bằng footer; sample values chỉ audit được 4 bảng.
- Full mode có fixture batching và chạy thật có giới hạn; toàn bộ corpus **chưa quét**.
- Legacy content gồm một group khoảng 3,5 GB compressed; reader từ chối trước decode.
  Không đánh đồng unavailable với 0 missing/duplicate/empty.
- Mẫu theo cluster không đại diện theo năm/loại; independent sample joins không xác nhận orphan toàn corpus.
- CC BY 4.0 là publisher claim; quyền nguồn chưa xác minh. Portal trực tiếp trả HTTP 403.
- Không có tokenizer/model token measurement, relevance labels, near-duplicate review hay train-ready corpus.
- GitHub Actions chỉ kiểm tra định nghĩa và chạy các lệnh tương đương local;
  run của delivery commit trên GitHub **chưa có** vì không push.
- Có review độc lập; hai finding quan trọng được sửa và có tests RED→GREEN.
  Chưa có kiểm tra load dài hạn hoặc môi trường Linux thực tế.

Trạng thái W01: **thành công một phần**; công cụ và bằng chứng kỹ thuật đã có,
gate về legacy content, quyền nguồn và nghiệm thu corpus vẫn pending.
